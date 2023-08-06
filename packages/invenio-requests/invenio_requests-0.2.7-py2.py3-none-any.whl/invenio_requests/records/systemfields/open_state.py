# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Systemfield for calculating the is_open property of a request."""

from invenio_records.systemfields import SystemField


class OpenStateCalculatedField(SystemField):
    """Systemfield for calculating whether or not the request is open."""

    def calculate(self, record):
        """Calculate the is_open property of the request."""
        return record.request_type.available_statuses.get(record.status, False)

    def __get__(self, record, owner=None):
        """Get the request's is_open state."""
        if record is None:
            # access by class
            return self

        return self.calculate(record)
