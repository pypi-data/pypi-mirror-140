// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { errorSerializer, payloadSerializer } from "../../api/serializers";
import { SUCCESS as TIMELINE_SUCCESS } from "../../timeline/state/actions";
import _cloneDeep from "lodash/cloneDeep";

export const IS_LOADING = "eventEditor/IS_LOADING";
export const HAS_ERROR = "eventEditor/HAS_ERROR";
export const SUCCESS = "eventEditor/SUCCESS";
export const SETTING_CONTENT = "eventEditor/SETTING_CONTENT";

export const setEventContent = (content) => {
  return async (dispatch) => {
    dispatch({
      type: SETTING_CONTENT,
      payload: content,
    });
  };
};

export const submitComment = (content, format) => {
  return async (dispatch, getState, config) => {
    dispatch({
      type: IS_LOADING,
    });

    const payload = payloadSerializer(content, format || "html");

    try {
      const response = await config.requestsApi.submitComment(payload);
      dispatch({
        type: TIMELINE_SUCCESS,
        payload: _updatedState(response.data, getState().timeline.data),
      });
      dispatch({ type: SUCCESS });
    } catch (error) {
      dispatch({
        type: HAS_ERROR,
        payload: errorSerializer(error),
      });

      // throw it again, so it can be caught in the local state
      throw error;
    }
  };
};

const _updatedState = (newComment, currentState) => {
  const timelineState = _cloneDeep(currentState);

  const currentHits = timelineState.hits.hits;

  currentHits.push(newComment);

  return timelineState;
};
