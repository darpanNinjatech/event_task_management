from uuid import uuid4

from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete
from django.dispatch import receiver


class EventManager(models.QuerySet):
    def in_datetime_range(self, start_datetime, end_datetime):
        return self.filter(
            Q(start_date_time__gte=start_datetime) & Q(end_date_time__lte=end_datetime)
        )

class EventModel(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    base_event_id = models.CharField(verbose_name="base event id",max_length=10)
    event_id = models.CharField(verbose_name="event id",max_length=10)
    title = models.CharField(verbose_name="title",max_length=255)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    start_date = models.DateField(verbose_name="start date",null=True, blank=True)
    start_time = models.TimeField(verbose_name="start time",null=True, blank=True)
    end_date = models.DateField(verbose_name="end date",null=True, blank=True)
    end_time = models.TimeField(verbose_name="end time",null=True, blank=True)
    min_price = models.FloatField(verbose_name="min price",default=0)
    max_price = models.FloatField(verbose_name="max price",default=0)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    objects = EventManager.as_manager()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.start_date_time:
            self.start_date = self.start_date_time.date()
            self.start_time = self.start_date_time.time()
        if self.end_date_time:
            self.end_date = self.end_date_time.date()
            self.end_time = self.end_date_time.time()
        cache.delete('old_event_ids')
        super(EventModel, self).save(*args, **kwargs)


@receiver(post_delete, sender=EventModel)
def clear_cache_on_delete(sender, instance, **kwargs):
    cache.delete('old_event_ids')
