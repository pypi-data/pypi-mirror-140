# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Request views module."""

from flask import render_template
from flask_login import login_required
from jinja2 import TemplateNotFound

from invenio_requests.views.decorators import pass_request


@login_required
@pass_request
def requests_detail(request=None, pid_value=None):
    """Community detail page."""
    request_dict = request.to_dict()
    # TODO replace by resolver
    request_dict["topic"] = {}

    try:
        return render_template(
            f"invenio_requests/{request_dict['type']}/index.html",
            request=request_dict,  # TODO: use serializer
        )

    except TemplateNotFound:
        return render_template(
            "invenio_requests/details/index.html",
            request=request_dict,  # TODO: use serializer
        )
