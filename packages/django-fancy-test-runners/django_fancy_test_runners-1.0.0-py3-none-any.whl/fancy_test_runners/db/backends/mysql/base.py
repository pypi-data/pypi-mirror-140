import os
import subprocess

from django.db.backends.mysql.base import DatabaseWrapper as MysqlDatabaseWrapper
from django.db.backends.mysql.creation import DatabaseCreation as MysqlDatabaseCreation


class DatabaseCreation(MysqlDatabaseCreation):

    """Database creation class."""

    test_db_template_path = None

    def _create_test_db(self, *args, **kwargs):
        test_database_name = super()._create_test_db(*args, **kwargs)
        if self.test_db_template_path:
            db_settings = self.connection.settings_dict
            db_settings.update(self.connection.settings_dict.get('TEST', {}))
            with open(self.test_db_template_path) as db_template:
                with open(os.devnull, 'wb') as devnull:
                    mysql = subprocess.Popen([
                        'mysql',
                        '-u%s' % db_settings['USER'],
                        '-p%s' % db_settings['PASSWORD'],
                        '-h%s' % db_settings['HOST'],
                        '-P%s' % db_settings['PORT'],
                        test_database_name], stdin=db_template, stdout=devnull)
            mysql.wait()
        return test_database_name


class DatabaseWrapper(MysqlDatabaseWrapper):

    """Database wrapper class."""

    creation_class = DatabaseCreation
