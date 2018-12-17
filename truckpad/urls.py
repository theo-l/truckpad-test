"""truckpad URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from truckpad.views import query_driver_source_and_destination, query_non_loaded_return_driver_info, \
    query_drivers_who_own_truck, query_terminal_load_traffic_by_date_period, query_each_type_truck_traffic_list, \
    update_driver
from .views import (
    terminal_entrance_registration,
)

api_urlpatterns = [
    url(r'^register-entrance/$', terminal_entrance_registration, name='register-entrance'),
    url(r'^query-driver-location/$', query_driver_source_and_destination, name='query-driver-location'),
    url(r'^query-empty-return-drivers/$', query_non_loaded_return_driver_info, name='query-empty-return-drivers'),
    url(r'^query-own-truck-drivers/$', query_drivers_who_own_truck, name='query-own-truck-drivers'),
    url(r'^query-terminal-loaded-traffic/$', query_terminal_load_traffic_by_date_period,
        name='query-terminal-loaded-traffic'),
    url(r'^query-truck-type-traffics/$', query_each_type_truck_traffic_list, name='query-truck-type-traffics'),
    url(r'^update-driver-info/$', update_driver, name='update-driver-info')
]

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(api_urlpatterns)),
]
