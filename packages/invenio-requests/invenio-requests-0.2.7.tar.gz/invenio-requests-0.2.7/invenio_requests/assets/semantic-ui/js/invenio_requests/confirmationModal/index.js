// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import { connect } from "react-redux";
import ConfirmationModalComponent from "./ConfirmationModal";
import { startAction, closeModal } from "./state/actions";

const mapDispatchToProps = (dispatch) => ({
  startAction: () => dispatch(startAction()),
  closeModal: () => dispatch(closeModal()),
});

const mapStateToProps = (state) => ({
  modalIsOpen: state.confirmationModal.modalIsOpen,
  modalAction: state.confirmationModal.modalAction,
  modalText: state.confirmationModal.modalText,
  modalError: state.confirmationModal.modalError,
  isLoading: state.confirmationModal.isLoading,
});

export const ConfirmationModal = connect(
  mapStateToProps,
  mapDispatchToProps
)(ConfirmationModalComponent);
