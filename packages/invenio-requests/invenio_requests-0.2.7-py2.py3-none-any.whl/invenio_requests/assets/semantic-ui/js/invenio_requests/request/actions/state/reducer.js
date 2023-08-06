// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { IS_LOADING, SUCCESS, HAS_ERROR, ACTION_MODAL_TOGGLE } from './actions';

export const initialState = {
  loading: false,
  data: {  },
  actionModalOpen: false,
  error: null,
};

export const requestActionReducer = (state = initialState, action) => {
  switch (action.type) {
    case IS_LOADING:
      return { ...state, loading: true };
    case SUCCESS:
      return {
        ...state,
        loading: false,
        data: action.payload,
        error: null,
      };
    case HAS_ERROR:
      return {
        ...state,
        loading: false,
        error: action.payload,
      };
    case ACTION_MODAL_TOGGLE:
      return {
        actionModalOpen: action.payload,
      };
    default:
      return state;
  }
};
