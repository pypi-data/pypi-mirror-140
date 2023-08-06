from typing import Iterable
from typing import Iterator
from unittest import TestCase

from lucious.types import QualifiedTableName


class QualifiedTableNameTest(TestCase):

    qualified_table_name = 'database.schema.table'
    qualified_table_name_list = qualified_table_name.split('.')

    def setUp(self) -> None:
        self.QualifiedTableName = QualifiedTableName(*self.qualified_table_name_list)
        self.expected_database, self.expected_schema, self.expected_table = self.qualified_table_name_list

    def test_can_instantiate(self):
        result = self.QualifiedTableName
        self.assertIsInstance(result, QualifiedTableName)
        self.assertEqual(result.database, self.expected_database.upper())
        self.assertEqual(result.schema, self.expected_schema.upper())
        self.assertEqual(result.table, self.expected_table.upper())

    def test_can_create_from_string(self):
        result = QualifiedTableName.of(self.qualified_table_name)
        self.assertIsInstance(result, QualifiedTableName)

    def test_can_get_qualified_schema_name(self):
        result = self.QualifiedTableName
        expected_qualified_schema = f'{self.expected_database.upper()}.{self.expected_schema.upper()}'
        self.assertIsInstance(result, QualifiedTableName)
        self.assertEqual(result.qualified_schema(), expected_qualified_schema)

    def test_can_render_as_iterable(self):
        result = self.QualifiedTableName
        self.assertIsInstance(iter(result), Iterator)
        self.assertIsInstance(list(result), Iterable)

