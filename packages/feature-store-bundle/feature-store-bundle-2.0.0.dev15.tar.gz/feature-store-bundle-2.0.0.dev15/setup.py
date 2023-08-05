# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['featurestorebundle',
 'featurestorebundle.checkpoint',
 'featurestorebundle.databricks.feature.reader',
 'featurestorebundle.databricks.feature.writer',
 'featurestorebundle.db',
 'featurestorebundle.delta',
 'featurestorebundle.delta.feature',
 'featurestorebundle.delta.feature.reader',
 'featurestorebundle.delta.feature.writer',
 'featurestorebundle.delta.metadata',
 'featurestorebundle.delta.metadata.reader',
 'featurestorebundle.delta.metadata.writer',
 'featurestorebundle.delta.target',
 'featurestorebundle.delta.target.reader',
 'featurestorebundle.entity',
 'featurestorebundle.feature',
 'featurestorebundle.feature.reader',
 'featurestorebundle.feature.writer',
 'featurestorebundle.metadata',
 'featurestorebundle.metadata.reader',
 'featurestorebundle.metadata.writer',
 'featurestorebundle.notebook',
 'featurestorebundle.notebook.decorator',
 'featurestorebundle.notebook.decorator.tests',
 'featurestorebundle.notebook.functions',
 'featurestorebundle.notebook.services',
 'featurestorebundle.notebook.tests',
 'featurestorebundle.orchestration',
 'featurestorebundle.target.reader',
 'featurestorebundle.test',
 'featurestorebundle.widgets']

package_data = \
{'': ['*'], 'featurestorebundle': ['_config/*']}

install_requires = \
['daipe-core>=1.4.2,<2.0.0',
 'databricks-bundle>=1.4.3,<2.0.0',
 'pyfony-bundles>=0.4.4,<0.5.0']

entry_points = \
{'pyfony.bundle': ['create = '
                   'featurestorebundle.FeatureStoreBundle:FeatureStoreBundle']}

setup_kwargs = {
    'name': 'feature-store-bundle',
    'version': '2.0.0.dev15',
    'description': 'Feature Store for the Daipe AI Platform',
    'long_description': '# Feature Store bundle\n\n**This package is distributed under the "DataSentics SW packages Terms of Use." See [license](https://raw.githubusercontent.com/daipe-ai/feature-store-bundle/master/LICENSE)**\n\nFeature store bundle allows you to store features with metadata.\n\n# Installation\n\n```bash\npoetry add feature-store-bundle\n```\n\n# Getting started\n\n\n1. Define entity and custom `feature decorator`\n\n```python\nfrom featurestorebundle.entity.getter import get_entity\nfrom featurestorebundle.feature.FeaturesStorage import FeaturesStorage\nfrom featurestorebundle.notebook.decorator import feature_decorator_factory\n\nentity = get_entity()\nfeatures_storage = FeaturesStorage(entity)\n\nfeature_decorator = feature_decorator_factory.create(entity, features_storage)\n```\n\n2. Use the `feature decorator` to save features as you create them\n\n```python\nimport daipe as dp\n\nfrom pyspark.sql import functions as f\nfrom pyspark.sql import DataFrame\n\n@dp.transformation(dp.read_table("silver.tbl_loans"), display=True)\n@feature_decorator(\n    ("Age", "Client\'s age"),\n    ("Gender", "Client\'s gender"),\n    ("WorkExperience", "Client\'s work experience"),\n    category="personal",\n)\ndef client_personal_features(df: DataFrame):\n    return (\n        df.select("UserName", "Age", "Gender", "WorkExperience")\n        .groupBy("UserName")\n        .agg(\n            f.max("Age").alias("Age"),\n            f.first("Gender").alias("Gender"),\n            f.first("WorkExperience").alias("WorkExperience"),\n        )\n        .withColumn("timestamp", f.lit(today))\n    )\n```\n\n3. Write/Merge all features in one go\n\n```python\nimport daipe as dp\nfrom featurestorebundle.feature.writer.FeaturesWriter import FeaturesWriter\n\n@dp.notebook_function()\ndef write_features(writer: FeaturesWriter):\n    writer.write(features_storage)\n```\n',
    'author': 'Datasentics',
    'author_email': 'jiri.koutny@datasentics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/daipe-ai/feature-store-bundle',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
