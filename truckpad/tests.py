#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Creation: 12/16/18 11:25 PM
@Author: liang
@File: tests.py
"""
from django.test import TestCase

from truckpad.models import Terminal


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.terminal1 = Terminal.objects.create(name='Terminal1', latitude=12.345678, longitude=23.5678901)
        self.terminal2 = Terminal.objects.create(name='Terminal2', latitude=22.345678, longitude=24.5678901)
        self.terminal3 = Terminal.objects.create(name='Terminal3', latitude=13.345678, longitude=23.5678901)
        self.terminal4 = Terminal.objects.create(name='Terminal4', latitude=24.345678, longitude=24.5678901)


class RegistrationBaseTestCase(BaseTestCase):
    pass


class DriverLocationBaseTestCase(BaseTestCase):
    pass


class EmptyReturnDriverBaseTestCase(BaseTestCase):
    pass


class SelfOwnTruckDriverBaseTestCase(BaseTestCase):
    pass


class LoadedTrafficStatisticByTerminalBaseTestCase(BaseTestCase):
    pass


class TruckTrafficRouteHistoryByTruckTypeBaseTestCase(BaseTestCase):
    pass


class DriverUpdateBaseTestCase(BaseTestCase):
    pass
