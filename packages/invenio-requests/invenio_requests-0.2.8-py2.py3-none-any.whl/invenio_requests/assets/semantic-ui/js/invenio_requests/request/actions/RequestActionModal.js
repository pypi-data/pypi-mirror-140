// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import Overridable from "react-overridable";
import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Modal } from "semantic-ui-react";
import Error from "../../components/Error";
import { i18next } from "@translations/invenio_requests/i18next";
import { Trans } from "react-i18next";

export class RequestActionModal extends Component {

  setOpen = (isOpen) => {
    const { setActionModalOpen, modalId } = this.props;
    setActionModalOpen(isOpen, modalId);
  };

  render() {
    const {
      action,
      loading,
      modalOpen,
      handleActionClick,
      modalId,
      error,
      children,
    } = this.props;
    return (
      <Overridable
        id="InvenioRequests.RequestActionModal.layout"
        {...this.props}
      >
        <Modal
          open={modalOpen.modalId === modalId && modalOpen.isOpen}
          trigger={
            <Button onClick={() => this.setOpen(true)} loading={loading}>
              <Trans
                defaults="{{action}}"
                values={{ "action": action }}
              />
            </Button>
          }
        >
          <Modal.Header> <Trans
                defaults="{{action}} request"
                values={{ "action": action }}
              /></Modal.Header>
          <Modal.Content>
            <Modal.Description>
              {error && <Error error={error.message} />}
              {children}
            </Modal.Description>
          </Modal.Content>
          <Modal.Actions>
            <Button onClick={() => this.setOpen(false)} loading={loading}>
              {i18next.t("Cancel")}
            </Button>
            <Button onClick={handleActionClick} loading={loading}>
              <Trans
                defaults="{{action}}"
                values={{ "action": action }}
              />
            </Button>
          </Modal.Actions>
        </Modal>
      </Overridable>
    );
  }
}

RequestActionModal.propTypes = {
  setActionModalOpen: PropTypes.func.isRequired,
  handleActionClick: PropTypes.func.isRequired,
  modalOpen: PropTypes.bool,
  loading: PropTypes.bool,
  modalId: PropTypes.string.isRequired
};

RequestActionModal.defaultProps = {
  loading: false,
  modalOpen: false,
}

export default Overridable.component(
  "InvenioRequests.RequestActionModal",
  RequestActionModal
);
