import asyncio
import logging
import time
import os
from django.core.management.base import BaseCommand
from management_app.views import EventPoller
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


async def poll(polling_instance: EventPoller):
    while True:
        try:
            start_time = time.time()
            logger.info('Polling events...')
            polling_instance.store_events()
            end_time = time.time()
            logger.info(f'Polling completed in {(end_time - start_time):.2f} seconds')
        except Exception as error:
            logger.error(f'Error polling events: {error}')
        finally:
            events_timer = int(os.getenv('EVENTS_TIMER'))
            logger.info(f'Awaiting for {events_timer} seconds')
            await asyncio.sleep(events_timer)


class Command(BaseCommand):
    help = 'Starts the events polling task'

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        events_poll = EventPoller()
        loop.run_until_complete(poll(events_poll))
