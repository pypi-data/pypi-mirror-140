import inspect

from functools import reduce
from itertools import chain
from pathlib import Path
from os import environ as envvars
from string import Template
from typing import Iterable
from typing import Iterator
from typing import Optional

from snowflake.connector import connect
from snowflake.connector.cursor import SnowflakeCursor

from lucious.types import SnowflakeColumn
from lucious.types import SnowflakeTable


projectroot = Path(__file__).parent.parent.resolve()

def class_properties(cls: type, include_hidden: bool = False):
    properties = inspect.getmembers(cls, lambda attribute: not(inspect.isroutine(attribute)))
    for property in properties:
        if not include_hidden and property[0].startswith('_'):
            pass
        else:
            yield property


def pad(iterable: Iterable, length: int = 0, padding=None):
    extension = [padding] * length
    if not isinstance(iterable, Iterator) and isinstance(iterable, Iterable):
        to_pad = [elm for elm in iterable]
        to_pad.extend(extension)
        return type(iterable)(to_pad)
    elif isinstance(iterable, Iterator) and isinstance(iterable, Iterable):
        return chain((elm for elm in iterable), extension)


def gather(option, arguments: Iterable, nargs: int = 0) -> Iterable[str]:
    arguments = list(arguments)
    if option in arguments:
        option_index = arguments.index(option)
        return arguments[option_index:option_index + (nargs + 1)]
    else:
        return []


def snowflake_cursor(database: str, schema: str) -> SnowflakeCursor:
    conn = connect(
        account=envvars.get('SNOWFLAKE_ACCOUNT'),  # https://<account>.snowflakecomputing.com/
        user=envvars.get('SNOWFLAKE_USER'),
        password=envvars.get('SNOWFLAKE_PASSWORD'),
        role=envvars.get('SNOWFLAKE_ROLE'),
        warehouse=envvars.get('SNOWFLAKE_WAREHOUSE'),
        database=database,
        schema=schema,
    )
    return conn.cursor()


def snowflake_exec(
    curs: SnowflakeCursor,
    query: str,
    error_msg: Optional[str] = None
) -> Optional[SnowflakeCursor]:
    try:
        return curs.execute(query)
    except Exception as e:
        if error_msg:
            print(error_msg)
        else:
            raise e


def interpolate(query: Template, qualified_table_name: str) -> str:
    return query.substitute(qualified_table_name=qualified_table_name)


def generate_table_queries(template: Template, tables: Iterable[SnowflakeTable]):
    for table in tables:
        qualified_table_name = table.qualified_name()
        yield qualified_table_name, interpolate(query=template, qualified_table_name=qualified_table_name)


def render_columns(columns: Iterable[SnowflakeColumn], delimiter: str = '\n') -> Iterator[str]:
    columns_names = [column.name for column in columns]
    return reduce(lambda a, b: a + f'{delimiter}{b}', columns_names)
