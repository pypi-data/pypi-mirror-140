// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { InvenioRequestsAPI } from "./api/api";
import React from "react";
import ReactDOM from "react-dom";
import { InvenioRequestsApp } from "./InvenioRequestsApp";

const requestDetailsDiv = document.getElementById("request-detail");
const request = JSON.parse(requestDetailsDiv.dataset.record);

const overriddenCmps = {
  // "RequestTopic.layout.community-submission": RequestTopicRecord,
  // customizable request topic (dynamic ID creation)
  // 'RequestTopic.layout.community-inclusion': RequestTopicUser,
  // 'RequestTopic.layout.community-invitation': RequestTopicCommunity,
};

ReactDOM.render(
  <InvenioRequestsApp request={request} />,
  requestDetailsDiv
);

export { default as RequestDetails } from "./request/RequestDetails";
export { default as Timeline } from "./timeline/TimelineFeed";
export { default as TimelineEvent } from "./timelineEvent/TimelineEvent";
export { default as RequestMetadata } from "./request/RequestMetadata";
export { InvenioRequestsAPI } from "./api/api";
