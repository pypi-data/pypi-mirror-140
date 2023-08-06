from os import environ as envvars
from typing import Iterator
from unittest import TestCase
from unittest.mock import PropertyMock
from unittest.mock import patch

from snowflake.connector.cursor import SnowflakeCursor

from lucious.utils import class_properties
from lucious.utils import gather
from lucious.utils import pad
from lucious.utils import snowflake_cursor
from lucious.utils import snowflake_exec


class UtilsTest(TestCase):

    def test_class_properties(self):
        class Type:
            def __init__(self, a, b):
                self.a = a
                self.b = b
        result = class_properties(Type('a', 'b'))
        self.assertDictEqual(
            dict(result),
            {'a': 'a', 'b': 'b'}
        )

    def test_pad(self):
        contents, pad_amount, padding = 'abc', 2, ''
        extension = [padding for _ in range(pad_amount)]

        iterable = list(contents)
        result = pad(iterable, pad_amount, padding)
        self.assertEqual(result, iterable + extension)

        iterator = iter(contents)
        result = pad(iterator, pad_amount, padding)
        self.assertIsInstance(result, Iterator)
        self.assertEqual(list(result), list(iter(contents)) + extension)

    def test_gather(self):
        option = '--option'
        first_value = 'a'
        second_value = 'b'
        third_value = 'c'

        arguments = (option, first_value, second_value, third_value)

        zeroth_result = gather(option, arguments, nargs=0)
        first_result = gather(option, arguments, nargs=1)
        second_result = gather(option, arguments, nargs=2)
        third_result = gather(option, arguments, nargs=3)

        self.assertEqual(zeroth_result, [option])
        self.assertEqual(first_result, [option, first_value])
        self.assertEqual(second_result, [option, first_value, second_value])
        self.assertEqual(third_result, [option, first_value, second_value, third_value])

    @patch.dict(
        envvars,
        {
            'SNOWFLAKE_ACCOUNT': 'snowflake',
            'SNOWFLAKE_USER': 'user',
            'SNOWFLAKE_PASSWORD': 'password',
            'SNOWFLAKE_ROLE': 'role',
            'SNOWFLAKE_WAREHOUSE': 'warehouse',
        },
        clear=True
    )
    @patch('snowflake.connector.connection.SnowflakeConnection.connect')
    @patch('snowflake.connector.connection.SnowflakeConnection.rest', new_callable=PropertyMock)
    def test_snowflake_cursor(self, mock_property, mock_connect):
        result = snowflake_cursor(database='database', schema='schema')
        self.assertIsInstance(result, SnowflakeCursor)

    @patch('snowflake.connector.cursor.SnowflakeCursor', autospec=True)
    def test_snowflake_exec(self, mock_cursor):
        error = RuntimeError(f'query failed.')
        def fail_query(query):
            raise error
        mock_cursor.execute.side_effect = fail_query

        query = 'SELECT this_column FROM that_table;'
        result = snowflake_exec(curs=mock_cursor, query=query, error_msg=str(error))
        self.assertIsNone(result)

        with self.assertRaises(type(error)) as ctx:
            snowflake_exec(curs=mock_cursor, query=query)