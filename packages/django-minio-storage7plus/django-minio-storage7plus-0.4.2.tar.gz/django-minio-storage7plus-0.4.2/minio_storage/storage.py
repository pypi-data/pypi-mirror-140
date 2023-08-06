import datetime
import mimetypes
import posixpath
import typing as T
import urllib
from logging import getLogger
from time import mktime
from urllib.parse import urlsplit, urlunsplit

import minio
import minio.error as merr
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage
from django.core.files.utils import validate_file_name
from django.utils import timezone
from django.utils.deconstruct import deconstructible
# from minio.helpers import get_target_url

from minio_storage.errors import minio_error
from minio_storage.files import ReadOnlySpooledTemporaryFile
from minio_storage.policy import Policy

logger = getLogger("minio_storage")



@deconstructible
class MinioStorage(Storage):
    """An implementation of Django's file storage using the minio client.

    The implementation should comply with
    https://docs.djangoproject.com/en/dev/ref/files/storage/.

    """

    file_class = ReadOnlySpooledTemporaryFile

    def __init__(
        self,
        minio_client: minio.Minio,
        bucket_name: str,
        *,
        base_url: T.Optional[str] = None,
        file_class=None,
        auto_create_bucket: bool = False,
        presign_urls: bool = False,
        auto_create_policy: bool = False,
        policy_type: T.Optional[Policy] = None,
        object_metadata: T.Optional[T.Dict[str, str]] = None,
        backup_format: T.Optional[str] = None,
        backup_bucket: T.Optional[str] = None,
        assume_bucket_exists: bool = False,
        file_overwrite: bool = True,
        **kwargs,
    ):
        self.client = minio_client
        self.bucket_name = bucket_name
        self.base_url = base_url

        self.backup_format = backup_format
        self.backup_bucket = backup_bucket
        if bool(self.backup_format) != bool(self.backup_bucket):
            raise ImproperlyConfigured(
                "To enable backups, make sure to set both backup format "
                "and backup format"
            )

        if file_class is not None:
            self.file_class = file_class
        self.auto_create_bucket = auto_create_bucket
        self.auto_create_policy = auto_create_policy
        self.assume_bucket_exists = assume_bucket_exists
        self.policy_type = policy_type
        self.presign_urls = presign_urls
        self.object_metadata = object_metadata
        self.file_overwrite = file_overwrite

        self._init_check()

        # A base_url_client is only necessary when using presign_urls
        if self.presign_urls and self.base_url:
            # Do this after _init_check, so client's bucket region cache will
            # already be populated
            self.base_url_client = self._create_base_url_client(
                self.client, self.bucket_name, self.base_url
            )

        super().__init__()

    def _init_check(self):
        if not self.assume_bucket_exists:
            if self.auto_create_bucket and not self.client.bucket_exists(
                self.bucket_name
            ):
                self.client.make_bucket(self.bucket_name)
                if self.auto_create_policy:
                    policy_type = self.policy_type
                    if policy_type is None:
                        policy_type = Policy.get
                    self.client.set_bucket_policy(
                        self.bucket_name, policy_type.bucket(self.bucket_name)
                    )

            elif not self.client.bucket_exists(self.bucket_name):
                raise OSError(f"The bucket {self.bucket_name} does not exist")

    @staticmethod
    def _create_base_url_client(client: minio.Minio, bucket_name: str, base_url: str):
        """
        Clone a Minio client, using a different endpoint from `base_url`.
        """
        base_url_parts = urlsplit(base_url)

        # Clone from the normal client, but with base_url as the endpoint
        base_url_client = minio.Minio(
            base_url_parts.netloc,
            access_key=client._access_key,
            secret_key=client._secret_key,
            session_token=client._session_token,
            secure=base_url_parts.scheme == "https",
            # The bucket region may be auto-detected by client (via an HTTP
            # request), so don't just use client._region
            region="",
            http_client=client._http,
        )
        if hasattr(client, "_credentials"):
            # Client credentials do not exist prior to minio-py 5.0.7, but
            # they should be reused if possible
            base_url_client._credentials = client._credentials

        return base_url_client

    def _sanitize_path(self, name):
        v = posixpath.normpath(name).replace("\\", "/")
        if v == ".":
            v = ""
        if name.endswith("/") and not v.endswith("/"):
            v += "/"
        return v


    def _clean_name(self, name):
        """
        Cleans the name so that Windows style paths work
        """
        # Normalize Windows style paths
        clean_name = posixpath.normpath(name).replace('\\', '/')

        # os.path.normpath() can strip trailing slashes so we implement
        # a workaround here.
        if name.endswith('/') and not clean_name.endswith('/'):
            # Add a trailing slash as it was stripped.
            clean_name += '/'
        return clean_name

    def _normalize_name(self, name):
        """
        Normalizes the name so that paths like /path/to/ignored/../something.txt
        work. We check to make sure that the path pointed to is not outside
        the directory specified by the LOCATION setting.
        """
        try:
            return safe_join("/", name)
        except ValueError:
            raise SuspiciousOperation("Attempted access to '%s' denied." % name)


    def _examine_file(self, name, content):
        """Examines a file and produces information necessary for upload.

        Returns a tuple of the form (content_size, content_type,
        sanitized_name)

        """
        content_size = content.size
        content_type = mimetypes.guess_type(name, strict=False)
        content_type = content_type[0] or "application/octet-stream"
        sane_name = self._sanitize_path(name)
        return (content_size, content_type, sane_name)

    def _open(self, name, mode="rb"):
        name = self._normalize_name(self._clean_name(name))
        try:
            f = self.file_class(name, mode, self)
        except merr.MinioError as e:
            raise minio_error("File {} could not be saved: {}".format(name, str(e)), e)
        return f

    def _save(self, name: str, content: bytes) -> str:
        try:
            
            if hasattr(content, "seek") and callable(content.seek):
                content.seek(0)
            content_size, content_type, sane_name = self._examine_file(name, content)

            cleaned_name = self._clean_name(name)
            name = self._normalize_name(cleaned_name)

            self.client.put_object(
                self.bucket_name,
                name,
                content,
                content_size,
                content_type,
                metadata=self.object_metadata,
            )
            
            return name
        except merr.InvalidResponseError as error:
            raise minio_error(f"File {name} could not be saved", error)


    def delete(self, name: str) -> None:
        name = self._normalize_name(self._clean_name(name))
        try:
            self.client.remove_object(self.bucket_name, name)
        except merr.InvalidResponseError as error:
            raise minio_error(f"Could not remove file {name}", error)


    def exists(self, name: str) -> bool:
        name = self._normalize_name(self._clean_name(name))
        try:
            exists = self.client.stat_object(self.bucket_name, name)
            if exists:
                return True
        except merr.InvalidResponseError as error:
            if error.code == "NoSuchKey":
                return False
        except Exception as error:
            logger.error(error)
        return False


    def listdir(self, path: str) -> T.Tuple[T.List, T.List]:
        #  [None, "", "."] is supported to mean the configured root among various
        #  implementations of Storage implementations so we copy that behaviour even if
        #  maybe None should raise an exception instead.
        #
        #  If the path prefix does not match anything full prefix that does exist this
        #  function will just return empty results, this is different from
        #  FileSystemStorage where an invalid directory would raise an OSError.

        if path in [None, "", ".", "/"]:
            path = ""
        else:
            if not path.endswith("/"):
                path += "/"

        dirs: T.List[str] = []
        files: T.List[str] = []
        try:
            objects = self.client.list_objects_v2(self.bucket_name, prefix=path)
            for o in objects:
                p = posixpath.relpath(o.object_name, path)
                if o.is_dir:
                    dirs.append(p)
                else:
                    files.append(p)
            return dirs, files
        except merr.NoSuchBucket:
            raise
        except merr.InvalidResponseError as error:
            raise minio_error(f"Could not list directory {path}", error)

    def size(self, name: str) -> int:
        try:
            info = self.client.stat_object(self.bucket_name, name)
            return info.size
        except merr.InvalidResponseError as error:
            raise minio_error(f"Could not access file size for {name}", error)

    def _presigned_url(
        self, name: str, max_age: T.Optional[datetime.timedelta] = None
    ) -> str:
        kwargs = {}
        if max_age is not None:
            kwargs["expires"] = max_age

        client = self.client if self.base_url is None else self.base_url_client
        url = client.presigned_get_object(self.bucket_name, name, **kwargs)

        if self.base_url is not None:
            url_parts = urlsplit(url)
            base_url_parts = urlsplit(self.base_url)

            # It's assumed that self.base_url will contain bucket information,
            # which could be different, so remove the bucket_name component (with 1
            # extra character for the leading "/") from the generated URL
            url_key_path = url_parts.path[len(self.bucket_name) + 1 :]

            # Prefix the URL with any path content from base_url
            new_url_path = base_url_parts.path + url_key_path

            # Reconstruct the URL with an updated path
            url = urlunsplit(
                (
                    url_parts.scheme,
                    url_parts.netloc,
                    new_url_path,
                    url_parts.query,
                    url_parts.fragment,
                )
            )
        return url

    def url(
        self, name: str, *args, max_age: T.Optional[datetime.timedelta] = None
    ) -> str:
        if self.presign_urls:
            url = self._presigned_url(name, max_age=max_age)
        else:
            if self.base_url is not None:

                def strip_beg(path):
                    while path.startswith("/"):
                        path = path[1:]
                    return path

                def strip_end(path):
                    while path.endswith("/"):
                        path = path[:-1]
                    return path

                url = "{}/{}".format(
                    strip_end(self.base_url), urllib.parse.quote(strip_beg(name))
                )
            else:
                scheme = "http://"
                if settings.MINIO_STORAGE_USE_HTTPS:
                   scheme = "https://"
                url = scheme + settings.MINIO_STORAGE_ENDPOINT + "/" + settings.MINIO_STORAGE_MEDIA_BUCKET_NAME + "/" + name
        return url

    def accessed_time(self, name: str) -> datetime.datetime:
        """
        Not available via the S3 API
        """
        return self.modified_time(name)

    def created_time(self, name: str) -> datetime.datetime:
        """
        Not available via the S3 API
        """
        return self.modified_time(name)

    def modified_time(self, name: str) -> datetime.datetime:
        try:
            info = self.client.stat_object(self.bucket_name, name)
            return datetime.datetime.fromtimestamp(mktime(info.last_modified))
        except merr.InvalidResponseError as error:
            raise minio_error(
                f"Could not access modification time for file {name}", error
            )

    def get_available_name(self, name, max_length=None):
        """Overwrite existing file with the same name."""
        name = self._clean_name(name)
        # if MINIO_STORAGE_OVERWRITE == False hash filenames, to avoid errors on overwriting
        if self.exists(name) and self.file_overwrite:
            return get_available_overwrite_name(name, max_length)
        return super().get_available_name(name, max_length)

_NoValue = object()


def get_setting(name, default=_NoValue):
    result = getattr(settings, name, default)
    if result is _NoValue:
        raise ImproperlyConfigured
    else:
        return result


def create_minio_client_from_settings(*, minio_kwargs=dict()):
    endpoint = get_setting("MINIO_STORAGE_ENDPOINT")
    access_key = get_setting("MINIO_STORAGE_ACCESS_KEY")
    secret_key = get_setting("MINIO_STORAGE_SECRET_KEY")
    secure = get_setting("MINIO_STORAGE_USE_HTTPS", True)
    # Making this client deconstructible allows it to be passed directly as
    # an argument to MinioStorage, since Django needs to be able to
    # deconstruct all Storage constructor arguments for Storages referenced in
    # migrations (e.g. when using a custom storage on a FileField).
    client = deconstructible(minio.Minio)(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
        **minio_kwargs,
    )
    return client

def get_available_overwrite_name(name, max_length):
    if max_length is None or len(name) <= max_length:
        return name

    # Adapted from Django
    dir_name, file_name = os.path.split(name)
    file_root, file_ext = os.path.splitext(file_name)
    truncation = len(name) - max_length

    file_root = file_root[:-truncation]
    if not file_root:
        raise SuspiciousFileOperation(
            'Storage tried to truncate away entire filename "%s". '
            'Please make sure that the corresponding file field '
            'allows sufficient "max_length".' % name
        )
    return os.path.join(dir_name, "{}{}".format(file_root, file_ext))

def safe_join(base, *paths):
    """
    A version of django.utils._os.safe_join for S3 paths.
    Joins one or more path components to the base path component
    intelligently. Returns a normalized version of the final path.
    The final path must be located inside of the base path component
    (otherwise a ValueError is raised).
    Paths outside the base path indicate a possible security
    sensitive operation.
    """
    base_path = base
    base_path = base_path.rstrip('/')
    paths = [p for p in paths]

    final_path = base_path + '/'
    for path in paths:
        _final_path = posixpath.normpath(posixpath.join(final_path, path))
        # posixpath.normpath() strips the trailing /. Add it back.
        if path.endswith('/') or _final_path + '/' == final_path:
            _final_path += '/'
        final_path = _final_path
    if final_path == base_path:
        final_path += '/'

    # Ensure final_path starts with base_path and that the next character after
    # the base path is /.
    base_path_len = len(base_path)
    if (not final_path.startswith(base_path) or final_path[base_path_len] != '/'):
        raise ValueError('the joined path is located outside of the base path'
                         ' component')

    return final_path.lstrip('/')

def clean_name(name):
    """
    Cleans the name so that Windows style paths work
    """
    # Normalize Windows style paths
    clean_name = posixpath.normpath(name).replace('\\', '/')

    # os.path.normpath() can strip trailing slashes so we implement
    # a workaround here.
    if name.endswith('/') and not clean_name.endswith('/'):
        # Add a trailing slash as it was stripped.
        clean_name = clean_name + '/'

    # Given an empty string, os.path.normpath() will return ., which we don't want
    if clean_name == '.':
        clean_name = ''

    return clean_name


@deconstructible
class MinioMediaStorage(MinioStorage):
    def __init__(self):
        client = create_minio_client_from_settings()
        bucket_name = get_setting("MINIO_STORAGE_MEDIA_BUCKET_NAME")
        base_url = get_setting("MINIO_STORAGE_MEDIA_URL", None)
        auto_create_bucket = get_setting(
            "MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET", False
        )
        auto_create_policy = get_setting(
            "MINIO_STORAGE_AUTO_CREATE_MEDIA_POLICY", "GET_ONLY"
        )

        policy_type = Policy.get
        if isinstance(auto_create_policy, str):
            policy_type = Policy(auto_create_policy)
            auto_create_policy = True

        presign_urls = get_setting("MINIO_STORAGE_MEDIA_USE_PRESIGNED", False)
        backup_format = get_setting("MINIO_STORAGE_MEDIA_BACKUP_FORMAT", False)
        backup_bucket = get_setting("MINIO_STORAGE_MEDIA_BACKUP_BUCKET", False)
        file_overwrite = get_setting("MINIO_STORAGE_OVERWRITE", True)

        assume_bucket_exists = get_setting(
            "MINIO_STORAGE_ASSUME_MEDIA_BUCKET_EXISTS", False
        )

        object_metadata = get_setting("MINIO_STORAGE_MEDIA_OBJECT_METADATA", None)

        super().__init__(
            client,
            bucket_name,
            auto_create_bucket=auto_create_bucket,
            auto_create_policy=auto_create_policy,
            policy_type=policy_type,
            base_url=base_url,
            presign_urls=presign_urls,
            backup_format=backup_format,
            backup_bucket=backup_bucket,
            assume_bucket_exists=assume_bucket_exists,
            object_metadata=object_metadata,
            file_overwrite=file_overwrite
        )


@deconstructible
class MinioStaticStorage(MinioStorage):
    def __init__(self):
        client = create_minio_client_from_settings()
        base_url = get_setting("MINIO_STORAGE_STATIC_URL", None)
        bucket_name = get_setting("MINIO_STORAGE_STATIC_BUCKET_NAME")
        auto_create_bucket = get_setting(
            "MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET", False
        )
        auto_create_policy = get_setting(
            "MINIO_STORAGE_AUTO_CREATE_STATIC_POLICY", "GET_ONLY"
        )

        policy_type = Policy.get
        if isinstance(auto_create_policy, str):
            policy_type = Policy(auto_create_policy)
            auto_create_policy = True

        presign_urls = get_setting("MINIO_STORAGE_STATIC_USE_PRESIGNED", False)

        assume_bucket_exists = get_setting(
            "MINIO_STORAGE_ASSUME_STATIC_BUCKET_EXISTS", False
        )

        object_metadata = get_setting("MINIO_STORAGE_STATIC_OBJECT_METADATA", None)

        super().__init__(
            client,
            bucket_name,
            auto_create_bucket=auto_create_bucket,
            auto_create_policy=auto_create_policy,
            policy_type=policy_type,
            base_url=base_url,
            presign_urls=presign_urls,
            assume_bucket_exists=assume_bucket_exists,
            object_metadata=object_metadata,
        )
