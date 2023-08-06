from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)  # immutable
class SnowflakeTable:
    created_on: datetime
    name: str
    database_name: str
    schema_name: str
    kind: str
    comment: str
    cluster_by: str
    rows: int
    bytes: int
    owner: str
    rentention_time: str # days
    automatic_clustering: str
    search_optimization: str
    is_external: str

    def qualified_name(self):
        return QualifiedTableName(self.database_name, self.schema_name, self.name)


@dataclass(frozen=True)
class SnowflakeColumn:
    table_name: str
    schema_name: str
    name: str
    data_type: Dict
    nullable: str  # aka "null?"
    default: str
    kind: str
    expression: str
    comment: str
    database_name: str
    autoincrement: str


@dataclass
class QualifiedTableName:
    database: str
    schema: str
    table: str

    def __post_init__(self):
        if not all((self.database, self.schema, self.table)):
            raise AttributeError('Database, schema, and table must be defined')
        self.database = self.database.upper()
        self.schema = self.schema.upper()
        self.table = self.table.upper()

    def __iter__(self):
        yield self.database
        yield self.schema
        yield self.table

    def __repr__(self):
        return f'{self.database}.{self.schema}.{self.table}'

    def qualified_schema(self):
        return f'{self.database}.{self.schema}'

    @staticmethod
    def of(name: str):
        return QualifiedTableName(*name.split('.'))
