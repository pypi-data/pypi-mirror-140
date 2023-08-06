from typing import Optional, Dict, Any, Union
import logging

import pandas as pd

from ._base import S3Base
from ..util.local import local_file_exists, file_to_df


logger = logging.getLogger(__name__)


class S3File(S3Base):
    """
    A class that allows downloading/uploading files from/to s3

    Parameters
    ----------
    bucket : str
        name of the s3 bucket where the file is to be downloaded from/uploaded to
    region_name : str
        AWS region of s3 bucket
    s3_key : str
        name of file in s3 bucket that will be downloaded/ uploaded a
    """

    def __init__(self, bucket: str, region_name: str, s3_key: str):
        """
        Parameters
        ----------
        bucket : str
            name of the s3 bucket where the file is to be downloaded from/uploaded to
        region_name : str
            AWS region of s3 bucket
        s3_key : str
            name of file in s3 bucket that will be downloaded/ uploaded as
        """
        self.bucket = bucket
        self.region_name = region_name
        self.s3_key = s3_key

        self.s3 = self._create_s3_client()

    def get(
        self,
        filepath: str,
        overwrite: bool = False,
        read_to_df: bool = False,
        load_args: Optional[Dict[str, Any]] = None,
    ) -> Union[None, pd.DataFrame]:
        """
        Download file from s3 and save locally as filepath with option to read into a
        DataFrame

        Parameters
        ----------
        filepath : str
            local filepath of file to upload to s3
        overwrite : bool default = False
            If set to True, method will overwrite the s3 object
        read_to_df: bool, default = True
            if True then downloaded csv will be loaded into a DataFrame
        load_args : dict
            Any arguments that can be passed to the corresponding read method if used

        Returns
        -------
        None or DataFrame

        Raises
        -------
        TypeError
            if a not supported file_type was passed
        S3ObjectNotFound
            if s3 key was not found
        CredentialsExpired
            if AWS credentials need to be refreshed
        """
        # check if file should be downloaded or not
        file_exists_locally: bool = local_file_exists(filepath)
        if file_exists_locally and not overwrite:
            logger.info(
                f"File {self.s3_key} already exists locally as "
                f"{filepath}-> download skipped"
            )
        else:
            self.file_download(filepath)
        if read_to_df:
            return self._local_file_to_df(filepath, load_args)
        return None

    @staticmethod
    def _local_file_to_df(
        filepath: str,
        load_args: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Read local file as a DataFrame

        Parameters
        ----------
        filepath : str
            local filepath of file to upload to s3
        load_args : dict
            Any arguments that can be passed to the corresponding read method if used

        Returns
        -------
        DataFrame

        Raises
        -------
        TypeError
            if a not supported file_type was passed
        FileNotFoundError
            if local file was not found
        """
        return file_to_df(filepath, load_args)

    def put_file_from_local(self, filepath: str, overwrite: bool = False) -> None:
        """
        Upload local file to s3

        Parameters
        ----------
        filepath : str
            local filepath of file to upload to s3
        overwrite : bool default = False
            If set to True, method will overwrite the s3 object

        Returns
        -------
        None

        Raises
        -------
        FileNotFoundError
            if local file was not found
        CredentialsExpired
            if AWS credentials need to be refreshed
        """
        if not local_file_exists(filepath):
            raise FileNotFoundError(f"{filepath} does not exist")

        s3_object_exists: bool = self.s3_key_exists()
        if s3_object_exists and not overwrite:
            logger.info(f"File {self.s3_key} already exists -> upload skipped")
        else:
            return self.s3_file_upload(filepath)

    def put_file_from_df(
        self,
        df: pd.DataFrame,
        overwrite: bool = False,
        save_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Save DataFrame as an object on s3

        Parameters
        ----------
        df : DataFrame
            Pandas DataFrame to upload as a `file_type`
        overwrite : bool default = False
            If set to True, method will overwrite the s3 object
        save_args : dict
            Any arguments that can be passed to the corresponding save method if used

        Returns
        -------
        None

        Raises
        -------
        CredentialsExpired
            if AWS credentials need to be refreshed
        """
        s3_object_exists: bool = self.s3_key_exists()
        if s3_object_exists and not overwrite:
            logger.info(f"File {self.s3_key} already exists -> upload skipped")
        return self.df_to_s3_object(df, save_args)
