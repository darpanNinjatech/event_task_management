import logging

from django.core.cache import cache
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EventModel
from .serializers import (
    EventCreateSerializer,
    EventsSerializer,
    QuerySerializer,
)

from .events import EventClientModel, ClientModel
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)


class EventAPI(APIView):

    def get_params(self):
        starts_at = self.request.GET.get('starts_at')
        ends_at = self.request.GET.get('ends_at')
        if not all([starts_at, ends_at]):
            logger.info("Missing 'starts_at' or 'ends_at' fields")
        return starts_at, ends_at

    @swagger_auto_schema(
        query_serializer=QuerySerializer,
        responses={
            200: openapi.Response("Success response", EventsSerializer),
            400: openapi.Response("Error response"),
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            starts_at, ends_at = self.get_params()
            if starts_at and ends_at:
                event_obj = EventModel.objects.in_datetime_range(starts_at, ends_at)
            else:
                event_obj = EventModel.objects.all()
            serialized_events = EventsSerializer(event_obj, many=True)
            return Response(
                {
                    'message': 'Data fetched successfully.',
                    'status': status.HTTP_200_OK,
                    'data': {'events': serialized_events.data}
                }
            )
        except (ValueError, TypeError) as error:
            logger.error(f"Error processing request: {error}")
            raise APIException(code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    @swagger_auto_schema(auto_schema=None)
    def post(self, request, *args, **kwargs):
        request_data = request.data
        ec_erializer = EventCreateSerializer(data=request_data)
        if ec_erializer.is_valid():
            ec_erializer.save()
            return Response(ec_erializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ec_erializer.errors, status=status.HTTP_400_BAD_REQUEST)


def list_of_ids(request):
    try:
        last_data = cache.get('old_event_ids')

        if last_data:
            logger.info("Returning data from cache")
            return JsonResponse(last_data, safe=False)
        logger.info("Updating data from DB")
        event_ids = EventModel.objects.values('base_event_id', 'event_id')
        data = [
            f"{event.get('base_event_id')}:{event.get('event_id')}" for event in event_ids
        ]
        cache.set('old_event_ids', data, timeout=600)
        return JsonResponse(data, safe=False)
    except Exception as error:
        raise APIException(code=status.HTTP_400_BAD_REQUEST, detail=str(error))



class EventPoller:
    def __init__(self):
        self.log = logger
        self.log.info('Initializing event poller')
        self.events_api_url = os.getenv('EVENTS_API_URL')
        self.response_api_url = os.getenv('RESPONSE_API_URL')
        self.events_client = EventClientModel(self.events_api_url)
        self.client_model_data = ClientModel(self.response_api_url)
        self.log.info('EventModel poller initialized')

    def format_event_data(self, event: dict):
        format_data = {
            'base_event_id': event.get('base_event_id'),
            'event_id': event.get('event_id'),
            'title': event.get('title'),
            'start_date_time': event.get('event_start_date'),
            'end_date_time': event.get('event_end_date'),
            'min_price': min(event.get('prices'), default=0),
            'max_price': max(event.get('prices'), default=0),
        }
        return format_data

    def submit_event(self, event_data: dict):
        format_data = self.format_event_data(event_data)
        return self.client_model_data.add_event(format_data)

    def get_unprocessed_events(self, events):
        events_list = []
        processed_event_ids = self.client_model_data.get_processed_event_ids()
        for event in events:
            base_event_id = event.get('base_event_id')
            event_id = event.get('event_id')
            new_event_id = f"{base_event_id}:{event_id}"
            if new_event_id not in processed_event_ids:
                events_list.append(event)
                self.log.info(f"Found unprocessed event: {new_event_id}")
            else:
                self.log.info(f'EventModel {new_event_id} is already processed.')
        return events_list

    def store_events(self):
        try:
            events = self.events_client.get_events()
            unprocessed_records = self.get_unprocessed_events(events=events)
            processed_event_count = 0
            for ur_event in unprocessed_records:
                if ur_event.get('sell_mode') == 'online':
                    self.submit_event(event_data=ur_event)
                    processed_event_count += 1
                else:
                    base_event_id = ur_event.get('base_event_id')
                    event_id = ur_event.get('event_id')
                    self.log.info(
                        f'Ignoring offline event with base event id {base_event_id} and event id {event_id}'
                    )

            self.log.info(f'Processed {processed_event_count} events')
        except Exception as err:
            self.log.error(f'Error polling events: {err}')
