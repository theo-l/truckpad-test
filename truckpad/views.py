#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Creation: 12/16/18 3:23 PM
@Author: liang
@File: views.py
"""
import json
from json import JSONDecodeError

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET, require_http_methods

from truckpad.models import Driver, Terminal, Registration, Truck, get_truck_type_description


@require_POST
@csrf_exempt
def terminal_entrance_registration(request):
    try:
        post_data = json.loads(request.body.decode())
        # post_data=request.POST.dict()
    except JSONDecodeError:
        return JsonResponse({'status': 20000, 'message': 'Request data is not a valid json data object!'})
    else:
        required_fields = [
            'truck_number', 'truck_type', 'cpf_no', 'age', 'gender',
            'drive_license_type', 'is_loaded', 'user_from_terminal', 'user_to_terminal', 'from_terminal', 'to_terminal'
        ]

        for key in required_fields:
            if key not in post_data or post_data.get(key, None) is None:
                return JsonResponse({'status': 10000, 'message': '*{}* need to be a valid value!'.format(key)})

        truck, _ = Truck.objects.get_or_create(number=post_data.pop('truck_number'),
                                               truck_type=post_data.pop('truck_type'))

        is_loaded = post_data.pop('is_loaded')
        user_from_terminal = Terminal.objects.filter(pk=post_data.pop('user_from_terminal')).first()
        user_to_terminal = Terminal.objects.filter(pk=post_data.pop('user_to_terminal')).first()
        from_terminal = Terminal.objects.filter(pk=post_data.pop('from_terminal')).first()
        to_terminal = Terminal.objects.filter(pk=post_data.pop('to_terminal')).first()
        if not all([user_from_terminal, user_to_terminal, from_terminal, to_terminal]):
            return JsonResponse({'status': 10002, 'message': 'Terminal not found!'})

        print(post_data)

        driver, _ = Driver.objects.get_or_create(cpf_no=post_data.pop('cpf_no'), from_terminal=user_from_terminal,
                                                 to_terminal=user_to_terminal)
        driver.update_registration_info(**post_data)

        registration = Registration.register(driver=driver, truck=truck, is_loaded=is_loaded,
                                             from_terminal=from_terminal, to_terminal=to_terminal)

        return_data = registration.to_dict(dehydrate_fields=['driver', 'truck'])
        return_data['status'] = 0
        return JsonResponse(return_data)


@require_GET
def query_driver_source_and_destination(request):
    required_query_fields = ['cpf_no']
    try:
        query_data = json.loads(request.body.decode())
    except JSONDecodeError:
        return JsonResponse({'status': 20000, 'message': 'Request data is not a valid json data object!'})
    else:
        for key in required_query_fields:
            if key not in query_data or query_data.get(key, None) is None:
                return JsonResponse({'status': 10000, 'message': '*cpf_no* need to be a valid value!'})

        driver = Driver.objects.filter(cpf_no=query_data.pop('cpf_no')).first()
        if driver is None:
            return JsonResponse({'status': 10001, 'message': 'Driver not found!'})

        result_data = {
            'status': 0,
            'cpf_no': driver.cpf_no,
            'name': driver.name,
            'origin_terminal': driver.from_terminal.to_dict(includes=['name', 'latitude', 'longitude']),
            'destination_terminal': driver.to_terminal.to_dict(includes=['name', 'latitude', 'longitude'])
        }

        return JsonResponse(result_data)


@require_GET
def query_non_loaded_return_driver_info(request):
    empty_returned_drivers = Registration.query_non_loaded_return_origin_truck_and_driver_info()
    result_data = {
        'status': 0,
        'data': [
            obj.to_dict() for obj in empty_returned_drivers
        ]
    }
    return JsonResponse(result_data)


@require_GET
def query_drivers_who_own_truck(request):
    driver_with_truck_count = Driver.query_number_of_drivers_who_own_truck()
    return JsonResponse({'status': 0, 'driver_count': driver_with_truck_count})


@require_GET
def query_terminal_load_traffic_by_date_period(request):
    required_query_fields = []
    try:
        query_data = json.loads(request.body.decode())
    except JSONDecodeError:
        return JsonResponse({'status': 20000, 'message': 'Request data is not a valid json data object!'})
    else:

        for key in required_query_fields:
            if key not in query_data:
                return JsonResponse({'status': 10000, 'message': '*{}* need to be a valid value!'.format(key)})

        start_date, end_date = None, None
        try:
            if 'start_date' in query_data:
                start_date = timezone.datetime.strptime(query_data.pop('start_date'), '%Y-%m-%d')
            if 'end_date' in query_data:
                end_date = timezone.datetime.strptime(query_data.pop('end_date'), '%Y-%m-%d')
        except ValueError as e:
            return JsonResponse(
                {'status': 20000, 'message': 'Request data is not a valid date format string![{}]'.format(str(e))})

        terminal = None
        if 'terminal' in query_data:
            terminal = Terminal.objects.filter(pk=query_data.pop('terminal')).first()
            if terminal is None:
                return JsonResponse({'status': 10002, 'message': 'Terminal not found!'})

        traffic_count = Registration.query_loaded_truck_traffic_of_terminal_by_date_period(start_date, end_date,
                                                                                           terminal)
        result_data = {
            'status': 0,
            'data': {'traffic_count': traffic_count}
        }
        return JsonResponse(result_data)


@require_GET
def query_each_type_truck_traffic_list(request):
    def _format_record(obj):
        obj = [get_truck_type_description(obj[0]), *obj[1:]]
        return dict(zip(['Truck Type', 'Origin Terminal', 'Destination Terminal'], list(obj)))

    list_data = Registration.query_source_and_destination_list_of_each_truck_type()
    data = map(_format_record, list_data)
    return JsonResponse({'status': 0, 'data': list(data)})


@require_http_methods(['PUT'])
@csrf_exempt
def update_driver(request):
    """
    receive client request to update driver's registration information data
    """
    try:
        post_data = json.loads(request.body.decode())
    except JSONDecodeError:
        return JsonResponse({'status': 20000, 'message': 'Request data is not a valid json data object!'})
    else:

        cpf_no = post_data.get('cpf_no', None)
        if not cpf_no:
            return JsonResponse({'status': 10000, 'message': '*cpf_no* need to be a valid value!'})

        driver = Driver.objects.filter(cpf_no=cpf_no).first()
        if driver is None:
            return JsonResponse({'status': 10001, 'message': 'Driver not found!'})

        del post_data['cpf_no']  # 不要更新用户的cpf number

        from_terminal_id = post_data.get('from_terminal', None)
        to_terminal_id = post_data.get('to_terminal', None)
        if from_terminal_id:
            from_terminal_obj = Terminal.objects.filter(pk=from_terminal_id).first()
            if from_terminal_obj is None:
                return JsonResponse({'status': 10002, 'message': 'From terminal not found!'})
            post_data['from_terminal'] = from_terminal_obj

        if to_terminal_id:
            to_terminal_obj = Terminal.objects.filter(pk=to_terminal_id).first()
            if to_terminal_obj is None:
                return JsonResponse({'status': 10002, 'message': 'To terminal not found!'})

            if to_terminal_obj == post_data.get('from_terminal', None):
                return JsonResponse({'status': 10003, 'message': 'From terminal can not be same as To terminal!'})
            post_data['to_terminal'] = to_terminal_obj

        driver.update_registration_info(**post_data)
        result_data = {
            'status':0,
            'data':driver.to_dict()
        }

        return JsonResponse(result_data)
