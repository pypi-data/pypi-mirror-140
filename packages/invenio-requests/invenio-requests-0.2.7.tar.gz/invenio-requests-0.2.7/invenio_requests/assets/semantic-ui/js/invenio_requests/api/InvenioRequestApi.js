// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import { http } from "./config";
import isEmpty from "lodash/isEmpty";

export class RequestLinkExtractor {
  #links;

  constructor(request) {
    if (!request?.links) {
      throw TypeError("Request resource links are undefined");
    }
    this.#links = request.links;
  }

  get timeline() {
    if (!this.#links.timeline) {
      throw TypeError("Timeline link missing from resource.");
    }
    return this.#links.timeline;
  }

  get comments() {
    if (!this.#links.comments) {
      throw TypeError("Comments link missing from resource.");
    }
    return this.#links.comments;
  }

  get actions() {
    if (!this.#links.actions) {
      throw TypeError("Actions link missing from resource.");
    }
    return this.#links.actions;
  }
}

export class InvenioRequestsAPI {
  #links;
  constructor(requestLinkExtractor) {
    this.#links = requestLinkExtractor;
  }

  getTimeline = async (params) => {
    return await http.get(this.#links.timeline, { params });
  };

  submitComment = async (payload) => {
    return await http.post(this.#links.comments, payload);
  };

  performAction = async (action, commentContent) => {
    let payload = {};
    if (!isEmpty(commentContent)) {
      payload = {
        payload: {
          content: commentContent,
          format: "html",
        },
      };
    }
    return await http.post(this.#links.actions[action], payload);
  };
}
