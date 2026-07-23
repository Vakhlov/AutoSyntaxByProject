"""
Общие псевдонимы типов.
"""

from typing import Dict, List, Union

SyntaxMap = Dict[str, str]

SettingsValue = Union[bool, float, int, str, Dict[str, str], List[str]]

SettingsDict = Dict[str, SettingsValue]
