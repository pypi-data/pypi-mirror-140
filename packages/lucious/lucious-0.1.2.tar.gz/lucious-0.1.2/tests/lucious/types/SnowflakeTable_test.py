from datetime import datetime
from datetime import timezone
from unittest import TestCase

from lucious.types import QualifiedTableName
from lucious.types import SnowflakeTable
from lucious.utils import class_properties


class SnowflakeTableTest(TestCase):

    table_name, database_name, schema_name = 'NAME', 'DATABASE_NAME', 'SCHEMA_NAME'

    table_data = (
        datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
        table_name,
        database_name,
        schema_name,
        'kind',
        'comment',
        'cluster_by',
        100,  # rows
        100,  # bytes
        'owner',
        'retention_time',
        'automatic_clustering',
        'search_optimization',
        'is_internal'
    )
    
    def test_can_instantiate(self):
        result = SnowflakeTable(*self.table_data)
        actual_property = dict(class_properties(result))
        self.assertSetEqual(
            set(actual_property.values()),
            set(self.table_data)
        )
    
    def test_can_produce_qualified_name(self):
        result = SnowflakeTable(*self.table_data)
        actual_qualified_name = result.qualified_name()
        self.assertIsInstance(actual_qualified_name, QualifiedTableName)
        self.assertEqual(
            repr(actual_qualified_name),
            f'{self.database_name}.{self.schema_name}.{self.table_name}'
        )
        