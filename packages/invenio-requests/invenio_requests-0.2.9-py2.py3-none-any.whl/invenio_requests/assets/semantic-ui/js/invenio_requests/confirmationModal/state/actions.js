// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import { errorSerializer } from "../../api/serializers";

export const OPEN_MODAL = "confirmation_modal/OPEN_MODAL";
export const CLOSE_MODAL = "confirmation_modal/CLOSE_MODAL";
export const START_ACTION = "confirmation_modal/START_ACTION";
export const ACTION_SUCCESS = "confirmation_modal/ACTION_SUCCESS";
export const HAS_ERROR = "confirmation_modal/HAS_ERROR";

export const openModal = ({ text, action }) => {
  return async (dispatch) => {
    dispatch({ type: OPEN_MODAL, payload: { text, action } });
  };
};

export const startAction = () => {
  return async (dispatch, getState) => {
    const { modalAction } = getState().confirmationModal;

    try {
      dispatch({ type: START_ACTION });

      await modalAction();

      dispatch({ type: CLOSE_MODAL });
    } catch (error) {
      dispatch({ type: HAS_ERROR, payload: errorSerializer(error) });
    }
  };
};

export const closeModal = () => {
  return async (dispatch) => {
    dispatch({ type: CLOSE_MODAL });
  };
};
