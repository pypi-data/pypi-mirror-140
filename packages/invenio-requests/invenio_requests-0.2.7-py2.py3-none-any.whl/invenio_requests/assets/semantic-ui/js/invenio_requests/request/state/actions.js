// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import isEmpty from "lodash/isEmpty";

export const REQUEST_INIT = "request/INIT";

export const initRequest = (newRequest) => {
  return async (dispatch, getState, config) => {
    if (isEmpty(newRequest)) {
      dispatch({
        type: REQUEST_INIT,
        payload: config.request,
      });
    }
    else{
      dispatch({
        type: REQUEST_INIT,
        payload: newRequest,
      });
    }
  };
};
