# spark-profiling

[![CI Build](https://github.com/tw-data-quality-2022/spark-profiling/actions/workflows/python-package.yml/badge.svg)
](https://github.com/tw-data-quality-2022/spark-profiling/actions/workflows/python-package.yml)

## Requirements

- Java 8+
- Apache Spark 3.0+

## Usage

### Installation

```shell
pip install --upgrade data-quality-check
```

### Use GeneralProfiler

```python
from pyspark.sql import SparkSession
from data_quality_check.config import ConfigDataset
from data_quality_check.profiler.general_profiler import GeneralProfiler

spark = SparkSession.builder.appName("SparkProfilingApp").enableHiveSupport().getOrCreate()
data = [{'name': 'Alice', 'age': 1, 'gender': 'female', 'is_new': True},
        {'name': 'Tom', 'age': 10, 'gender': 'male', 'is_new': False}]

# Run general check on spark df
df = spark.createDataFrame(data)
result_df = GeneralProfiler(spark, df=df).run(return_type='dataframe')
result_df.show()

# Run general check on spark/hive table
df.createOrReplaceTempView('my_table')
result_df = GeneralProfiler(spark, dataset_config=ConfigDataset(name='my_table')).run(return_type='dataframe')
result_df.show()
```

### Use CustomizedProfiler

```python
import json

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType
from data_quality_check.config import Config, ConfigDataset, ConfigProfilingCustomized
from data_quality_check.profiler.customized_profiler import CustomizedProfiler

# Initialize spark
spark = SparkSession.builder.appName("SparkProfilingApp").enableHiveSupport().getOrCreate()
dept = [("Finance", 1),
        ("Marketing", 2),
        ("Sales", 3),
        ("IT", 4)]
deptSchema = StructType([StructField('dept_name', StringType(), True),
                         StructField('dept_id', LongType(), True)])
spark.createDataFrame(data=dept, schema=deptSchema).createOrReplaceTempView('dept')
print('dept table:')
spark.table('dept').show(truncate=False)

employee = [(1, "Amy", 1, 'male', 1000, 'amy@example.com'),
            (2, "Caro", 2, 'male', 1000, 'caro@example.com'),
            (3, "Mark", 3, 'Error', 2000, 'unknown'),
            (4, "Timi", 4, 'female', 2000, None),
            (5, "Tata", 5, 'unknown', 3000, 'bad email address'),
            (6, "Zolo", None, None, 3000, 'my-C0omplicated_EMAIL@A.ddress.xyz')]
employeeSchema = StructType([StructField('uid', LongType(), True),
                             StructField('name', StringType(), True),
                             StructField('dept_id', LongType(), True),
                             StructField('gender', StringType(), True),
                             StructField('income', LongType(), True),
                             StructField('email', StringType(), True)])
spark.createDataFrame(data=employee, schema=employeeSchema).createOrReplaceTempView('employee')
print('employee table:')
spark.table('employee').show(truncate=False)

# Specify the configuration of customized profiler
customized_config_dict = {
    'code_check': [
        {'column': 'gender', 'codes': ['male', 'female', 'unknown']}
    ],
    'key_mapping_check': [
        {'column': 'dept_id', 'target_table': 'dept', 'target_column': 'dept_id'}
    ]
}

customized_config = ConfigProfilingCustomized.parse_obj(customized_config_dict)
dataset_config = ConfigDataset.parse_obj({'name': 'employee'})

# Initialize CustomizedProfiler with configuration
customized_profiler = CustomizedProfiler(spark,
                                         dataset_config=dataset_config,
                                         customized_profiling_config=customized_config)

result = customized_profiler.run(return_type='dict')
print(json.dumps(result, indent=' ', ensure_ascii=False, allow_nan=True))
```

## Development

### Dependencies

| Filename | Requirements|
|----------|-------------|
| requirements.txt | Package requirements|
| requirements-dev.txt |  Requirements for development|

### Test

```shell
PYTHONPATH=./src pytest tests/*
```

### Build

```
python setup.py sdist bdist_wheel
twine check dist/*
```

### Publish

```
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
twine upload dist/*
```


