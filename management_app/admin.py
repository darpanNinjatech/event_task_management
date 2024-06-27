from django.contrib import admin
from .models import EventModel


@admin.register(EventModel)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'base_event_id',
        'event_id',
        'start_date_time',
        'end_date_time',
    ]
