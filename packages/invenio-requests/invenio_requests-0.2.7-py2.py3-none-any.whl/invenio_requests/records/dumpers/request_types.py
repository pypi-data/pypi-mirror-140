# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Elasticsearch dumpers for the request type of requests."""


from invenio_records.dumpers import ElasticsearchDumperExt


class RequestTypeDumperExt(ElasticsearchDumperExt):
    """Elasticsearch dumper extension for request types."""

    def __init__(self, field):
        """Constructor."""
        super().__init__()
        self.field = field

    def dump(self, record, data):
        """Dump the data."""
        data[self.field] = record.request_type.name

    def load(self, data, record_cls):
        """Load the data."""
        data.pop(self.field)
