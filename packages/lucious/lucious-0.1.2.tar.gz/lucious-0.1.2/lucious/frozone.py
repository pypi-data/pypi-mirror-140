from typing import Union

from actionpack.actions import Call
from actionpack.actions import Pipeline
from actionpack.actions import Write
from actionpack.utils import Closure
from snowflake.connector.cursor import SnowflakeCursor

from lucious.types import QualifiedTableName
from lucious.types import SnowflakeColumn
from lucious.types import SnowflakeTable
from lucious.utils import render_columns
from lucious.utils import snowflake_exec


def fetch_tables(curs: SnowflakeCursor, database: str, schema: str, ignore_hidden: bool = False):
    query = f'show tables in {database}.{schema};'
    for answer in fetch_answers(curs, query):
        table = SnowflakeTable(*answer)
        if ignore_hidden and table.name.startswith('_'):
            continue
        yield table


def fetch_columns(
    curs: SnowflakeCursor,
    table: Union[SnowflakeTable, QualifiedTableName],
    ignore_hidden: bool = False
):
    if isinstance(table, SnowflakeTable):
        query = f'show columns in {table.qualified_name()};'
    elif isinstance(table, QualifiedTableName):
        query = f'show columns in {table};'
    else:
        raise TypeError('Table must be a SnowflakeTable or QualifiedTableName')

    for answer in fetch_answers(curs, query):
        column = SnowflakeColumn(*answer)
        if ignore_hidden and column.name.startswith('_'):
            continue
        yield column


def fetch_answers(curs: SnowflakeCursor, query: str):
    curs = snowflake_exec(curs, query, f'\n  -> Query failed: {query}')
    return curs.fetchall() if curs else []


def fetch_columns_then_write(
    curs: SnowflakeCursor,
    table: Union[SnowflakeTable, QualifiedTableName],
    outfilename: str,
    ignore_hidden_columns: bool = False
) -> Pipeline:
    if isinstance(table, SnowflakeTable):
        qualified_table_name = QualifiedTableName.of(table.qualified_name())
    elif isinstance(table, QualifiedTableName):
        qualified_table_name = table
    else:
        raise TypeError('Table must be a SnowflakeTable or QualifiedTableName')

    call = Call(Closure(fetch_columns, curs, table, ignore_hidden_columns))
    format_answer = Pipeline.Fitting(
        action=Call,
        enclose=render_columns,
    )
    write = Pipeline.Fitting(
        action=Write,
        **{
            'overwrite': True,
            'mkdir': True,
            'filename': outfilename,
            'to_write': Pipeline.Receiver
        },
    )
    return Pipeline(call, format_answer, write).set(name=qualified_table_name)
