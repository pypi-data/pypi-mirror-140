# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import base64

from requests.models import Response

import contrast
from contrast.agent.settings_state import SettingsState
from contrast.utils.timer import now_ms
from contrast.utils.decorators import fail_safely
from contrast.utils.service_util import sleep
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

PYTHON = "Python"


class BaseTsMessage:
    def __init__(self):
        self.settings = SettingsState()

        self.msg_name = None
        self.path = None
        self.base_url = f"{self.settings.api_url}/api/ng/"
        self.proxy = (
            self.settings.build_proxy_url() if self.settings.is_proxy_enabled else {}
        )

        self.headers = {
            "Authorization": _b64url_stripped(
                f"{self.settings.api_user_name}:{self.settings.api_service_key}"
            ),
            "API-Key": self.settings.api_key,
            "Server-Name": _b64url_stripped(self.settings.get_server_name()),
            "Server-Path": _b64url_stripped(self.settings.get_server_path()),
            "Server-Type": _b64url_stripped(self.settings.get_server_type()),
            "X-Contrast-Agent": f"{PYTHON} {contrast.__version__}",
            "X-Contrast-Header-Encoding": "base64",
        }

        self.body = ""

    @property
    def name(self):
        return self.msg_name

    @fail_safely("Failed to process TS response")
    def process_response(self, response):
        """
        Concrete subclasses that require response handling should define this method
        """
        return


class ServerActivity(BaseTsMessage):
    def __init__(self):
        super().__init__()

        self.msg_name = "activity_server"
        self.path = "activity/server"

        last_update = self.settings.last_update_time_ms
        if self.settings.last_update_time_ms == 0:
            last_update = now_ms()

        self.body = {"lastUpdate": last_update}

    @fail_safely("Failed to process ServerActivity response")
    def process_response(self, response):
        settings = SettingsState()
        if not _process_ts_response_code(response):
            return

        body = response.json()

        settings.apply_ts_server_settings(body)


class BaseTsAppMessage(BaseTsMessage):
    def __init__(self):
        super().__init__()
        self.headers.update(
            {
                "Application-Language": _b64url_stripped(PYTHON),
                "Application-Name": _b64url_stripped(self.settings.app_name),
                "Application-Path": _b64url_stripped(self.settings.app_path),
            }
        )


class Preflight(BaseTsAppMessage):
    def __init__(self, findings):
        super().__init__()
        self.msg_name = "preflight"
        self.path = "preflight"
        self.findings = findings

        self.body = {"messages": []}
        for idx, finding in enumerate(self.findings):
            message = {
                "appLanguage": PYTHON,
                "appName": self.settings.app_name,
                "appPath": self.settings.app_path,
                "appVersion": self.settings.app_version,
                "code": "TRACE",
                "data": finding.preflight,
                "key": idx,
            }
            self.body["messages"].append(message)

    @fail_safely("Failed to process Preflight response")
    def process_response(self, response):
        if not _process_ts_response_code(response):
            return

        body = response.text
        finding_idxs_to_report = self._parse_body(body)
        for finding_idx in finding_idxs_to_report:
            finding = self.findings[finding_idx]  # pylint: disable=unused-variable

            # TODO: PYT-2118 here we will need to construct a Traces message and add it
            # to the reporting queue

    @staticmethod
    def _parse_body(body):
        """
        A preflight response body is a comma-separated list of finding indices that
        should be reported in a Traces message. Some elements of this list will have a
        *, meaning TS needs an AppCreate message before it will accept this finding. For
        now, we do not send findings with a *.

        TODO: PYT-2119 handle * preflight findings
        """
        indices = body.strip('"').split(",")
        return [int(index) for index in indices if index.isdigit()]


class Traces(BaseTsAppMessage):
    def __init__(self, findings):
        super().__init__()
        self.msg_name = "traces"
        self.path = "traces"
        # TODO: PYT-2118


def _b64url_stripped(header_str):
    """
    For some headers, TS expects a value that
    - is base64 encoded using URL-safe characters
    - has any padding (= or ==) stripped

    This follows RFC-4648 - base64 with URL and filename safe alphabet
    """
    return base64.urlsafe_b64encode(header_str.encode()).rstrip(b"=")


def _process_ts_response_code(response):
    """
    Return True if new settings need to be processed
    """
    if not isinstance(response, Response):
        return False

    # TODO: PYT-2120 handle 409, 410, and 5xx properly
    if response.status_code in (401, 408, 409, 410, 412):
        logger.debug(
            "Received %s response code from Teamserver. Sleeping for 15 minutes",
            direct_to_teamserver=1,
        )

        sleep(900)

        return False

    return response.status_code == 200
