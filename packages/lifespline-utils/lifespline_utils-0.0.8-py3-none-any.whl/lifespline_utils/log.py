"""Logging."""
import logging
from typing import Dict, List
import json

_log_format: str = "%(message)s"

logging.basicConfig(
    format=_log_format,
    level=logging.INFO,
)

logger = logging.getLogger("root")

class CLI:
    """CLI log styling
    """
    pass

class API:
    """API log styling
    """
    pass

class LogColour:
    """
    ANSI escape code: \033
    ANSI format: \033[{style};{foreground};{background}m
    https://ozzmaker.com/add-colour-to-text-in-python/
    """
    ansi_code = '\033['
    fg = {
        "black" : '30',
        "red" : '31',
        "green" : '32',
        "yellow" : '33',
        "blue" : '34',
        "purple" : '35',
        "cyan" : '36',
        "white" : '37',
        "none": '0'
    }

    bg = {
        "black" : '40',
        "red" : '41',
        "green" : '42',
        "yellow" : '43',
        "blue" : '44',
        "purple" : '45',
        "cyan" : '46',
        "white" : '47',
        "none": '0'
    }
    style = {
        'none' : 0,
        'bold' : 1,
        'underline' : 2,
        'italics' : 3,
        'underline' : 4,
    }

    def get_code(style='', fg='', bg=''):
        """Get ANSI color code:

        style;foreground;background

        Args:
            style ([type]): [description]
            fg ([type]): [description]
            bg ([type]): [description]

        Returns:
            [type]: [description]
        """
        ansi_code = '\033['
        code = ansi_code

        if style:
            code += str(style)
        if fg:
            code += f";{str(fg)}"
        if bg:
            code += f";{str(bg)}"
        if code == ansi_code:
            code += '0;0;0'

        code +='m'

        return code


class Config(object):
    
    @staticmethod
    def init(*paths: str, how: str = '', verbose: bool = False):
        if verbose:
            if how == 'no-dump':
                logger.info('no configuration dump found')
            elif how == 'empty':
                logger.info('initialized empty config')
            elif how == 'dump':
                logger.info('parsed config dump')
            elif paths:
                logger.info('parsed config files:')
                for index, path in enumerate(paths):
                    logger.info(f"[{str(index + 1)}] {path}")

    @staticmethod
    def get_section(section, verbose: bool = False):
        """Print the selected section.

        Args:
            section (Section): the selected section.
            verbose (bool, optional): Print iff `True`. Defaults to `False`.
        """        
        if verbose:
            print(json.dumps(section.get_values(), indent=4, sort_keys=True))


    @staticmethod
    def str(config):
        result: Dict[str, Dict[str, str]] = {}
        sections: List[str] = config.list_sections()

        for section in sections:
            result = { **result, **config.get_section(section).get_values() }

        return json.dumps(result, indent=4, sort_keys=True)


class Section(object):
    
    @staticmethod
    def init(*paths: str, verbose: bool = False):
        if verbose:
            pass # doesn't apply

    @staticmethod
    def get_values(values: Dict[str, Dict[str, str]], verbose: bool = False):
        """Print the selected key values.

        Args:
            values (Dict[str, Dict[str, str]]): the selected key values.
            verbose (bool, optional): Print iff `True`. Defaults to `False`.
        """        
        if verbose:
            print(json.dumps(values, indent=4, sort_keys=True))
