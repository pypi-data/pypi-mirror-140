// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import FormattedInputEditor from "../../components/FormattedInputEditor";
import React, { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { Divider, Modal } from "semantic-ui-react";
import { RequestActionModal } from "./";
import { Trans } from "react-i18next";

export class RequestAction extends Component {
  constructor(props) {
    super(props);
    this.state = { actionComment: "", modalOpen: false };
  }

  onCommentChange = (event, editor) => {
    this.setState({ actionComment: editor.getData() });
  };

  handleActionClick = () => {
    const { action, performAction } = this.props;
    const { actionComment } = this.state;
    performAction(action, actionComment);
  };

  render() {
    const { action, loading, performAction } = this.props;
    return (
      <Overridable
        id="InvenioRequests.RequestAction.layout"
        action={action}
        loading={loading}
        performAction={performAction}
      >
        <RequestActionModal
          action={action}
          loading={loading}
          handleActionClick={this.handleActionClick}
          modalId={action}
        >
          <Modal.Content>
            <Modal.Description>
              <Trans
                defaults="Comment on your {{action}} request action (optional)."
                values={{ action: action }}
              />
              <Divider hidden />
              <FormattedInputEditor onChange={this.onCommentChange} />
            </Modal.Description>
          </Modal.Content>
        </RequestActionModal>
      </Overridable>
    );
  }
}

RequestAction.propTypes = {
  action: PropTypes.string.isRequired,
  performAction: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};

RequestAction.defaultProps = {
  loading: false,
};

export default Overridable.component(
  "InvenioRequests.RequestAction",
  RequestAction
);
