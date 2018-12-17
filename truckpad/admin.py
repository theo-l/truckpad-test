#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Creation: 12/16/18 10:41 AM
@Author: liang
@File: admin.py
"""
from django.contrib import admin

from truckpad.models import Registration, Terminal, Driver, Truck


@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    pass


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    pass


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    pass


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('driver', 'truck', 'from_terminal', 'to_terminal', 'is_loaded', 'created_at')
