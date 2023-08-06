from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from lucious.frozone import fetch_answers


class FrozoneTest(TestCase):

    @patch('snowflake.connector.cursor.SnowflakeCursor', autospec=True)
    def test_fetch_answers(self, mock_cursor):
        query = 'SELECT this_column FROM that_table;'
        some_data = [('SOME', 'DATA')]

        can_fetch = MagicMock()
        can_fetch.fetchall.return_value = some_data
        mock_cursor.execute.side_effect = [can_fetch, None]

        result = fetch_answers(curs=mock_cursor, query=query)
        self.assertEqual(result, some_data)

        result = fetch_answers(curs=mock_cursor, query=query)
        self.assertEqual(result, [])
