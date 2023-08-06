import os
from pathlib import Path

import boto3
import botocore


class BaseUtil:
    """Utility with methods to handle files and directories."""

    def __init__(self, base_path=Path.home()):
        """
        When calling methods that manipulate paths, they will be relative to
        `base_path`. You can use absolute paths as well.
        """
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def is_dir(self, *paths):
        """Check if joining the arguments results in a directory name."""
        last_path = str(paths[-1]) if paths else ""
        return last_path.endswith("/") or self.base_path.joinpath(*paths).is_dir()

    def get_abspath(self, *paths, create_dirs=False):
        """Build absolute path joining positional args with `self.base_path`.

        If `create_dirs` then it will create the required directories to ensure
        read/write operations in the resulting path.
        """
        abs_path = self.base_path.joinpath(*paths)
        if create_dirs:
            if self.is_dir(*paths):
                abs_path.mkdir(parents=True, exist_ok=True)
            else:
                abs_path.parent.mkdir(parents=True, exist_ok=True)
        return abs_path


class S3(BaseUtil):
    """S3 wrapper built on top of `boto3`."""

    def __init__(self, bucket_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._s3 = boto3.resource("s3")
        self.bucket = self._s3.Bucket(bucket_name)

        # method aliases.
        self.rm = self.remove
        self.ls = self.list_keys

    # def _get_credentials(self):
    #     return {
    #         "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
    #         "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
    #         "aws_session_token": os.getenv("AWS_SESSION_TOKEN"),
    #     }

    def find_keys(self, s3_prefix="", remove_prefix=False):
        """Generator that yields keys under `s3_prefix`."""
        if s3_prefix and not s3_prefix.endswith("/"):
            s3_prefix += "/"
        for obj in self.bucket.objects.filter(Prefix=s3_prefix):
            s3_key = obj.key
            if remove_prefix:
                s3_key = s3_key[len(s3_prefix) :]
            yield s3_key

    def list_keys(self, s3_prefix="", remove_prefix=False):
        """List keys under `s3_prefix`."""
        return list(self.find_keys(s3_prefix, remove_prefix))

    def _upload_single_file(self, abs_local_path, s3_key):
        if s3_key.endswith("/"):
            # `s3_key` is not a valid key. append filename.
            s3_key += abs_local_path.name
        # self.log(f"Uploading {abs_local_path} to {s3_key}")
        self.bucket.upload_file(
            Filename=abs_local_path.as_posix(),
            Key=s3_key,
        )

    def upload(self, local_path, s3_prefix):
        """Upload files to S3, recursively if `local_path` is a directory."""
        abs_local_path = self.get_abspath(local_path)
        if not abs_local_path.exists():
            raise FileNotFoundError(abs_local_path)

        if abs_local_path.is_file():
            self._upload_single_file(abs_local_path, s3_prefix)
        elif abs_local_path.is_dir():
            # recursively build destination `s3_prefix` from directory structure.
            for subpath in abs_local_path.iterdir():
                self.upload(subpath, os.path.join(s3_prefix, subpath.name))
        else:
            raise ValueError(f"Invalid path: {abs_local_path}")

    def _download_single_file(self, s3_key, abs_local_path, overwrite):
        if abs_local_path.is_dir():
            # append destination filename to path.
            s3_filename = os.path.basename(s3_key)
            abs_local_path = abs_local_path.joinpath(s3_filename)

        if not abs_local_path.exists() or overwrite:
            with open(abs_local_path, "wb") as f:
                # self.log(f"Downloading {s3_key} into {abs_local_path}")
                self.bucket.download_fileobj(
                    Key=s3_key,
                    Fileobj=f,
                )
        else:
            # self.log(f"Skipping download of {s3_key} into {abs_local_path}")
            pass

    def download(self, s3_source, local_path, overwrite=False):
        """Download files from S3, recursively if `s3_source` is a prefix."""
        try:
            # check if `s3_source` is a valid S3 key, and download it.
            self.bucket.Object(s3_source).load()
            abs_local_path = self.get_abspath(local_path, create_dirs=True)
            self._download_single_file(s3_source, abs_local_path, overwrite)

        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                # else, try to download keys under `s3_source`.
                keys = self.list_keys(s3_source, remove_prefix=True)
                if not keys:
                    raise FileNotFoundError(f"Nothing to download from {s3_source}.")

                for s3_key in keys:
                    abs_local_path = self.get_abspath(
                        local_path,
                        s3_key,
                        create_dirs=True,
                    )
                    self._download_single_file(
                        os.path.join(s3_source, s3_key),
                        abs_local_path,
                        overwrite,
                    )
            else:
                raise FileNotFoundError(f"Nothing to download from {s3_source}.")

    def remove(self, *s3_keys):
        self.bucket.delete_objects(Delete={"Objects": [{"Key": k} for k in s3_keys]})
