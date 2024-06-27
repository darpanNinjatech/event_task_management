from rest_framework import serializers
from .models import EventModel


class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventModel
        fields = [
            'id',
            'title',
            'start_date',
            'start_time',
            'end_date',
            'end_time',
            'min_price',
            'max_price',
            'start_date_time',
            'end_date_time',
        ]


class EventCreateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = EventModel
        fields = [
            'id',
            'base_event_id',
            'event_id',
            'title',
            'start_date_time',
            'end_date_time',
            'min_price',
            'max_price',
        ]


class QuerySerializer(serializers.Serializer):
    starts_at = serializers.DateTimeField(required=False)
    ends_at = serializers.DateTimeField(required=False)
