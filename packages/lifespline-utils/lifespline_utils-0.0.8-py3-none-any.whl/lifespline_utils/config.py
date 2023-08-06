"""_summary_
"""
from typing import Dict, Union, List
import lifespline_utils.utils as utils
import lifespline_utils.log as log
import json
from lifespline_utils.error import LSUInvalidArgumentsError, LSUInvalidSectionKeyError, LSUInvalidSectionError
import os
import functools as F


class Section(object):
    """`lifespline_utils.config.Section` is a config section.

    Internally, it is simple a dictionary wrapper. Each section is parsed into 
    a dictionary. The section:

    ```cfg
    [section]
    key = value
    ```

    Is parsed into:

    ```json
    {
        "section": {
            "key": "value"
        }
    }
    ```

    Which is wrapped by `lifespline_utils.config.Section` such that:
    ```json
    >>> config.get_sections('section').get_values()
    {
        "section": {
            "key": "value"
        }
    }
    ```
    """
    _name: str
    _values: Dict[str, str]
    
    def __init__(self, name: str, values: Dict[str, Union[str, List[str]]], verbose=False):
        """Initialize a new `lifespline_utils.config.Section`.

        Args:
            name (str): The section name
            values (Dict[str, Union[str, List[str]]]): The section values.
            verbose (bool, optional): Print to `stdout` iff `True`. Defaults to `False`.
        """        
        self._name = name
        self._values = values

        log.Section.init(verbose=verbose)

    def get_values(self, *keys: str, verbose: bool = False):
        """Get the values of a config section. See the examples below.

            Prints the selected key values.

        Args:
            keys (`(str)`): The selected section keys
            verbose (`bool`): Print the returned value to the `stdout`
            value_only (`bool`): Return only the value if `value_only`

        Returns:
            (`Dict[str, Dict[str, str]]`) The selected section keys

        Raises:

            (`lifespline_utils.error.LSUInvalidSectionKeyError`): The section
            key does not exist

        Examples

        ```python
        >>> config: Config = Config("test/test_config/setup1.cfg", verbose=True)
        >>> config.get_sections('section-1')
        {
            "section-1": {
                "key-1": "value-1",
                "key-2": "value-2",
                "key-3": "value-3"
            }
        }
        >>> config.get_sections('section-1').get_values()
        {
            "section-1": {
                "key-1": "value-1",
                "key-2": "value-2",
                "key-3": "value-3"
            }
        }

        >>> config.get_sections('section-1').get_values('key-1', 'key-3')
        {
            "section-1": {
                "key-1": "value-1",
                "key-3": "value-3"
            }
        }

        >>> config.get_sections('section-1').get_values('key-1')
        {
            "section-1": {
                "key-1": "value-1",
            }
        }

        >>> config.get_sections('section-1').get_values('key-4')
        ...
        lifespline_utils.error.LSUInvalidSectionKeyError: No such section key: key-4
        ```
        """
        values: Dict[str, Dict[str, str]] = {
            self._name: {}
        }

        if len(keys) == 0:
            values[self._name] = self._values
        elif len(keys) == 1:
            key: str = keys[0]
            value: str = self._values.get(key)
            if not value:
                raise LSUInvalidSectionKeyError(f"No such section key: {key}")

            values[self._name] = { key: value }
        elif len(keys) > 1:
            section_values: List[str] = []
            for key in list(keys):
                value: str = self._values.get(key)
                if not value:
                    err: str = f"No such section key: {key}"
                    raise LSUInvalidSectionKeyError(err)

                section_values.append((key, value))

            def to_values_dict(acc, pair):
                """Get a dictionary with keys `key1`, `key2` and the 
                corresponding values. 

                Args:
                    key1 (`str`): _description_
                    key2 (`str`): _description_

                Returns:
                    `Dict[str, str]`: A dictionary with keys `key1`, `key2` and the corresponding values.
                """
                key: str = pair[0]
                value: str = pair[1]

                res: Dict[str, str] = { **acc, **{ key: value } }

                return res

            acc: Dict = {}
            values[self._name] = F.reduce(to_values_dict, section_values, acc)

        log.Section.get_values(values, verbose=verbose)

        return values


    def __str__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        # TODO: move to lifespline_utils.log
        return json.dumps({self._name: self._values}, indent=4, sort_keys=True)

class Config(object):
    """`lifespline_utils.config.Config` is an object holding project configuration values.

        The object can be persisted in between contexts.
    """
    # config sections
    _sections: Dict[str, Section] = {}

    def __init__(self, *paths: str, dump: str = 'setup.json', verbose: bool = False):
        """Initialize a new `lifespline_utils.config.Config`.

            Loads configuration dump (`dump` or `setup.json`) if there is a 
            configuration dump. Otherwise it parses the specified config files.
            If there no paths are provided, it initializes an empty config.
            Prints the loaded configuration (if `verbose`).

            No section name sorting is guaranteed.

        # Args

            paths (`str`): The configuration files paths
            dump (`str`, optional): The configuration dumped file path. 
            Defaults to `setup.json`, i.e., the configuration is dumped to 
            your project root directory.
            verbose (`bool`, optional): `True` for verbose logging. Defaults to 
            `False`.

        # Returns

            `lifespline_utils.config.Config` A configuration object

        # Examples

        Load config from configuration dump

        ```python
        >>> config = Config(verbose=True)
        parsed config dump
        ```

        Create config without configuration dump and configuration files

        ```python
        >>> config = Config(verbose=True)
        initialized an empty config
        ```

        Create config from configuration paths

        ```python
        >>> paths = [
            "test/test_config/setup1.cfg",
            "test/test_config/setup2.cfg"
        ]
        >>> config = Config(*paths, verbose=True)
        parsed config files:
        [1] test/test_config/setup1.cfg
        [2] test/test_config/setup2.cfg

        >>> config
        {
            "section-1": {
                "key-1": "value-1",
                "key-2": "value-2",
                "key-3": "value-3"
            },
            "section-2": {
                "key-2": "value-2"
            }
        }
        ```
        """
        # Load configuration dump. 
        loaded: bool = self.load(path=dump, verbose=verbose)
        if not loaded:
            log.Config.init(how='no-dump', verbose=verbose)

            # If there is no configuration dump, read and parser the configuration files.
            if paths:
                config: Dict[str, Dict[str, str]]
                config = utils.parse_files(*list(paths))

                self._sections = Config._dict_to_sections(config)

                log.Config.init(*list(paths), verbose=verbose)

            if not paths:
                log.Config.init(how='empty', verbose=verbose)


    def __str__(self):
        """The string representation.
        """
        log.Config.str(self)

    @staticmethod
    def _dict_to_sections(config: Dict[str, Dict[str, str]]):
        """Convert dictionary sections to a dictionary of Sections

        # Args

            config (Dict[str, Dict[str, str]]): A config dictionary

        # Returns

            `Dict[str, lifespline_utils.config.Section]` Sections
        """
        sections: Dict[str, Section] = {}
        for section, values in config.items():
            sections[section] = Section(
                name=section,
                values=values
            )

        return sections


    def get_section(self, section: str, verbose: bool = False):
        """Get the config `section`.

            Prints the config section values (if `verbose`).

        Args:

            section `str`: The config section.

        Returns:

            `lifespline_utils.config.Section`: The config section.

        Raises:

            `lifespline_utils.error.LSUInvalidSectionError`: The provided section name does not exist in the config.

        Examples

        List sections contents
        ```python
        >>> config.get_sections('foo', verbose=True)
        ...
        lifespline_utils.error.LSUInvalidArgumentsError: No such section: 'foo'

        >>> config.get_sections('section-1', verbose=True)
        {
            "section-1": {
                "key-1": "value-1",
                "key-2": "value-2",
                "key-3": "value-3"
            }
        }
        ```
        """
        res: Section = self._sections.get(section)

        # the user specified an invalid section
        if not res:
            err: str = f"No such section: '{section}'"
            raise LSUInvalidSectionError(err)

        log.Config.get_section(section=res, verbose=verbose)

        return res


    def list_sections(self):
        """List the config section names.

            Prints the config section names.

        Returns:
            `List[str]` The list of section names
        """
        sections: List[str] = list(self._sections.keys())
        # return json.dumps(sections, indent=4, sort_keys=True)
        return sections


    def load(self, path: str = 'setup.json', verbose: bool = False):
        """Load a configuration dump.

        # Args

            path (`str`, optional):  The configuration dumped file path. 
            Defaults to `setup.json`, i.e., the configuration is dumped to 
            your project root directory.

        # Returns

            (`bool`): `True` if there was a valid config to be loaded, `False` otherwise.
        """
        res: bool = False

        config: Dict[str, Dict[str, str]]
        
        if os.path.exists(path):

            with open(path, 'r') as inp:
                config = json.load(inp)

            sections: Dict[str, Section]
            sections = Config._dict_to_sections(config)

            self._sections = sections.copy()

            res = True

        return res
