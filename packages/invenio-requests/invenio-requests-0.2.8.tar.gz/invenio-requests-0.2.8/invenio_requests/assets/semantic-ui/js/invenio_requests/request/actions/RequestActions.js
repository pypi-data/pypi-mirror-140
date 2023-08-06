// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { RequestLinksExtractor } from "../../api";
import React from "react";
import Overridable from "react-overridable";
import ReactDOM from "react-dom";
import { RequestAction } from "./index";

const element = document.getElementById("request-actions");

export const RequestActions = ({ request }) => {
  const actions = Object.keys(new RequestLinksExtractor(request).actions);
  return (
    <Overridable id="InvenioRequests.RequestActions.layout" request={request}>
      <>
        {actions.map((action) => (
          <RequestAction action={action} key={action} />
        ))}
      </>
    </Overridable>
  );
};

export const RequestActionsPortalCmp = ({ request }) => {
  return ReactDOM.createPortal(<RequestActions request={request} />, element);
};

export const RequestActionsPortal = Overridable.component(
  "InvenioRequests.RequestActionsPortal",
  RequestActionsPortalCmp
);

export default Overridable.component(
  "InvenioRequests.RequestActions",
  RequestActions
);
