
from .dialect import TYPES_MAP

from sqlalchemy.engine import reflection
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2, EXECUTEMANY_VALUES, EXECUTEMANY_BATCH, EXECUTEMANY_DEFAULT
from sqlalchemy.dialects.postgresql.base import PGCompiler, PGDDLCompiler, PGDialect, PGTypeCompiler
from sqlalchemy import util
from sqlalchemy import types as sqltypes
from .compiler import (
    CrateCompiler,
    CrateTypeCompiler,
    CrateDDLCompiler
)


class CratePGCompiler(CrateCompiler, PGCompiler):
    pass


class CratePGDDLCompiler(CrateDDLCompiler, PGDDLCompiler):
    pass


class CratePGTypeCompiler(CrateTypeCompiler, PGTypeCompiler):
    pass


class CratePGDialect(PGDialect_psycopg2):
    name = 'cratepg'
    driver = 'crate-python'
    statement_compiler = CratePGCompiler
    ddl_compiler = CratePGDDLCompiler

    def __init__(
            self,
            server_side_cursors=False,
            use_native_unicode=True,
            client_encoding=None,
            use_native_hstore=True,
            use_native_uuid=True,
            executemany_mode=None,
            executemany_batch_page_size=None,
            executemany_values_page_size=None,
            use_batch_mode=None,
            **kwargs
    ):
        PGDialect.__init__(self, **kwargs)
        self.server_side_cursors = server_side_cursors
        self.use_native_unicode = use_native_unicode
        self.use_native_hstore = use_native_hstore
        self.use_native_uuid = use_native_uuid
        self.supports_unicode_binds = use_native_unicode
        self.client_encoding = client_encoding

        # Parse executemany_mode argument, allowing it to be only one of the
        # symbol names
        self.executemany_mode = util.symbol.parse_user_argument(
            executemany_mode,
            {
                EXECUTEMANY_DEFAULT: [None],
                EXECUTEMANY_BATCH: ["batch"],
                EXECUTEMANY_VALUES: ["values"],
            },
            "executemany_mode",
        )
        if use_batch_mode:
            self.executemany_mode = EXECUTEMANY_BATCH

        self.executemany_batch_page_size = executemany_batch_page_size
        self.executemany_values_page_size = executemany_values_page_size
        self.identifier_preparer.illegal_initial_characters.add('_')
        self.statement_compiler = CratePGCompiler
        self.ddl_compiler = CratePGDDLCompiler

    def initialize(self, connection):
        # get lowest server version
        self.server_version_info = \
            self._get_server_version_info(connection)
        # get default schema name
        self.default_schema_name = \
            self._get_default_schema_name(connection)

        super(PGDialect_psycopg2, self).initialize(connection)

    def do_rollback(self, connection):
        # if any exception is raised by the dbapi, sqlalchemy by default
        # attempts to do a rollback crate doesn't support rollbacks.
        # implementing this as noop seems to cause sqlalchemy to propagate the
        # original exception to the user
        pass

    def _get_default_schema_name(self, connection):
        return 'doc'

    def _get_server_version_info(self, connection):
        # return tuple(connection.connection.lowest_server_version.version)
        return tuple([4, 0, 0])

    @classmethod
    def dbapi(cls):
        import psycopg2Crate

        return psycopg2Crate

    @classmethod
    def _psycopg2_extensions(cls):
        from psycopg2Crate import extensions

        return extensions

    @classmethod
    def _psycopg2_extras(cls):
        from psycopg2Crate import extras

        return extras

    def has_schema(self, connection, schema):
        return schema in self.get_schema_names(connection)

    def has_table(self, connection, table_name, schema=None):
        return table_name in self.get_table_names(connection, schema=schema)

    @reflection.cache
    def get_schema_names(self, connection, **kw):
        query = (
                f"""
                    select schema_name
                    from information_schema.schemata
                    order by schema_name asc"""
        )
        cursor = connection.execute(query)
        return [row[0] for row in cursor.fetchall()]

    @reflection.cache
    def get_table_names(self, connection, schema=None, **kw):
        schema = schema if schema is not None else self.default_schema_name
        query = (
            f"""
                SELECT table_name FROM information_schema.tables
                WHERE {self.schema_column} = '{schema}'  AND table_type = 'BASE TABLE'
                ORDER BY table_name ASC, {self.schema_column} ASC
            """
        )
        cursor = connection.execute(query)
        return [row[0] for row in cursor.fetchall()]

    @reflection.cache
    def get_columns(self, connection, table_name, schema=None, **kw):
        schema = schema if schema is not None else self.default_schema_name
        query = (
                f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}' AND {self.schema_column} = '{schema}'
                """
        )
        cursor = connection.execute(query)
        return [self._create_column_info(row) for row in cursor.fetchall()]

    @reflection.cache
    def get_pk_constraint(self, engine, table_name, schema=None, **kw):
        schema = schema if schema is not None else self.default_schema_name
        query = (
                f"""
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_name = '{table_name}' AND {self.schema_column} = '{schema}'
                AND constraint_type='PRIMARY_KEY'
                """
        )

        def result_fun(result):
            rows = result.fetchone()
            return set(rows[0] if rows else [])

        pk_result = engine.execute(
            query,
            [table_name, schema or self.default_schema_name]
        )
        pks = result_fun(pk_result)
        return {'constrained_columns': pks,
                'name': 'PRIMARY KEY'}

    @reflection.cache
    def get_check_constraints(self, connection, table_name, schema=None, **kw):
        return []

    @reflection.cache
    def get_foreign_keys(self, connection, table_name, schema=None,
                         postgresql_ignore_search_path=False, **kw):
        # Crate doesn't support Foreign Keys, so this stays empty
        return []

    @reflection.cache
    def get_indexes(self, connection, table_name, schema, **kw):
        return []

    @property
    def schema_column(self):
        return "table_schema"

    def _create_column_info(self, row):
        return {
            'name': row[0],
            'type': self._resolve_type(row[1]),
            # In Crate every column is nullable except PK
            # Primary Key Constraints are not nullable anyway, no matter what
            # we return here, so it's fine to return always `True`
            'nullable': True
        }

    def _resolve_type(self, type_):
        return TYPES_MAP.get(type_, sqltypes.UserDefinedType)


