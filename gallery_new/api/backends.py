from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from .utils.exceptions import MailformedData
from .models import Token

import math


class CustomPagination(LimitOffsetPagination):

    """ Customised response and parameter names """

    limit_query_param = 'obj_per_page'
    offset_query_param = 'page'
    default_limit = 50

    def get_paginated_response(self, data):
        return Response({
            'total_pages': self.get_total_pages(),
            'total_objects': self.count,
            'obj_per_page': self.limit,
            'items': data
        })

    def get_total_pages(self):
        return int(math.ceil(self.count / self.limit))


class CustomFilterBackend(BaseFilterBackend):

    """
        Filter query by provided parameters

        This method takes filter_parameters list(default: id)
        You can provide parameters for special method
        Example:
            filter_parameters_DELETE = ['id', 'slug']

        If no one of required parameters were not provided raises Exception 'Mailformed data'
    """

    filter_parameters = ['id']

    def filter_queryset(self, request, queryset, view):

        filter = {}
        filter_parameters = self.get_parameters(request, view)

        # get data depending on method
        if request.method == 'GET':
            data = request.query_params
        else:
            data = request.data

        self.check_required_parameters(request, data, view)

        # construct filter request to db
        for parameter in filter_parameters:

            # check if parameter is tuple
            parameter, field = self.clear_parameter(parameter)

            # get parameter value
            value = data.get(parameter)

            if value:
                filter[field] = value

        return queryset.filter(**filter)

    def get_parameters(self, request, view):

        # get method parameters
        method_parameters = getattr(view, 'filter_parameters_' + request.method, None)
        if method_parameters:
            return method_parameters

        # get other parameters
        parameters = getattr(view, 'filter_parameters', None)
        if parameters:
            return parameters

        return self.filter_parameters

    def check_required_parameters(self, request, data, view):

        """ One of required parameters should be provided """

        required_parameters = self.get_required_parameters(request, view)
        if required_parameters:
            check_parameters = any(parameter in data.keys() for parameter in required_parameters)
            if not check_parameters:
                raise MailformedData

    def get_required_parameters(self, request, view):

        # get method required parameters
        method_parameters = getattr(view, 'filter_required_parameters_' + request.method, None)
        if method_parameters:
            return method_parameters

        # get other required parameters
        parameters = getattr(view, 'filter_required_parameters', None)
        if parameters:
            return parameters

        return []

    def clear_parameter(self, parameter):

        """
            parameter can be tuple
            because field name and parameter can be different

            Example:
                ('date_gt', 'created_at__gt'),
        """

        if isinstance(parameter, tuple):
            parameter, field = parameter
        else:
            field = parameter

        return parameter, field


class CustomTokenAuth(TokenAuthentication):

    """ Custom token model """

    model = Token
    keyword = 'Bearer'
