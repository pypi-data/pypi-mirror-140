from typing import List, Dict

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.utils import AnalysisException

from data_quality_check.config import ConfigProfilingGeneral, ConfigDataset
from data_quality_check.core.checks.general_check import ValuedRowCountCheck, MeanValueCheck, StddevValueCheck, \
    MinValueCheck, MaxValueCheck, ZeroValueRowCheck, NullRowCheck, EmptyRowCheck, ValuesCountCheck, \
    TopFreqCountByValuesCheck, UniqueValuedRowCheck, DuplicatedValuedRowCheck


class GeneralFieldResult:
    field_name: str
    min_value = None
    max_value = None
    mean_value = None
    stddev_value = None
    zero_count = None  # 0
    null_count = None  # Null
    empty_count = None  # Empty String
    valued_row_count = None
    duplicated_valued_row_count = None
    unique_valued_row_count = None
    value_count = None
    top_freq_count_by_values = None

    def __init__(self, field_name):
        self.field_name = field_name

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            'field_name': self.field_name,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'mean_value': self.mean_value,
            'stddev_value': self.stddev_value,
            'zero_count': self.zero_count,
            'empty_count': self.empty_count,
            'null_count': self.null_count,
            'valued_row_count': self.valued_row_count,
            'total_row_count': (self.null_count or 0) + (self.valued_row_count or 0),
            'unique_valued_row_count': self.unique_valued_row_count,
            'duplicated_valued_row_count': self.duplicated_valued_row_count,
            'value_count': self.value_count,
            'top_freq_count_by_values': self.top_freq_count_by_values
        }

    def to_str_dict(self):
        result_dict = self.to_dict()
        return {str(key): str(val) for key, val in result_dict.items() if key != 'top_freq_count_by_values'}


class GeneralProfilerResult:
    field_results: Dict[str, GeneralFieldResult] = {}

    def __init__(self, field_results: Dict = None):
        if field_results is None:
            self.field_results = {}
        else:
            self.field_results = field_results

    def to_dict(self):
        return dict((vi.field_name, vi.to_dict()) for vi in list(self.field_results.values()))


class GeneralProfiler:
    config: ConfigProfilingGeneral
    field_names: List[str]
    field_results: Dict
    spark: SparkSession
    general_profiler_result: GeneralProfilerResult = None

    def __init__(self, spark, df: DataFrame = None, config: ConfigProfilingGeneral = ConfigProfilingGeneral(),
                 dataset_config: ConfigDataset = None):
        if df is not None:
            self.df: DataFrame = df
        elif dataset_config is not None:
            select_items = ', '.join(config.columns)
            self.df = spark.sql(f'SELECT {select_items} FROM {dataset_config.name}')
        else:
            raise ValueError("Value missing error:"
                             " Must specify 1 of the following args: df or dataset_config.")

        self.spark = spark
        self.config: ConfigProfilingGeneral = config

    def run(self, return_type='dict'):
        df = self.df
        spark = self.spark

        if len(self.config.columns) < 1 or self.config.columns[0] == '*':
            self.field_names = self.df.columns
        else:
            self.field_names = self.config.columns

        if self.general_profiler_result is None:
            self.general_profiler_result = GeneralProfilerResult()
            field_results = self.general_profiler_result.field_results
            for field_name in self.field_names:
                field_result = GeneralFieldResult(field_name)

                field_result.valued_row_count = ValuedRowCountCheck(spark=self.spark, df=self.df,
                                                                    column_name=field_name).get_profile_result()
                field_result.mean_value = MeanValueCheck(spark=self.spark, df=self.df,
                                                         column_name=field_name).get_profile_result()
                field_result.stddev_value = StddevValueCheck(spark=self.spark, df=self.df,
                                                             column_name=field_name).get_profile_result()
                field_result.min_value = MinValueCheck(spark=self.spark, df=self.df,
                                                       column_name=field_name).get_profile_result()
                field_result.max_value = MaxValueCheck(spark=self.spark, df=self.df,
                                                       column_name=field_name).get_profile_result()

                field_result.zero_count = ZeroValueRowCheck(self.spark, df=df,
                                                            column_name=field_name).get_profile_result()
                field_result.null_count = NullRowCheck(self.spark, df=df, column_name=field_name).get_profile_result()
                field_result.empty_count = EmptyRowCheck(self.spark, df=df, column_name=field_name).get_profile_result()

                field_result.value_count = ValuesCountCheck(self.spark, df=df,
                                                            column_name=field_name).get_profile_result()
                field_result.top_freq_count_by_values = TopFreqCountByValuesCheck(self.spark, df=df,
                                                                                  column_name=field_name).get_profile_result()
                field_result.unique_valued_row_count = UniqueValuedRowCheck(self.spark, df=df,
                                                                            column_name=field_name).get_profile_result()
                field_result.duplicated_valued_row_count = DuplicatedValuedRowCheck(self.spark, df=df,
                                                                                    column_name=field_name).get_profile_result()
                field_results[field_name] = field_result
        else:
            field_results = self.general_profiler_result.field_results

        if return_type == 'dataframe':
            data = [vi.to_str_dict() for vi in list(field_results.values())]

            return spark.createDataFrame(data).select('field_name', 'min_value', 'max_value', 'mean_value',
                                                      'stddev_value', 'zero_count', 'null_count', 'empty_count',
                                                      'valued_row_count', 'total_row_count',
                                                      'duplicated_valued_row_count',
                                                      'unique_valued_row_count', 'value_count')
        elif return_type == 'dict':
            return self.general_profiler_result.to_dict()
        else:
            return self.general_profiler_result
