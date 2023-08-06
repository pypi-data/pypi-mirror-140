from unittest import TestCase

from lucious.types import SnowflakeColumn
from lucious.utils import class_properties


class SnowflakeColumnTest(TestCase):

    data_type = {
        "type": "TEXT",
        "length": 16777216,  # 24-bit "SWORD"
        "byteLength": 16777216,  # 24-bit "SWORD"
        "nullable": True,
        "fixed": False
    }

    column_data = (
        'TABLE_NAME',
        'SCHEMA_NAME',
        'NAME',
        f'{data_type}',
        'nullable',
        'default',
        'KIND',
        'expression',
        'comment',
        'database_name',
        'autoincrement'
    )
    
    def test_can_instantiate(self):
        result = SnowflakeColumn(*self.column_data)
        actual_property = dict(class_properties(result))
        self.assertSetEqual(
            set(actual_property.values()),
            set(self.column_data)
        )
