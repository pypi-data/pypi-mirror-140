import re
from typing import Optional, Dict, Any, Union
import os
import logging
import time

import boto3
import pandas as pd
from botocore.config import Config
from botocore.exceptions import ClientError

from .s3 import S3File
from .exceptions import AthenaQueryParameters, AthenaQueryFailed, CredentialsExpired
from kedroio.connectors.util.local import load_from_yml, local_file_exists, file_to_df

logger = logging.getLogger(__name__)


class AthenaQuery:
    """
    Executes an Athena query, downloads the CSV result with option to read into a
    DataFrame

    Parameters
    ----------
    sql_filepath : str
        filepath to sql file that contains the query to be executed
    bucket : str
        s3 bucket where Athena workgroup is set to save query results
    subfolder : str
        s3 subdir where results are written to
    workgroup : str
        Athena workgroup to use
    region_name : str
        AWS region for Athena and s3 clients
    params_yml_path : str
        filepath to yml file containing params to be replaced in sql query
    verbosity : int, default = 1
        higher increases verbosity
    read_timeout_sec : int
        Athena query timeout in seconds (max set by AWS is 30 minutes)
    max_attempts : int, default = 3
        number of attempts for query
    query_params: dict
        dict of query params, of name: type pair
    """

    def __init__(
        self,
        sql_filepath: str,
        bucket: str,
        subfolder: str,
        workgroup: str,
        region_name: str,
        params_yml_path: Optional[str] = None,
        verbosity: int = 1,
        read_timeout_sec: int = 1800,
        max_attempts: int = 3,
        query_params: Dict[str, Any] = None,
    ):
        """

        Parameters
        ----------
        sql_filepath : str
            filepath to sql file that contains the query to be executed
        bucket : str
            s3 bucket where Athena workgroup is set to save query results
        subfolder : str
            s3 subdir where results are written to
        workgroup : str
            Athena workgroup to use
        region_name : str
            AWS region for Athena and s3 clients
        params_yml_path : str
            filepath to yml file containing params to be replaced in sql query
        verbosity : int, default = 1
            higher increases verbosity
        read_timeout_sec : int
            Athena query timeout in seconds (max set by AWS is 30 minutes)
        max_attempts : int, default = 3
            number of attempts for query
        query_params: dict
            dict of query params, of name: type pairs
        """
        self.sql_filepath = sql_filepath
        self.bucket = bucket
        self.subfolder = subfolder
        self.workgroup = workgroup
        self.s3_result_loc = self._parse_s3_result_loc(bucket, subfolder)
        self.region_name = region_name
        self.params_yml_path = params_yml_path
        self.verbosity = verbosity
        self.read_timeout_sec = read_timeout_sec
        self.max_attempts = max_attempts

        default_query_parameters = {}
        self._query_params = (
            {**default_query_parameters, **query_params}
            if query_params is not None
            else default_query_parameters
        )

        self.athena = self._create_athena_client()

    def _create_athena_client(self) -> boto3.client("athena"):
        config = Config(
            signature_version="s3v4",
            read_timeout=self.read_timeout_sec,
            retries=dict(max_attempts=self.max_attempts),
        )
        return boto3.client("athena", region_name=self.region_name, config=config)

    def get(
        self,
        filepath: str,
        overwrite: bool = False,
        read_to_df: bool = True,
        load_args: Optional[Dict[str, Any]] = None,
    ) -> Union[None, pd.DataFrame]:
        """
        Execute an Athena query and download csv result locally. If read_to_df=True,
        the downloaded csv will be then read into a DataFrame

        Parameters
        ----------
        filepath :
            local filepath to save result csv as
        overwrite : bool, default = False
            if local filepath exists, execute query and overwrite local file
        read_to_df: bool, default = True
            if True then downloaded csv will be loaded into a DataFrame
        load_args : dict
            Any arguments that can be passed to the corresponding read method if used

        Returns
        -------
        None, DataFrame
        """
        # check if file should be downloaded or not
        file_exists_locally: bool = local_file_exists(filepath)
        if file_exists_locally and not overwrite:
            logger.info(f"File {filepath} already exists locally -> query skipped")
            if read_to_df:
                return file_to_df(filepath, load_args)
        else:
            s3_result = self._run_query()
            s3_file = S3File(self.bucket, self.region_name, s3_result)
            return s3_file.get(filepath, overwrite, read_to_df, load_args)

    @staticmethod
    def _parse_s3_result_loc(bucket: str, subfolder: str) -> str:
        """
        The s3 location where the CSV query result will by written to by Athena

        Parameters
        ----------
        bucket : str
            Bucket name that Athena workgroup is set to write results to
        subfolder : str, optional
            If CSV should be written under a subdir in the s3 bucket

        Returns
        -------
        str
            the location on s3 under which the csv can be found

        """
        loc = os.path.join("s3://", bucket)
        if subfolder:
            return os.path.join(loc, subfolder)
        return loc + "/"

    @staticmethod
    def file_exists(filepath: str) -> bool:
        """
        Indicates if filepath already exists locally

        Parameters
        ----------
        filepath : str
            local file
        Returns
        -------
        bool
        """
        return local_file_exists(filepath)

    def _run_query(self) -> str:
        """
        Trigger the Athena query execution, capture the execution id and once complete,
        read the CSV saved in the s3_result_loc bucket.

        """
        sql_query: str = self._parse_sql_file()
        query_filename = self.sql_filepath.split("/")[-1]
        if self.verbosity > 0:
            logger.info(f"Executing Athena query {query_filename}")
        execution_id, s3_key = self._start_athena_job(sql_query)

        query_status: Union[str, None] = None
        # query execution status every 5 seconds
        while query_status in ["QUEUED", "RUNNING"] or query_status is None:
            response = self.athena.get_query_execution(QueryExecutionId=execution_id)
            query_status = response["QueryExecution"]["Status"]["State"]

            if query_status in ["FAILED", "CANCELLED"]:
                raise AthenaQueryFailed(
                    f"Athena query in {self.sql_filepath} {query_status} \n"
                    f"Please look in "
                    f"https://{self.region_name}.console.aws.amazon.com/athena"
                    f"/query-history/home?region={self.region_name}"
                    f"for any errors, execution_id={execution_id}"
                )
            time.sleep(5)
            if self.verbosity > 1:
                logger.info(f"Athena query {query_filename} status: {query_status}")

        return s3_key

    def _start_athena_job(self, sql: str) -> (str, str):
        try:
            response: dict = self.athena.start_query_execution(
                QueryString=sql,
                ResultConfiguration={"OutputLocation": self.s3_result_loc},
                WorkGroup=self.workgroup,
            )
            # construct s3_key for the csv result
            execution_id = response.get("QueryExecutionId")
            s3_key: str = os.path.join(self.subfolder, execution_id)
            s3_key: str = s3_key + ".csv"
            if self.verbosity > 1:
                logger.info(f"Result CSV: {s3_key}")
        except ClientError as e:
            if "(UnrecognizedClientException)" in str(e):
                aws_profile = os.getenv("AWS_PROFILE")
                raise CredentialsExpired(f"{aws_profile} credentials expired")
            else:
                raise

        return execution_id, s3_key

    def _parse_sql_file(self) -> str:
        """
        Open the .sql file and return the sql query as a string.
        If params are used then the key:value pairs for the params are loaded and the
        param name is replaced in the sql query string
        """
        # open sql file and read as text
        if not local_file_exists(self.sql_filepath):
            raise FileNotFoundError(f"{self.sql_filepath} does not exist")
        with open(self.sql_filepath, "r") as f:
            sql_query: str = f.read()

        # sql parameters should be enclosed in "{{}}"
        # replace these with the actual parameter values in the sql string
        if self._query_params:
            query_params = self._load_query_params()
            for param in query_params:
                to_replace = "{{" + param + "}}"
                # enforce the use of double curly brackets for parameters
                if not re.search(to_replace, sql_query):
                    raise AthenaQueryParameters(
                        f"Include the param in '{{}}, i.e. '{to_replace}' in sql query"
                    )
                sql_query = sql_query.replace(to_replace, query_params[param])

        return sql_query

    def _load_query_params(self) -> Dict[str, str]:
        """Load query parameters from a yml file if they are of type=yml_variable, or
        from the environment variables if they are of type=env_variable."""
        # create a dict and populate with parameter name: value pairs
        query_params = {}
        for param in self._query_params.keys():
            param_name = self._query_params[param]["name"]
            param_type = self._query_params[param]["type"]

            if param_type == "yml_variable":
                # load parameter value from a yml file
                try:
                    param_value = load_from_yml(
                        yml_filepath=self.params_yml_path, key=param_name
                    )
                    query_params[param] = str(param_value)
                except KeyError:
                    raise AthenaQueryParameters(
                        f"Unable to find param {param_name} in {self.params_yml_path}"
                    )
                except Exception as ex:
                    logger.error(f"error while attempting to load {param_name}: {ex}")
                    raise
            elif param_type == "env_variable":
                # grab parameter value from the environment variable
                query_param = os.getenv(param_name)
                if query_param is not None:
                    query_params[param] = query_param
                else:
                    raise AthenaQueryParameters(
                        f"Unable to find env_variable param {param_name}"
                    )
            else:
                raise AthenaQueryParameters(
                    f"Parameter type '{param_type}' not valid. Use one of "
                    f"[yml_variable/env_variable]"
                )

        return query_params
