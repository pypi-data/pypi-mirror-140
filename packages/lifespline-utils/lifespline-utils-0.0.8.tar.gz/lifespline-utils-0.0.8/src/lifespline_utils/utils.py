import os
from pathlib import Path
from lifespline_utils.log import logger
import pathlib
from lifespline_utils.error import (
    LSUInvalidConfigFileFormatError,
    LSUNoSuchPathError,
    LSUDuplicateConfigSectionsError
)
from typing import List, Dict
import configparser

# TODO mv to config?
_project_name: str = 'lifespline-utils'

def parse_files(*paths: str):
    """Parse files of type `.cfg` into dictionary data structure.

    Validates whether or not each path in `paths` is a well-structure cfg file, 
    and parses the files into a map of dictionaries if they're valid.

    :raises:
        `lifespline_utils.error.LSUInvalidFileFormatError`: The cfg file does not have the correct format.

        `lifespline_utils.error.LSUDuplicateConfigSectionsError`: Two 
        configuration files have the same section name.

    Args:
        path (_type_): _description_
    """

    def have_duplicate_keys(cfg1, cfg2):
        """Check if dicts `cfg1` and `cfg2` have duplicate keys.
        headers.

        Args:
            cfg1 (`dict`): dictionary
            cfg2 (`dict`): dictionary

        Returns:
            (`bool`): `True` if there are duplicate keys, `False` otherwise.
        """
        cfg1_keys = set(cfg1)
        cfg2_keys = set(cfg2)
        cfgs_keys = set({ **cfg1, **cfg2 })

        return len(cfg1_keys) + len(cfg2_keys) > len(cfgs_keys)

    # configuration file parser
    parser: configparser.ConfigParser

    # dict with parsed configuration files
    config: Dict[str, Dict[str, str]] = {}

    # get absolute paths
    abs_paths: List[str] = [get_path(path) for path in paths]

    # read and parse config files, add all parsed configuration files to
    # a dict data structure
    for abs_path in abs_paths:
        try:
            parser = configparser.ConfigParser()
            parser.read(abs_path)

            if have_duplicate_keys(cfg1=parser._sections, cfg2=config):
                err: str = f"Found duplicate keys in '{abs_path}' and some other configuration file."
                raise LSUDuplicateConfigSectionsError(err)

            config = { **config, **parser._sections }

        except configparser.MissingSectionHeaderError:
            err: str = f"Missing section header in '{abs_path}'"
            raise LSUInvalidConfigFileFormatError(err)

    return config

def get_project_root(verbose: bool = True, venv: str = '.env'):
    """Get the absolute project root path.

        Get the absolute path of your project. This is achieved by getting the parent directory of your project's python virtual environment, which defaults to `.env`.

        The project root is important to get absolute paths for whatever files you might be interested in finding whithin your project.

    ## Parameters

    + verbose (str, optional): [description]. Defaults to None.
    + venv (str, optional): The name of the python virtual environment. 
    Defaults to '.env'.

    ## Returns

        `str`: The project root path.

    ## Examples

    Having installed the package in development mode (from src)
    ```bash
    >>> from lifespline_utils.utils import get_project_root
    >>> get_project_root()
    "{home}/{lifespline-utils-project-path}/src/lifespline_utils/"
    ```

    Having installed the package from PyPi/build
    ```bash
    >>> from lifespline_utils.utils import get_project_root
    >>> get_project_root()
    "{home}/{your-project-path}/"
    ```
    """  
    curr_file_path: str = str(pathlib.Path(__file__).resolve())

    try:
        fst_index: int = curr_file_path.index(venv)
    except ValueError:
        # if the virtual environment could not be found, then the package
        # is running from a local clone.
        fst_index: int = curr_file_path.index(_project_name)
        lst_index: int = fst_index + len(_project_name) + 1
        fst_index = lst_index

    project_root: str = curr_file_path[:fst_index]

    return project_root

def get_path(path: str = ''):
    """Get the absolute path for `file`.

    Get the absolute path for `file` if `file` exists in the user home dir or 
    in the project root (see `lifespline_utils.utils.get_project_root`). `file` 
    can be either a file or a directory.

    ## Parameters

    + file (str, optional): [description]. Defaults to None.
    + verbose (str, optional): [description]. Defaults to None.

    ## Returns

        (`str`) The file path if the path exists, None if it doesn't exist.

    ## Examples

    Having installed the package in development mode (from src)
    ```bash
    >>> from lifepsline_utils.utils import get_path
    >>> get_path()
    "/{home}/{lifespline-utils-project-path}/src/lifespline_utils/utils.py"
    >>> get_path("README.md")
    "/{home}/{lifespline-utils-project-path}/README.md"
    >>> get_path(".bashrc")
    "/{home}/.bashrc"
    ```

    When installing from the PyPi/build
    ```bash
    >>> from lifepsline_utils.utils import get_path
    >>> get_path()
    '/{home}/{your-project-venv-package-egg-path}/lifespline_utils/utils.py'
    >>> get_path("README.md")
    "/{home}/{your-project-path}/README.md"
    >>> get_path(".bashrc")
    "/{home}/.bashrc"
    ```

    ```bash
    >>> get_path('foo')
    "LSUNoSuchPathError: '/home/{your-project-path}/foo'"
    ```
    """
    root: str
    file_path: str = str(pathlib.Path(__file__).resolve())

    if path:
        root = get_project_root()
        file_path = os.path.join(root, path)
        # verify whether the path exists, otherwise, verify if exists in the 
        # user home directory
        if not os.path.exists(file_path):
            root = os.path.expanduser('~')
            file_path = os.path.join(root, path)
            if not os.path.exists(file_path):
                raise LSUNoSuchPathError(f"No such path: '{file_path}'")

    return file_path
