// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import React from "react";
import { Modal, Button, Message } from "semantic-ui-react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_requests/i18next";

export const ConfirmationModal = ({
  modalIsOpen,
  modalText,
  closeModal,
  startAction,
  isLoading,
  modalError,
}) => {
  return (
    <Modal onClose={closeModal} open={modalIsOpen}>
      <Modal.Header>{i18next.t("Confirm")}</Modal.Header>
      <Modal.Content>{modalText}</Modal.Content>
      <Modal.Actions>
        {modalError && (
          <Message negative compact>
            {modalError}
          </Message>
        )}

        <Button content={i18next.t("Cancel")} onClick={() => closeModal()} />
        <Button
          content={i18next.t("Confirm")}
          negative
          onClick={() => startAction()}
          loading={isLoading}
        />
      </Modal.Actions>
    </Modal>
  );
};

ConfirmationModal.propTypes = {
  modalIsOpen: PropTypes.bool,
  modalText: PropTypes.string,
  closeModal: PropTypes.func,
  startAction: PropTypes.func,
  isLoading: PropTypes.bool,
  modalError: PropTypes.string,
};

export default ConfirmationModal;
