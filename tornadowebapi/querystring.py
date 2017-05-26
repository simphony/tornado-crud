# -*- coding: utf-8 -*-
# Imported from flask-rest-jsonapi
# https://github.com/miLibris/flask-rest-jsonapi

import json

from tornado import escape
from tornadowebapi.errors import Error, Source
from .exceptions import BadRequest, InvalidFilters, InvalidSort
from .schema import get_model_field, get_relationships


class QueryStringManager(object):
    """Querystring parser according to jsonapi reference
    """

    MANAGED_KEYS = (
        'filter',
        'page',
        'fields',
        'sort',
        'include'
    )

    def __init__(self, querystring, schema):
        """Initialization instance

        Parameters
        ----------
        querystring: dict
            query string dict from request.args
        """
        if not isinstance(querystring, dict):
            raise ValueError('QueryStringManager require a dict-like object '
                             'query_string parameter')

        self.qs = querystring
        self.schema = schema

    def _get_key_values(self, name):
        """Return a dict containing key / values items for a given key, used
        for items like filters, page, etc.

        Parameters
        ----------
        name: str
            name of the querystring parameter

        Returns
        -------
        dict:
            a dict of key / values items
        """
        results = {}

        for key, value in self.qs.items():
            try:
                if not key.startswith(name):
                    continue

                key_start = key.index('[') + 1
                key_end = key.index(']')
                item_key = key[key_start:key_end]

                if ',' in value:
                    item_value = value.split(',')
                else:
                    item_value = value

                if isinstance(item_value, list):
                    if len(item_value) == 0:
                        continue
                    elif len(item_value) == 1:
                        item_value = item_value[0]

                results.update({item_key: item_value})
            except Exception:
                raise BadRequest([
                    Error(
                        source=Source(parameter=key),
                        title="Parse error"
                    )])

        return escape.recursive_unicode(results)

    @property
    def querystring(self):
        """Return original querystring but containing only managed keys

        Returns
        -------
        dict: dict of managed querystring parameter
        """
        return {key: value for (key, value) in self.qs.items()
                if key.startswith(self.MANAGED_KEYS)}

    @property
    def filters(self):
        """Return filters from query string.

        Returns
        -------
        list:
            filter information
        """
        filters = self.qs.get('filter')
        if filters is not None:
            try:
                filters = json.loads(filters)
            except (ValueError, TypeError):
                raise InvalidFilters.from_message("Parse error")

        return filters

    @property
    def pagination(self):
        """Return all page parameters as a dict.

        :return dict: a dict of pagination information

        To allow multiples strategies, all parameters starting with `page`
        will be included. e.g::

            {
                "number": '25',
                "size": '150',
            }

        Example with number strategy::

            >>> query_string = {'page[number]': '25', 'page[size]': '10'}
            >>> parsed_query.pagination
            {'number': '25', 'size': '10'}
        """
        # check values type
        result = self._get_key_values('page')
        for key, value in result.items():
            if key not in ('number', 'size'):
                raise BadRequest([
                    Error(
                        source=Source(
                            parameter="page",
                        ),
                        detail="{} is not a valid parameter "
                               "of pagination".format(key)
                    )])
            try:
                result[key] = int(value)
            except ValueError:
                raise BadRequest([
                    Error(
                        source=Source(
                            parameter='page[{}]'.format(key),
                        ),
                        detail="Parse error"
                    )
                ])

        return result

    @property
    def fields(self):
        """Return fields wanted by client.

        Returns
        -------
        dict:
            a dict of sparse fieldsets information

            Return value will be a dict containing all fields by resource,
            for example::

                {
                    "user": ['name', 'email'],
                }

        """
        result = self._get_key_values('fields')
        for key, value in result.items():
            if not isinstance(value, list):
                result[key] = [value]

        return result

    @property
    def sorting(self):
        """Return fields to sort by including sort name for SQLAlchemy
        and row sort parameter for other ORMs

        Returns
        -------
        list:
            a list of sorting information

            Example of return value::

                [
                    {'field': 'created_at', 'order': 'desc'},
                ]

        """
        if self.qs.get('sort'):
            sorting_results = []
            for sort_field in self.qs['sort'].split(','):
                field = sort_field.replace('-', '')
                if field not in self.schema._declared_fields:
                    raise InvalidSort.from_message(
                        "{} has no attribute "
                        "{}".format(self.schema.__name__, field))
                if field in get_relationships(self.schema).values():
                    raise InvalidSort.from_message(
                        "You can't sort on {} "
                        "because it is a relationship "
                        "field".format(field))
                field = get_model_field(self.schema, field)
                order = 'desc' if sort_field.startswith('-') else 'asc'
                sorting_results.append({'field': field, 'order': order})
            return sorting_results

        return []

    @property
    def include(self):
        """Return fields to include

        Returns
        -------
        list:
            a list of include information
        """
        include_param = self.qs.get('include')
        return include_param.split(',') if include_param else []
