import os
import io
from typing import Optional, Dict, Any, Literal, get_args
import logging
from abc import ABC

import pandas as pd
import boto3
from botocore.exceptions import ClientError
from mypy_boto3_s3.client import S3Client
import tqdm

from .exceptions import S3ObjectNotFound, CredentialsExpired
from ..util.local import make_dir_if_not_exists, infer_file_type
from ..util.progress import update_progress_bar


logger = logging.getLogger(__name__)

S3FileTypes = Literal["csv", "parquet"]


class S3Base(ABC):
    """
    A base object that allows to download/upload a single object from/to s3
    """

    bucket: Optional[str] = None
    region_name: Optional[str] = None
    s3_key: Optional[str] = None
    s3: Optional[S3Client] = None

    def _create_s3_client(self) -> S3Client:
        return boto3.client("s3", region_name=self.region_name)

    def file_download(self, filepath: str) -> None:
        """Download an object from s3 reporting on progress

        Parameters
        ----------
        filepath : str
            local filepath to save file as

        Returns
        -------
        None

        Raises
        -------
        S3ObjectNotFound
            if s3 key was not found
        CredentialsExpired
            if AWS credentials need to be refreshed
        """
        logger.info(f"Downloading file {self.s3_key}")
        # create local dir if not existing
        make_dir_if_not_exists(filepath=filepath)

        try:
            # grab object"s file size in bytes
            file_object = self.s3.head_object(Bucket=self.bucket, Key=self.s3_key)
            file_size: int = file_object["ContentLength"]

            # ue a tqdm progress bar to report percentage of bytes downloaded
            with tqdm.tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                desc=f"Downloading: {self.s3_key}",
            ) as t:
                self.s3.download_file(
                    Bucket=self.bucket,
                    Key=self.s3_key,
                    Filename=filepath,
                    Callback=update_progress_bar(t),
                )
            logger.debug(f"File {self.s3_key} downloaded!\n")

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise S3ObjectNotFound(f"The object {self.s3_key} does not exist")
            elif e.response["Error"]["Code"] == "400":
                aws_profile = os.getenv("AWS_PROFILE")
                raise CredentialsExpired(f"{aws_profile} credentials expired")
            else:
                raise

    def s3_key_exists(self) -> bool:
        """see if file exists on s3 by explicitly attempting to retrieve the object"s
        metadata on s3"""
        try:
            self.s3.head_object(Bucket=self.bucket, Key=self.s3_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise

    def s3_file_upload(self, filepath: str) -> None:
        """Get local file object"s size and upload to s3 bucket reporting on progress.

        Parameters
        ----------
        filepath : str
            local filepath of file to upload to s3

        Returns
        -------
        None

        Raises
        -------
        CredentialsExpired
            if AWS credentials need to be refreshed
        """
        logger.info(f"Uploading file {filepath}...")
        try:
            # grab local file"s size in bytes
            file_size: int = os.stat(filepath).st_size

            # ue a tqdm progress bar to report percentage of bytes uploaded
            with tqdm.tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                desc=f"Uploading: {self.s3_key}",
            ) as t:
                self.s3.upload_file(
                    Filename=filepath,
                    Bucket=self.bucket,
                    Key=self.s3_key,
                    Callback=update_progress_bar(t),
                    ExtraArgs={"ACL": "bucket-owner-full-control"},
                )
            logger.debug(f"File {filepath} uploaded!\n")

        except ClientError as e:
            if e.response["Error"]["Code"] == "400":
                aws_profile = os.getenv("AWS_PROFILE")
                raise CredentialsExpired(f"{aws_profile} credentials expired")
            else:
                raise

    def df_to_s3_object(
        self, df: pd.DataFrame, save_args: Optional[Dict[str, Any]] = None
    ) -> None:
        """Upload an in-memory DataFrame into an s3 csv/parquet file.

        Parameters
        ----------
         df : DataFrame
            Pandas DataFrame to upload to s3
        save_args : dict
            Any arguments that can be passed to the corresponding save method if used
        Returns
        -------
        None

        Raises
        -------
        TypeError
            if a not supported file_type was passed
        CredentialsExpired
            if AWS credentials need to be refreshed
        """
        # infer file type from suffix
        file_type = infer_file_type(self.s3_key)
        if file_type not in get_args(S3FileTypes):
            raise TypeError(f"Allowed file_type options: {get_args(S3FileTypes)}")
        logger.info(f"Saving DataFrame to s3 as {self.s3_key}...")

        # upload as a single file
        mio = io.StringIO()
        _save_args = {}
        if save_args:
            _save_args.update(save_args)
        if file_type == "csv":
            # noinspection PyTypeChecker
            df.to_csv(mio, index=False, **_save_args)
        elif file_type == "parquet":
            mio = io.BytesIO()
            # noinspection PyTypeChecker
            df.to_parquet(mio, index=False, **_save_args)
        try:
            self.s3.put_object(Bucket=self.bucket, Key=self.s3_key, Body=mio.getvalue())
        except ClientError as e:
            if e.response["Error"]["Code"] == "400":
                aws_profile = os.getenv("AWS_PROFILE")
                raise CredentialsExpired(f"{aws_profile} credentials expired")
            else:
                raise
