#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Creation: 12/16/18 11:25 PM
@Author: liang
@File: tests.py
"""
import json

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

    def setUp(self):
        super(RegistrationBaseTestCase, self).setUp()
        self.endpoint = '/api/register-entrance/'
        self.post_data = {
            "truck_number": "DSZ3381",
            "truck_type": 1,
            "cpf_no": "23725897840",
            "name": "Liang",
            "age": 30,
            "gender": 1,
            "drive_license_type": "A/B",
            "has_truck": True,
            "is_loaded": False,
            "user_from_terminal": str(self.terminal1.pk),
            "user_to_terminal": str(self.terminal2.pk),
            "from_terminal": str(self.terminal2.pk),
            "to_terminal": str(self.terminal1.pk)
        }

    def test_required_fields_missing_fail(self):
        lack_data = self.post_data.copy()
        lack_data.popitem()
        while lack_data:
            response = self.client.post(self.endpoint, data=json.dumps(lack_data),
                                        content_type='application/json').json()
            assert response['status'] == 10000
            lack_data.popitem()

    def test_register_entrance_ok(self):
        response = self.client.post(self.endpoint, data=json.dumps(self.post_data),
                                    content_type='application/json').json()
        assert response['status'] == 0
        assert 'driver' in response
        assert 'truck' in response


class DriverLocationBaseTestCase(BaseTestCase):

    def setUp(self):
        super(DriverLocationBaseTestCase, self).setUp()
        self.endpoint = '/api/query-driver-location/'

    def test_required_fields_missing_fail(self):
        response = self.client.generic('GET', self.endpoint, data='{}', content_type='application/json').json()
        assert response['status'] == 10000

    def _prepare_registration_data(self):
        register_data = {
            "truck_number": "DHZ338*",
            "truck_type": 1,
            "cpf_no": "23725897841",
            "name": "Liang",
            "age": 30,
            "gender": 1,
            "drive_license_type": "A/B",
            "has_truck": True,
            "is_loaded": False,
            "user_from_terminal": str(self.terminal1.pk),
            "user_to_terminal": str(self.terminal2.pk),
            "from_terminal": str(self.terminal2.pk),
            "to_terminal": str(self.terminal1.pk)
        }

        self.client.post('/api/register-entrance/', data=json.dumps(register_data), content_type='application/json')

    def test_query_driver_location_ok(self):
        self._prepare_registration_data()
        query_data = {
            'cpf_no': "23725897841"
        }
        response = self.client.generic('GET', self.endpoint, data=json.dumps(query_data),
                                       content_type='application/json').json()
        assert 'origin_terminal' in response, response
        assert 'destination_terminal' in response, response


class EmptyReturnDriverBaseTestCase(BaseTestCase):

    def setUp(self):
        super(EmptyReturnDriverBaseTestCase, self).setUp()
        self.endpoint = '/api/query-empty-return-drivers/'

    def _prepare_multiple_registration_data(self):
        register_data = {
            "truck_number": "DHZ338*",
            "truck_type": 1,
            "cpf_no": "23725897841",
            "name": "Liang",
            "age": 30,
            "gender": 1,
            "drive_license_type": "A/B",
            "has_truck": True,
            "is_loaded": True,
            "user_from_terminal": str(self.terminal1.pk),
            "user_to_terminal": str(self.terminal2.pk),
            "from_terminal": str(self.terminal1.pk),
            "to_terminal": str(self.terminal2.pk)
        }
        # driver from terminal1 -> terminal2  with load
        self.client.post('/api/register-entrance/', data=json.dumps(register_data), content_type='application/json')

        register_data["from_terminal"] = str(self.terminal2.pk)
        register_data["to_terminal"] = str(self.terminal1.pk)
        register_data["is_loaded"] = False

        # driver from terminal2 -> terminal1 without load
        self.client.post('/api/register-entrance/', data=json.dumps(register_data), content_type='application/json')

    def test_query_empty_return_drivers_ok(self):
        self._prepare_multiple_registration_data()
        response = self.client.get(self.endpoint).json()
        assert response['status'] == 0
        assert len(response['data']) == 1


class SelfOwnTruckDriverBaseTestCase(BaseTestCase):

    def setUp(self):
        super(SelfOwnTruckDriverBaseTestCase, self).setUp()
        self.endpoint = '/api/query-own-truck-drivers/'

    def _prepare_multiple_registration_data(self):
        registration_data1 = {
            "truck_number": "DHZ338*",
            "truck_type": 1,
            "cpf_no": "23725897841",
            "name": "Liang",
            "age": 30,
            "gender": 1,
            "drive_license_type": "A/B",
            "has_truck": True,
            "is_loaded": True,
            "user_from_terminal": str(self.terminal1.pk),
            "user_to_terminal": str(self.terminal2.pk),
            "from_terminal": str(self.terminal1.pk),
            "to_terminal": str(self.terminal2.pk)
        }

        registration_data2 = {
            "truck_number": "DHZ338*",
            "truck_type": 1,
            "cpf_no": "23725897842",
            "name": "Hello",
            "age": 30,
            "gender": 1,
            "drive_license_type": "A/B",
            "has_truck": False,
            "is_loaded": True,
            "user_from_terminal": str(self.terminal1.pk),
            "user_to_terminal": str(self.terminal2.pk),
            "from_terminal": str(self.terminal1.pk),
            "to_terminal": str(self.terminal2.pk)
        }

        self.client.post('/api/register-entrance/', data=json.dumps(registration_data1),
                         content_type='application/json')
        self.client.post('/api/register-entrance/', data=json.dumps(registration_data2),
                         content_type='application/json')

    def test_query_own_truck_driver_count_ok(self):
        self._prepare_multiple_registration_data()
        response = self.client.get(self.endpoint).json()
        assert response['status'] == 0
        assert response['driver_count'] == 1


class LoadedTrafficStatisticByTerminalBaseTestCase(BaseTestCase):

    def setUp(self):
        super(LoadedTrafficStatisticByTerminalBaseTestCase, self).setUp()
        self.endpoint = '/api/query-terminal-loaded-traffic/'

    def _prepare_registration_data(self):
        pass

    def test_query_loaded_traffic_of_all_terminal_in_today_ok(self):
        pass

    def test_query_loaded_traffic_of_all_terminal_on_specific_day_ok(self):
        pass

    def test_query_loaded_traffic_of_all_terminal_on_specific_week_period_ok(self):
        pass

    def test_query_loaded_traffic_of_all_terminal_on_specific_month_period_ok(self):
        pass

    def test_query_loaded_traffic_of_specific_terminal_in_today_ok(self):
        pass

    def test_query_loaded_traffic_of_specific_terminal_on_specific_day_ok(self):
        pass

    def test_query_loaded_traffic_of_specific_terminal_on_specific_week_period_ok(self):
        pass

    def test_query_loaded_traffic_of_specific_terminal_on_specific_month_period_ok(self):
        pass


class TruckTrafficRouteHistoryByTruckTypeBaseTestCase(BaseTestCase):
    def setUp(self):
        super(TruckTrafficRouteHistoryByTruckTypeBaseTestCase, self).setUp()
        self.endpoint = '/api/query-truck-type-traffics/'

    def _prepare_multiple_registration_data(self):
        pass

    def test_query_truck_route_history_grouped_by_truck_type_ok(self):
        pass


class DriverUpdateBaseTestCase(BaseTestCase):

    def setUp(self):
        super(DriverUpdateBaseTestCase, self).setUp()
        self.endpoint = '/api/update-driver-info/'

    def _prepare_initial_registration_data(self):
        pass

    def test_update_without_required_field_fail(self):
        pass

    def test_update_driver_info_ok(self):
        pass
