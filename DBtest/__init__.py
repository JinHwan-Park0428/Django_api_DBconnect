import time

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Command(BaseCommand):
    help = "Automatically calls collectstatic when the staticfiles get modified."

    def handle(self, *args, **options):
        event_handler = CollectstaticEventHandler()
        observer = Observer()
        for path in settings.STATICFILES_DIRS:
            observer.schedule(event_handler, path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()


class CollectstaticEventHandler(FileSystemEventHandler):
    def on_moved(self, event):
        super().on_moved(event)
        self._collectstatic()

    def on_created(self, event):
        super().on_created(event)
        self._collectstatic()

    def on_deleted(self, event):
        super().on_deleted(event)
        self._collectstatic()

    def on_modified(self, event):
        super().on_modified(event)
        self._collectstatic()

    def _collectstatic(self):
        call_command("collectstatic", interactive=False)