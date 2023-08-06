import os
from pathlib import Path
import logging
from typing import Optional, Union, Dict, Any, Literal, get_args

import pandas as pd
import yaml


logger = logging.getLogger(__name__)


FileTypes = Literal["csv", "parquet"]


class YamlNotFound(Exception):
    pass


def local_file_exists(filepath: str) -> bool:
    return os.path.isfile(filepath)


def local_dir_exists(dir_: str) -> bool:
    return os.path.isdir(dir_)


def make_dir_if_not_exists(
    dir_: Optional[str] = None, filepath: Optional[str] = None
) -> bool:
    """Create dir if not exising.
    Returns True if dir was created, False if skipped"""
    assert not all([dir_, filepath]), "only one of [dir/filepath] should be provided"
    if filepath:
        dir_ = os.path.dirname(filepath)
    if not os.path.isdir(dir_):
        logger.debug(f"Creating dir: {dir}")
        Path(dir_).mkdir(parents=True, exist_ok=True)
        return True
    return False


def load_from_yml(yml_filepath, key) -> Union[str, dict]:
    """Method used to read yml configurations"""
    if os.path.isfile(yml_filepath):
        conf = yaml.load(open(yml_filepath), Loader=yaml.FullLoader)
        value = conf.get(key)
        return value
    else:
        raise YamlNotFound(f"yml '{yml_filepath}' not found")


def infer_file_type(filename: str) -> str:
    return filename.split(".")[-1]


def file_to_df(
    filepath: str, load_args: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    if not local_file_exists(filepath):
        raise FileNotFoundError(f"{filepath} does not exist")
    file_type = infer_file_type(filepath)
    _load_args = {}
    if load_args:
        _load_args.update(load_args)
    if file_type == "csv":
        return pd.read_csv(filepath, **_load_args)
    elif file_type == "parquet":
        return pd.read_parquet(filepath, **_load_args)
    else:
        raise TypeError(f"Allowed file_type options: {get_args(FileTypes)}")
