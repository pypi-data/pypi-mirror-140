from django.conf import settings

CAN_RUN_TESTS = settings.CAN_RUN_TESTS
SQL_DUMP_FILE_FOR_TESTS = getattr(settings, 'SQL_DUMP_FILE_FOR_TESTS', None)
