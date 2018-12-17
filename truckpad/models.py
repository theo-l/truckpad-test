#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Creation: 12/14/18 5:34 PM
@Author: liang
@File: models.py
"""
import json
import uuid
from datetime import timedelta

from django.db import models
from django.db.models import Q, F, DateField, DateTimeField, ForeignKey
from django.utils import timezone

TRUCK_TYPES = (
    (1, 'Caminhão 3/4'),
    (2, 'Caminhão Toco'),
    (3, 'Caminhão Truck'),
    (4, 'Caminhão Simples'),
    (5, 'Caminhão Eixo Extendido'),

)

GENDERS = (
    (0, 'Secret'),
    (1, 'Male'),
    (2, 'Female')
)


def get_truck_type_description(truck_type):
    """
    Used to get truck_type's corresponding description text
    """
    for ty in TRUCK_TYPES:
        if ty[0] == truck_type:
            return ty[1]
    return 'Unknown'


def gen_uuid() -> str:
    return str(uuid.uuid4())


class BaseModel(models.Model):
    object_id = models.UUIDField(primary_key=True, default=gen_uuid, editable=False)
    created_at = models.DateTimeField(verbose_name='Create time', auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(verbose_name='Update time', auto_now=True, null=True, editable=False)

    class Meta:
        abstract = True

    def to_dict(self, includes=None, excludes=None, json_fields=None, dehydrate_fields=None):
        """
        将model实力转化为dict数据对象
        :includes 指定需要转换的特定的字段
        :excludes 指定不需要转换的字段, includes 具有更高的优先级
        :json_fields 指定字段存储为json的字段, 用来反序列化json字段为dict对象
        :dehydrate_fields 指定可以反序列化的外键对象字段
        """

        model_field_names = {field.name for field in self._meta.fields}
        includes = set(includes or {})
        excludes = set(excludes or {})
        process_fields = includes if includes else model_field_names - excludes
        json_fields = set(json_fields or {})
        dehydrate_fields = set(dehydrate_fields or {})

        data = {}
        for field in self._meta.fields:
            field_name, field_value = field.name, getattr(self, field.name, None)

            if field_name in process_fields:
                if field_name in json_fields:
                    data[field_name] = json.loads(field_value or '{}')
                elif isinstance(field, ForeignKey):
                    if field_name in dehydrate_fields:
                        data[field_name] = field_value.to_dict()
                    else:
                        data[field_name] = str(field_value.pk)
                elif isinstance(field, (DateTimeField, DateField)):
                    data[field_name] = None if not field_value else int(field_value.timestamp())
                else:
                    data[field_name] = field_value
        return data


class Terminal(BaseModel):
    name = models.CharField(max_length=50, verbose_name='Name')
    latitude = models.FloatField(verbose_name='Latitude')
    longitude = models.FloatField(verbose_name='Longitude')

    class Meta:
        verbose_name = 'Terminal'
        verbose_name_plural = 'Terminals'

    def __str__(self):
        return '<Terminal: {}>'.format(self.name)


class Driver(BaseModel):
    cpf_no = models.CharField(max_length=30, unique=True, verbose_name='CPF Number')
    name = models.CharField(max_length=100, default='', verbose_name='Name')
    age = models.IntegerField(null=True, verbose_name='Age')
    gender = models.IntegerField(choices=GENDERS, default=0, verbose_name='Gender')
    drive_license_type = models.CharField(max_length=10, null=True, verbose_name='CNH Type')
    has_truck = models.BooleanField(default=False, verbose_name='Has Truck')
    from_terminal = models.ForeignKey(Terminal, related_name='exit_drivers', verbose_name='Source Terminal')
    to_terminal = models.ForeignKey(Terminal, related_name='enter_drivers', verbose_name='Destination Terminal')

    class Meta:
        verbose_name = 'Truck Driver'
        verbose_name_plural = 'Truck Drivers'

    def __str__(self):
        return '<Driver: {}-{}>'.format(self.name, self.cpf_no)

    @classmethod
    def query_number_of_drivers_who_own_truck(cls):
        """
        check the driver who has their own truck
        """
        return cls.objects.filter(has_truck=True).count()

    def update_registration_info(self, **kwargs):
        """
        Update driver's registration information
        """
        editable_fields = ['name', 'age', 'gender', 'drive_license_type', 'has_truck', 'from_terminal', 'to_terminal']
        for key in kwargs:
            if key in editable_fields:
                if getattr(self, key) != kwargs[key]:
                    setattr(self, key, kwargs[key])

        self.save()
        self.refresh_from_db()
        return self


class Truck(BaseModel):
    number = models.CharField(max_length=20, unique=True, verbose_name='Truck number')
    truck_type = models.IntegerField(choices=TRUCK_TYPES, verbose_name='Truck type')

    class Meta:
        verbose_name_plural = 'Trucks'
        verbose_name = 'Truck'

    def __str__(self):
        return '<Truck: {}-{}>'.format(self.number, self.get_truck_type_display())


class Registration(BaseModel):
    driver = models.ForeignKey(Driver, related_name='entrances', verbose_name='Driver')
    truck = models.ForeignKey(Truck, related_name='entrances', verbose_name='Truck')
    from_terminal = models.ForeignKey(Terminal, related_name='exit_registrations', verbose_name='From Terminal')
    to_terminal = models.ForeignKey(Terminal, related_name='enter_registrations', verbose_name='To Terminal')
    is_loaded = models.BooleanField(default=True, verbose_name='Is Truck Enter loaded?')

    class Meta:
        verbose_name = 'Entrance Registration'
        verbose_name_plural = 'Entrance Registrations'

    def __str__(self):
        return '<Registration: {} ----> {})>'.format(self.driver, self.to_terminal)

    @classmethod
    def register(cls, driver, truck, is_loaded, from_terminal, to_terminal):
        """
        1. register information of every arriving truck & driver
        """
        record = cls.objects.create(driver=driver, truck=truck, is_loaded=is_loaded, from_terminal=from_terminal,
                                    to_terminal=to_terminal)
        return record

    @classmethod
    def query_loaded_truck_traffic_of_terminal_by_date_period(cls, start_date=None, end_date=None, terminal=None):
        """
        date period can be one day, one week or one month
        """
        start_date = start_date or timezone.now().date()
        end_date = end_date or start_date + timedelta(days=1)
        query = Q(is_loaded=True) & Q(created_at__range=[start_date, end_date])
        if terminal is not None:
            query &= Q(to_terminal=terminal)

        return cls.objects.filter(query).count()

    @classmethod
    def query_driver_route_location(cls, driver):
        """
        check every driver's terminal route information
        """
        pass

    @classmethod
    def query_source_and_destination_list_of_each_truck_type(cls):
        """
        List each truck type's < origin to destination> information
        """
        return cls.objects.values_list('truck__truck_type', 'from_terminal__name',
                                       'to_terminal__name').distinct().order_by(
            'truck__truck_type')

    @classmethod
    def query_non_loaded_return_origin_truck_and_driver_info(cls):
        """
        check the drivers which returned to their origin terminal without load
        """
        return list({obj.driver for obj in
                     cls.objects.select_related('driver').filter(driver__from_terminal=F('to_terminal'),
                                                                 is_loaded=False)})
