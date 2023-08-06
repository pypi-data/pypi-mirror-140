from django.core.management.commands.test import Command as TestCommand

from fancy_test_runners import settings


class Command(TestCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--db-template',
            nargs='?',
            action='store',
            dest='db_template_path',
            default=None,
            const=settings.SQL_DUMP_FILE_FOR_TESTS,
            help='A SQL dump file that will be loaded before running migrations',
        )

    def handle(self, *test_labels, **options):
        if settings.CAN_RUN_TESTS:
            super().handle(*test_labels, **options)
        else:
            raise Exception('You shall not run tests in this environment!')
