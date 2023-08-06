// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import RequestComponent from './Request';
import { connect } from 'react-redux';
import { initRequest } from './state/actions'

const mapDispatchToProps = (dispatch) => ({
  initRequest: () => dispatch(initRequest()),
});

const mapStateToProps = (state) => ({
  request: state.request.data,
});

export const Request = connect(
  mapStateToProps,
  mapDispatchToProps
)(RequestComponent);

