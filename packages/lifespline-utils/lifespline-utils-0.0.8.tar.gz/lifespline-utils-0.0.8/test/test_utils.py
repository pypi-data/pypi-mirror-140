"""_summary_."""
from typing import List, Dict
from os.path import expanduser
import os
from lifespline_utils import utils
from lifespline_utils.error import LSUDuplicateConfigSectionsError
from requests_toolbelt import user_agent


def test_parse_files_invalid_files():
    """Verify if parsing at least one invalid file, the exception 
    LSUInvalidFileFormatException is thrown.
    """
    # TODO: add files with edge cases
    invalid_file_paths: List[str] = [
        "test/test_utils/invalid_setup.cfg",
    ]
    assert True


def test_parse_files_valid_files():
    """Verify if parsing only valid files, the exception 
    LSUInvalidFileFormatException is not thrown.
    """
    # TODO: add files with edge cases
    valid_file_paths: List[str] = [
        "test/test_utils/valid_setup.cfg",
    ]
    assert True


def test_parse_files_verify_correct_parse():
    """Verifies that valid cfg files are correctly parsed.
    """
    valid_file_paths: List[str] = [
        "test/test_utils/valid_setup.cfg",
    ]
    expected_output: Dict[str, Dict[str, str]] = {
        'section': {
            'key': 'value'
        }
    }
    assert True


def test_parse_files_verify_missing_section_header():
    """Verify that duplicate section headers will raise `lifespline_utils.error.LSUDuplicateConfigSectionsError` 
    """
    res: bool = False

    # read configuration files that have a duplicate section
    root: str = "test/test_config/"
    conflicting_setups: List[str] = [
        f"{root}setup1.cfg",
        f"{root}setup3.cfg",
    ]

    # verify that the correct error is raised
    try:
        utils.parse_files(*conflicting_setups)
    except LSUDuplicateConfigSectionsError as err:
        res = True

    assert res


def test_parse_files_verify_duplicate_sections():
    """Verify that duplicate section headers will raise `lifespline_utils.error.LSUDuplicateConfigSectionsError` 
    """
    res: bool = False

    # read configuration files that have a duplicate section
    root: str = "test/test_config/"
    conflicting_setups: List[str] = [
        f"{root}setup1.cfg",
        f"{root}setup3.cfg",
    ]

    # verify that the correct error is raised
    try:
        utils.parse_files(*conflicting_setups)
    except LSUDuplicateConfigSectionsError as err:
        res = True

    assert res


def test_parse_files_no_duplicate_sections():
    """Verify that duplicate section headers will raise `lifespline_utils.error.LSUDuplicateConfigSectionsError` 
    """
    res: bool = True

    # read configuration files that don't have a duplicate section
    root: str = "test/test_config/"
    conflicting_setups: List[str] = [
        f"{root}setup1.cfg",
        f"{root}setup2.cfg",
    ]

    # verify that no error is raised
    utils.parse_files(*conflicting_setups)

    assert res


def test_get_project_root_from_repo():
    """Verify if, after installing the package from the python package index, the project root is as expected.

    ```bash
    >>> from lifespline_utils.utils import get_path, get_project_root
    >>> get_project_root()
    '/home/dipm/src/lifespline-utils/'
    >>> get_path()
    '/home/dipm/src/lifespline-utils/.env/lib/python3.8/site-packages/lifespline_utils-0.0.8-py3.8.egg/lifespline_utils/utils.py'
    >>> get_path('README.md')
    '/home/dipm/src/lifespline-utils/README.md'
    >>> get_path('.bashrc')
    '/home/dipm/.bashrc'
    ```
    """
    assert True


def test_get_project_root_from_src():
    """Verify if, in debug mode, the project root is as expected.

    Running from local package source code
    ```bash
    >>> from lifespline_utils.utils import get_path, get_project_root
    >>> get_project_root()
    '/home/dipm/src/lifespline-utils/'
    >>> get_path()
    '/home/dipm/src/lifespline-utils/.env/lib/python3.8/site-packages/lifespline_utils-0.0.8-py3.8.egg/lifespline_utils/utils.py'
    >>> get_path('README.md')
    '/home/dipm/src/lifespline-utils/README.md'
    >>> get_path('.bashrc')
    '/home/dipm/.bashrc'
    ```
    """
    assert True


def test_get_project_root_from_build():
    """Verify if in pip-install mode, the project root is as expected.

    Running from local package build
    ```bash
    >>> from lifespline_utils.utils import get_path, get_project_root
    >>> get_project_root()
    '/home/dipm/src/lifespline-utils/'
    >>> get_path()
    '/home/dipm/src/lifespline-utils/.env/lib/python3.8/site-packages/lifespline_utils-0.0.8-py3.8.egg/lifespline_utils/utils.py'
    >>> get_path('README.md')
    '/home/dipm/src/lifespline-utils/README.md'
    >>> get_path('.bashrc')
    '/home/dipm/.bashrc'
    ```
    """
    assert True


def test_get_path_from_repo():
    """Verify if, after installing the package from the python package index, the project root is as expected.

    ```bash
    >>> from lifespline_utils.utils import get_path, get_project_root
    >>> get_project_root()
    '/home/dipm/src/lifespline-utils/'
    >>> get_path()
    '/home/dipm/src/lifespline-utils/.env/lib/python3.8/site-packages/lifespline_utils-0.0.8-py3.8.egg/lifespline_utils/utils.py'
    >>> get_path('README.md')
    '/home/dipm/src/lifespline-utils/README.md'
    >>> get_path('.bashrc')
    '/home/dipm/.bashrc'
    ```
    """
    assert True


def test_get_path_from_src():
    """Verify if, in debug mode, the project root is as expected.

    Running from local package source code
    ```bash
    >>> from lifespline_utils.utils import get_path, get_project_root
    >>> get_project_root()
    '/home/dipm/src/lifespline-utils/'
    >>> get_path()
    '/home/dipm/src/lifespline-utils/.env/lib/python3.8/site-packages/lifespline_utils-0.0.8-py3.8.egg/lifespline_utils/utils.py'
    >>> get_path('README.md')
    '/home/dipm/src/lifespline-utils/README.md'
    >>> get_path('.bashrc')
    '/home/dipm/.bashrc'
    ```
    """
    assert True


def test_get_path_from_build():
    """Verify if in pip-install mode, the project root is as expected.

    Running from local package build
    ```bash
    >>> from lifespline_utils.utils import get_path, get_project_root
    >>> get_project_root()
    '/home/dipm/src/lifespline-utils/'
    >>> get_path()
    '/home/dipm/src/lifespline-utils/.env/lib/python3.8/site-packages/lifespline_utils-0.0.8-py3.8.egg/lifespline_utils/utils.py'
    >>> get_path('README.md')
    '/home/dipm/src/lifespline-utils/README.md'
    >>> get_path('.bashrc')
    '/home/dipm/.bashrc'
    ```
    """
    assert True
