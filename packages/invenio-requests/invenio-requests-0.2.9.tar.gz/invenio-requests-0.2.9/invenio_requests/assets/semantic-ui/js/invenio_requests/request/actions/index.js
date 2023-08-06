// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { connect } from 'react-redux';
import { performAction, setActionModalOpen } from './state/actions';
import RequestActionCmp from './RequestAction';
import RequestActionModalCmp from './RequestActionModal';

const mapDispatchToProps = (dispatch) => ({
  performAction: (action, payload) => dispatch(performAction(action, payload)),
});

const mapStateToProps = (state) => ({
  loading: state.requestAction.loading,
  error: state.requestAction.error,
});


export const RequestAction = connect(
  mapStateToProps,
  mapDispatchToProps
)(RequestActionCmp);


const mapDispatchToPropsModal = (dispatch) => ({
  setActionModalOpen: (isOpen, modalId) => dispatch(setActionModalOpen(isOpen, modalId)),
});

const mapStateToPropsModal = (state) => ({
  error: state.requestAction.error,
  modalOpen: state.requestAction.actionModalOpen,
  loading: state.requestAction.loading,
});


export const RequestActionModal = connect(
  mapStateToPropsModal,
  mapDispatchToPropsModal
)(RequestActionModalCmp);
