from contextlib import contextmanager

import psycopg2
import time
from typing import List, Optional, Tuple, Any, Iterable, Dict, Union
from dbt.contracts.connection import (
    Connection, ConnectionState, AdapterResponse
)
import dbt.exceptions
from dbt.adapters.base import Credentials
from dbt.adapters.sql import SQLConnectionManager
from dbt.contracts.connection import AdapterResponse
from dbt.logger import GLOBAL_LOGGER as logger

from dbt.helper_types import Port
from dataclasses import dataclass
from typing import Optional


@dataclass
class CratedbAdapterCredentials(Credentials):
    host: str
    user: str
    port: Port
    password: str  # on postgres the password is mandatory

    _ALIASES = {
        'dbname': 'database',
        'pass': 'password'
    }

    @property
    def type(self):
        return 'cratedbadapter'

    def _connection_keys(self):
        # return an iterator of keys to pretty-print in 'dbt debug'.
        # Omit fields like 'password'!
        return ('host', 'port', 'user', 'schema')


class CratedbAdapterConnectionManager(SQLConnectionManager):
    TYPE = 'cratedbadapter'

    def add_query(
        self,
        sql: str,
        auto_begin: bool = False,
        bindings: Optional[Any] = None,
        abridge_sql_log: bool = False
    ) -> Tuple[Connection, Any]:
        connection = self.get_thread_connection()
        sql=sql.replace('"".','')
        sql = sql.replace(' cascade', '')
        sql = sql.replace(' limit 100;', '')
        #print("...")
        #print(sql)
        #print("...")
        if auto_begin and connection.transaction_open is False:
            self.begin()

        logger.debug('Using {} connection "{}".'
                     .format(self.TYPE, connection.name))

        with self.exception_handler(sql):
            if abridge_sql_log:
                log_sql = '{}...'.format(sql[:512])
            else:
                log_sql = sql

            logger.debug(
                'On {connection_name}: {sql}',
                connection_name=connection.name,
                sql=log_sql,
            )
            pre = time.time()

            cursor = connection.handle.cursor()
            cursor.execute(sql, bindings)
            logger.debug(
                "SQL status: {status} in {elapsed:0.2f} seconds",
                status=self.get_response(cursor),
                elapsed=(time.time() - pre)
            )

            return connection, cursor

    @classmethod
    def open(cls, connection):
        if connection.state == 'open':
            logger.debug('Connection is already open, skipping open.')
            return connection

        credentials = cls.get_credentials(connection.credentials)

        try:
            handle = psycopg2.connect(
                dbname="",
                user=credentials.user,
                host=credentials.host,
                password=credentials.password,
                port=credentials.port,
                connect_timeout=10)
            connection.handle = handle
        except psycopg2.Error as e:
            logger.debug("Got an error when attempting to open a cratedb "
                         "connection: '{}'"
                         .format(e))
            connection.handle = None
            connection.state = 'fail'
            raise dbt.exceptions.FailedToConnectException(str(e))
        return connection

    def cancel(self, connection):
        connection_name = connection.name
        try:
            pid = connection.handle.get_backend_pid()
        except psycopg2.InterfaceError as exc:
            # if the connection is already closed, not much to cancel!
            if 'already closed' in str(exc):
                logger.debug(
                    f'Connection {connection_name} was already closed'
                )
                return
            # probably bad, re-raise it
            raise

        sql = "select pg_terminate_backend({})".format(pid)

        logger.debug("Cancelling query '{}' ({})".format(connection_name, pid))

        _, cursor = self.add_query(sql)
        res = cursor.fetchone()

        logger.debug("Cancel query '{}': {}".format(connection_name, res))

    @classmethod
    def get_credentials(cls, credentials):
        return credentials

    @classmethod
    def get_response(cls, cursor) -> AdapterResponse:
        message = str(cursor.statusmessage)
        rows = cursor.rowcount
        status_message_parts = message.split() if message is not None else []
        status_messsage_strings = [
            part
            for part in status_message_parts
            if not part.isdigit()
        ]
        code = ' '.join(status_messsage_strings)
        return AdapterResponse(
            _message=message,
            code=code,
            rows_affected=rows
        )

    @contextmanager
    def exception_handler(self, sql):
        try:
            yield

        except psycopg2.DatabaseError as e:
            logger.debug('Postgres error: {}'.format(str(e)))

            try:
                self.rollback_if_open()
            except psycopg2.Error:
                logger.debug("Failed to release connection!")
                pass

            raise dbt.exceptions.DatabaseException(str(e).strip()) from e

        except Exception as e:
            logger.debug("Error running SQL: {}", sql)
            logger.debug("Rolling back transaction.")
            self.rollback_if_open()
            if isinstance(e, dbt.exceptions.RuntimeException):
                # during a sql query, an internal to dbt exception was raised.
                # this sounds a lot like a signal handler and probably has
                # useful information, so raise it without modification.
                raise

            raise dbt.exceptions.RuntimeException(e) from e