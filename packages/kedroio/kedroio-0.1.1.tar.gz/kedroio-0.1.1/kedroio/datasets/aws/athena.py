from typing import Dict, Any, Union

from kedro.io import AbstractDataSet
import pandas as pd

from kedroio.connectors.aws.athena import AthenaQuery


class AthenaQueryDataSet(AbstractDataSet, AthenaQuery):
    """
    Executes an Athena Query and downloads the CSV result. This can optionally be read
    into a DataFrame.
    Note: This DataSet Class has no _save method.

    """

    def __init__(
        self,
        filepath: str,
        sql_filepath: str,
        bucket: str,
        workgroup: str,
        subfolder: str,
        region_name: str,
        params_yml_path: str = "conf/base/parameters.yml",
        verbosity: int = 1,
        read_timeout_sec: int = 1800,
        max_attempts: int = 3,
        read_result: bool = True,
        overwrite: bool = False,
        load_args: Dict[str, Any] = None,
        query_params: Dict[str, Any] = None,
    ) -> None:
        """

        Parameters
        ----------
        filepath : str
            filepath to save result csv
        sql_filepath : str
            filepath to sql file that contains the query to be executed
        bucket : str
            s3 bucket where Athena workgroup is set to save query results
        workgroup : str
            Athena workgroup to use
        subfolder : str
            s3 subdir where results are written to
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
        read_result : bool, default = True
            if True then downloaded csv will be loaded into a DataFrame
        overwrite : bool, default = False
            if local filepath exists, execute query and overwrite local file
        load_args : dict
            Any arguments that can be passed to the corresponding read method if used
        query_params: dict
            dict of query params, of name: type pair
        """
        self.filepath = filepath
        self.sql_filepath = sql_filepath
        self.bucket = bucket
        self.workgroup = workgroup
        self.subfolder = subfolder
        self.region_name = region_name
        self.params_yml_path = params_yml_path
        self.verbosity = verbosity
        self.read_timeout_sec = read_timeout_sec
        self.max_attempts = max_attempts
        self.read_result = read_result
        self.overwrite = overwrite
        self.load_args = load_args
        self.query_params = query_params
        super().__init__(
            sql_filepath=self.sql_filepath,
            bucket=self.bucket,
            subfolder=self.subfolder,
            workgroup=self.workgroup,
            region_name=self.region_name,
            params_yml_path=self.params_yml_path,
            verbosity=self.verbosity,
            read_timeout_sec=self.read_timeout_sec,
            max_attempts=self.max_attempts,
            query_params=self.query_params,
        )

    def _load(self) -> Union[None, pd.DataFrame]:
        """
        Executes an Athena Query, downloads the result csv with option of reading it
        into a DaraFrame.

        Returns
        -------
        None or pd.DataFrame
        """
        return self.get(
            filepath=self.filepath,
            overwrite=self.overwrite,
            read_to_df=self.read_result,
            load_args=self.load_args,
        )

    def _save(self, **kwargs) -> None:
        raise NotImplementedError("Athena will never be used as an output of a node")

    def _exists(self) -> bool:
        return self.file_exists(self.filepath)

    def _describe(self) -> Dict[str, Any]:
        return self.__dict__
