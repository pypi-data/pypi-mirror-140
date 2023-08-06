import os
import subprocess

from django.db.backends.postgresql.base import DatabaseWrapper as PostgresqlDatabaseWrapper
from django.db.backends.postgresql.creation import DatabaseCreation as PostgresqlDatabaseCreation


class DatabaseCreation(PostgresqlDatabaseCreation):

    """Database creation class."""

    test_db_template_path = None

    def _create_test_db(self, *args, **kwargs):
        test_database_name = super()._create_test_db(*args, **kwargs)
        if self.test_db_template_path:
            with open(self.test_db_template_path) as db_template:
                with open(os.devnull, 'wb') as devnull:
                    psql = subprocess.Popen(['psql', test_database_name], stdin=db_template, stdout=devnull)
            psql.wait()
        return test_database_name


class DatabaseWrapper(PostgresqlDatabaseWrapper):

    """Database wrapper class."""

    creation_class = DatabaseCreation
