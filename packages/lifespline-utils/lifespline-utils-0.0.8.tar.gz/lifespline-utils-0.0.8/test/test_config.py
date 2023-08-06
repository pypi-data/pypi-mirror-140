from typing import Dict, List
import json
from lifespline_utils.config import Config, Section
from configparser import ConfigParser
from lifespline_utils.error import (
    LSUInvalidSectionKeyError,
    LSUInvalidSectionError
)

def test_get_section():
    """Test whether a section in a test file is correctly read as a config.
    Section.
    """
    assert True


def test_get_values():
    """Test whether a section values in a test file is correctly read.
    """
    assert True

# Test `lifespline_utils.config.Config.__init__`
# 
# Features to test
# - loads a config dump
# - read configuration files

def test_dict_to_config():
    """Test that a dictionary data structure is properly converted to a 
    dictionary of `lifespline_utils.config.Section`.
    """
    res: bool = True

    # create mock dump data file
    mock: Dict[str, Dict[str, str]]
    mock = {
        "section-1": {
            "key-1": "value-1",
            "key-2": "value-2",
            "key-3": "value-3"
        },
        "section-2": {
            "key-1": "value-1"
        },
    }

    # convert the dictionary to a dictionary of sections
    sections: Dict[str, Section]
    sections = Config._dict_to_sections(config=mock)

    # compare each section with the mock data
    for section, values in mock.items():
        mock_section: Dict[str, str] = mock[section]
        config_section: Section = sections[section]

        if res:

            for key in values.keys():
                mock_value: str = mock_section[key]
                section_value: str = config_section.get_values()[section][key]
                res = res and mock_value == section_value

                if not res:
                    break

    assert res


def test_load():
    """Verify that a dumped configuration file is properly loaded.

    Tests depending on this test:

    + `lifespline_utils.test.test_config.test_init_load_dump`.
    """
    res: bool = True

    # read test dump data file
    expected: Dict[str, Dict[str, str]]
    dump: str = 'test/test_config/setup.json'
    with open(dump) as json_file:
        expected = json.load(json_file)

    # load the configuration from the dumped file
    config: Config = Config(dump=dump)

    # compare 
    for section, values in expected.items():
        for key, value in values.items():
            expected_value: str = expected[section][key]
            value: str = config.get_section(section).get_values(key)[section][key]
            comparison = expected_value == value

            res = res and comparison

            if not res:
                assert expected_value == value

    assert res


def test_get_section_pass_argument():
    """Test whether `lifespline_utils.config.Config.get_section` properly 
    returns the requested section.

    Tests depending on this test:

    + `lifespline_utils.test.test_config.test_init_single_path`.
    """
    res: bool = True

    # read expected
    expected: Dict[str, Dict[str, str]]
    root: str = 'test/test_config/'
    setup: str = f'{root}setup1.cfg'
    parser: ConfigParser = ConfigParser()
    parser.read(setup)
    expected = parser._sections.copy()

    # create config from expected
    config: Config = Config(setup, verbose=True)

    # verify all section names exist in the config. If the section doesn't 
    # exist, an exception will be raised.
    for section in expected.keys():
        config.get_section(section)

    assert res


def test_get_section_pass_no_valid_section():
    """Test whether `lifespline_utils.config.Config.get_section` raises `lifespline_utils.error.LSUInvalidArgumentsError` if an invalid section name is passed as an argument.

    Assumes `lifespline_utils.config.Section.get_values`
    """
    res: bool = False

    # an empty config will not have a section name
    invalid_section_name: str = 'foo'
    config: Config = Config(verbose=True)
    try:
        config.get_section(invalid_section_name, verbose=True)
    except LSUInvalidSectionError:
        res = True

    assert res


def test_init_single_path():
    """Verify that `lifespline_utils.config.Config` is correctly initialized from a single configuration path.

    The test is covered by `lifespline_utils.test.test_config.
    test_get_section_pass_argument`. Reading from a single configuration file 
    path and checking for the expected sections is sufficient to prove the test.
    """
    pass 


def test_init_multiple_paths():
    """Verify that `lifespline_utils.config.Config` is correctly initialized from multiple configuration paths.
    """
    res: bool = True

    # read expected configuration files and parse them into a dictionary
    expected: Dict[str, Dict[str, str]] = {}
    root: str = 'test/test_config/'
    setups: List[str] = [
        f'{root}setup1.cfg',
        f'{root}setup2.cfg'
    ]
    parser: ConfigParser
    for setup in setups:
        parser = ConfigParser()
        parser.read(setup)
        expected = { **expected, **parser._sections.copy() }

    # init config from expected configuration files
    config: Config = Config(*setups, verbose=True)

    # compare the dictionary with the config by verifying all section names 
    # exist in the config. If the section doesn't exist, an exception will be 
    # raised. See: `lifespline_utils.config.Config.get_section`
    for section in expected.keys():
        config.get_section(section)

    assert res


def test_init_load_dump():
    """Verify that `lifespline_utils.config.Config` is correctly initialized from configuration dump.


    Test equivalent to `lifespline_utils.test.test_config.test_load`. The configuration does nothing more than loading the dump file.
    """
    pass 


def test_init_conflicting_config_sections():
    """Verify that `lifespline_utils.config.Config` raises an error if the 
    configuration files have a section header in common.
    """
    pass


def test_get_values_single_key():
    """Test whether `lifespline_utils.config.Section.get_values` properly 
    returns a correct single key value.

    Because this test is run on all keys, it also tests whether a config is properly initialized from a single config path.
    """
    res: bool = True

    # read expected
    expected: Dict[str, Dict[str, str]]
    root: str = 'test/test_config/'
    setup: str = f'{root}setup1.cfg'
    parser: ConfigParser = ConfigParser()
    parser.read(setup)
    expected = parser._sections.copy()

    # create config from expected
    config: Config = Config(setup, verbose=True)

    # compare section key value by key value
    for section, values in expected.items():
        for key, expected_value in values.items():
            true_value: str = config.get_section(section).get_values(key)
            true_value = true_value[section][key]
            comparison = expected_value == true_value

            res = res and comparison

            if not res:
                assert expected_value == true_value

    assert res


def test_get_values_multiple_keys():
    """Test whether `lifespline_utils.config.Config.get_section` properly 
    returns the requested section.
    """
    res: bool = True

    # read expected
    expected: Dict[str, Dict[str, str]]
    root: str = 'test/test_config/'
    setup: str = f'{root}setup1.cfg'
    parser: ConfigParser = ConfigParser()
    parser.read(setup)
    expected = parser._sections.copy()

    # create config from expected
    config: Config = Config(setup, verbose=True)

    # compare section key value by key value
    for section, values in expected.items():
        expected_keys: List[str] = list(values.keys())
        expected_values: List[str] = list(values.values())
        true_section: Dict[str, Section] = config.get_section(section)
        true_values: Dict[str, str] = true_section.get_values(*expected_keys)
        true_values: List[str] = list(true_values[section].values())

        expected_values.sort()
        true_values.sort()
        comparison: bool = expected_values == true_values

        if not comparison:
            assert expected_values == true_values

    assert res


def test_get_values_invalid_key():
    """Test whether `lifespline_utils.config.Config.get_section` properly 
    returns the requested section.
    """
    res: bool = False

    # the mock config setup does not have key-4
    root: str = 'test/test_config/'
    setup: str = f'{root}setup1.cfg'
    section: str = 'section-1'
    invalid_key: str = 'key-4'
    config: Config = Config(setup, verbose=True)

    # the line below must raise an exception for an unexisting key
    try:
        config.get_section(section).get_values(invalid_key, verbose=True)
    except LSUInvalidSectionKeyError as err:
        res = True

    assert res


