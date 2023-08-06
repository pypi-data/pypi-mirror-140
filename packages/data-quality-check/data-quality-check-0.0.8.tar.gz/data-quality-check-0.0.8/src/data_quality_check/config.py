from typing import Optional, List

from pydantic import BaseModel


# def _merge_dictionaries(dict1: dict, dict2: dict) -> dict:
#     """
#     Recursive merge dictionaries.
#
#     :param dict1: Base dictionary to merge.
#     :param dict2: Dictionary to merge on top of base dictionary.
#     :return: Merged dictionary
#     """
#     for key, val in dict1.items():
#         if isinstance(val, dict):
#             dict2_node = dict2.setdefault(key, {})
#             _merge_dictionaries(val, dict2_node)
#         else:
#             if key not in dict2:
#                 dict2[key] = val
#     return dict2


class ConfigMetadata(BaseModel):
    creator: str = 'ThoughtWorks Data Service'
    description: Optional[str] = None


class ConfigDataset(BaseModel):
    type: str = 'hive'
    name: str = None


class ConfigProfilingGeneral(BaseModel):
    columns: list = ['*']
    top_freq_values_number: int = 10


class ConfigProfilingCustomized(BaseModel):
    class CodeCheck(BaseModel):
        column: str
        codes: List[str]
        do_verify: bool = False

    class KeyMappingCheck(BaseModel):
        column: str
        target_table: str
        target_column: str
        do_verify: bool = False

    class PatternCheck(BaseModel):
        column: str
        pattern: str
        do_verify: bool = False

    code_check: Optional[List[CodeCheck]]
    key_mapping_check: Optional[List[KeyMappingCheck]]
    pattern_check: Optional[List[PatternCheck]]


class ConfigProfiling(BaseModel):
    general: ConfigProfilingGeneral = ConfigProfilingGeneral()
    customized: Optional[ConfigProfilingCustomized] = None


class Config(BaseModel):
    title: str = "Spark Profiling Report"
    metadata: Optional[ConfigMetadata] = None
    dataset: ConfigDataset = None
    profiling: ConfigProfiling = None
