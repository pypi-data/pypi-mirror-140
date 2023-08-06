// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import EventWithStateComponent from "./TimelineEventWithState";
import { connect } from "react-redux";
import { updateComment, deleteComment } from "./state/actions";
import { openModal } from "../confirmationModal/state/actions";

const mapDispatchToProps = (dispatch) => ({
  openConfirmModal: (payload) => dispatch(openModal(payload)),
  updateComment: async (payload) => dispatch(updateComment(payload)),
  deleteComment: async (payload) => dispatch(deleteComment(payload)),
});

export const TimelineEventWithState = connect(
  null,
  mapDispatchToProps
)(EventWithStateComponent);
