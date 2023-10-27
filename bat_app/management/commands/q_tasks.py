from django.core.management.base import BaseCommand
from django_q.tasks import async_task
from bat_app.sentiment import get_sentiment

class Command(BaseCommand):
    help = 'Run Django Q task as an always-on task'

    def handle(self, *args, **options):
        async_task(get_sentiment)
