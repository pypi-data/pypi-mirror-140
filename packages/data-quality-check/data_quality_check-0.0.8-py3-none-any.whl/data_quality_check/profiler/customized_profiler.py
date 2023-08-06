from typing import Dict, List

from pyspark.sql import SparkSession
from data_quality_check.config import ConfigDataset, ConfigProfilingCustomized
from data_quality_check.core.checks.customized_check import CodeInSetCheck, KeyMappingCheck


class CodeCheckResult:
    field_name: str
    config_expected_codes: list
    null_row_count: int
    unexpected_valued_row_count: int
    unexpected_code_samples: list
    total_row_count: int

    def __init__(self, field_name: str, config_expected_codes: list, null_row_count: int = 0,
                 unexpected_valued_row_count: int = 0, unexpected_code_samples: list = [], total_row_count: int = 0):
        self.field_name = field_name
        self.config_expected_codes = config_expected_codes
        self.null_row_count = null_row_count
        self.unexpected_valued_row_count = unexpected_valued_row_count
        self.unexpected_code_samples = unexpected_code_samples
        self.total_row_count = total_row_count

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            'field_name': self.field_name,
            'config_expected_codes': self.config_expected_codes,
            'unexpected_code_samples': self.unexpected_code_samples,
            'null_row_count': self.null_row_count,
            'unexpected_valued_row_count': self.unexpected_valued_row_count,
            'total_row_count': self.total_row_count
        }


class KeyMappingCheckResult:
    field_name: str
    target_table: str
    target_column: str
    outstanding_value_samples: list
    outstanding_row_count: int
    null_and_empty_row_count: int
    total_row_count: int

    def __init__(self, field_name: str, target_table: str, target_column: str,
                 outstanding_value_samples: list = [], outstanding_row_count: int = 0,
                 null_and_empty_row_count: int = 0,
                 total_row_count: int = 0):
        self.field_name = field_name
        self.target_table = target_table
        self.target_column = target_column
        self.outstanding_value_samples = outstanding_value_samples
        self.outstanding_row_count = outstanding_row_count
        self.null_and_empty_row_count = null_and_empty_row_count
        self.total_row_count = total_row_count

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            'field_name': self.field_name,
            'target_table': self.target_table,
            'target_column': self.target_column,
            'outstanding_value_samples': self.outstanding_value_samples,
            'outstanding_row_count': self.outstanding_row_count,
            'null_and_empty_row_count': self.null_and_empty_row_count,
            'total_row_count': self.total_row_count
        }


class CustomizedProfilerResult:
    code_check_result: List[CodeCheckResult] = []
    key_mapping_check_result: List[KeyMappingCheckResult] = []

    def __init__(self, code_check_result: Dict = None, key_mapping_check_result: Dict = None):
        if code_check_result is not None:
            self.code_check_result = code_check_result

        if key_mapping_check_result is not None:
            self.key_mapping_check_result = key_mapping_check_result

    def has_code_check_result(self):
        return len(self.code_check_result) > 0

    def has_key_mapping_check_result(self):
        return len(self.key_mapping_check_result) > 0

    def to_dict(self):
        result = {}
        if self.has_code_check_result():
            result['code_check'] = []
            for cc in self.code_check_result:
                result['code_check'].append(cc.to_dict())

        # Key Mapping Check
        if self.has_key_mapping_check_result():
            result['key_mapping_check'] = []
            for kmc in self.key_mapping_check_result:
                result['key_mapping_check'].append(kmc.to_dict())
        return result


class CustomizedProfiler:
    dataset_config: ConfigDataset
    profiling_config: ConfigProfilingCustomized
    spark: SparkSession

    def __init__(self, spark, dataset_config: ConfigDataset,
                 customized_profiling_config: ConfigProfilingCustomized = ConfigProfilingCustomized()):
        self.spark = spark
        self.dataset_config = dataset_config
        self.profiling_config = customized_profiling_config

    def code_check(self, table_name: str, field_name: str, config_expected_codes: list = []):
        cisc = CodeInSetCheck(spark=self.spark, table_name=table_name, column_name=field_name,
                              config_expected_codes=config_expected_codes)
        result = cisc.run()
        return CodeCheckResult(field_name=result.get('column_name'),
                               config_expected_codes=result.get('config_expected_codes'),
                               null_row_count=result.get('null_row_count'),
                               unexpected_valued_row_count=result.get('unexpected_valued_row_count'),
                               unexpected_code_samples=result.get('unexpected_code_samples'),
                               total_row_count=result.get('total_row_count'))

    def key_mapping_check(self, table_name, field_name, target_table_name, target_field_name):
        kmc = KeyMappingCheck(self.spark, table_name, column_name=field_name, target_table_name=target_table_name,
                              target_column_name=target_field_name)
        result = kmc.run()
        return KeyMappingCheckResult(field_name=result.get('column_name'),
                                     target_table=result.get('target_table_name'),
                                     target_column=result.get('target_column_name'),
                                     outstanding_value_samples=result.get('outstanding_value_samples'),
                                     outstanding_row_count=result.get('outstanding_row_count'),
                                     null_and_empty_row_count=result.get('null_and_empty_row_count'),
                                     total_row_count=result.get('total_row_count'))

    def run(self, return_type='dict'):
        table_name = self.dataset_config.name
        customized_profiler_result = CustomizedProfilerResult()

        # Code Check
        code_check_list = self.profiling_config.code_check
        if code_check_list is not None and len(code_check_list) > 0:
            for cc in code_check_list:
                cc_result = self.code_check(table_name=table_name, field_name=cc.column, config_expected_codes=cc.codes)
                customized_profiler_result.code_check_result.append(cc_result)

        # Key Mapping Check
        key_mapping_check_list = self.profiling_config.key_mapping_check
        if key_mapping_check_list is not None and len(key_mapping_check_list) > 0:
            for kmc in key_mapping_check_list:
                kmc_result = self.key_mapping_check(table_name=table_name, field_name=kmc.column,
                                                    target_table_name=kmc.target_table,
                                                    target_field_name=kmc.target_column)
                customized_profiler_result.key_mapping_check_result.append(kmc_result)

        if return_type == 'dict':
            return customized_profiler_result.to_dict()
        else:
            return customized_profiler_result
