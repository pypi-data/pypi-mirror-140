# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import threading
import queue

from requests import put as put_request

from .teamserver_messages import BaseTsMessage
from contrast.agent import scope
from contrast.agent.settings_state import SettingsState
from contrast.reporting import RequestAudit
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class ReportingClient(threading.Thread):
    def __init__(self):
        self.message_q = queue.Queue(maxsize=128)
        self.settings = SettingsState()
        self.request_audit = (
            RequestAudit(self.settings.config)
            if self.settings.config.is_request_audit_enabled
            else None
        )
        self.stopped = False

        if self.request_audit:
            self.request_audit.prepare_dirs()

        super().__init__()

        self.daemon = True

    def run(self):
        with scope.contrast_scope():
            logger.debug("Starting reporting thread", direct_to_teamserver=1)

            while not self.stopped and self.settings.is_agent_config_enabled():
                try:
                    msg = self.message_q.get(block=True, timeout=5)
                    response = self.send_message(msg)
                    msg.process_response(response)
                except queue.Empty:
                    pass

    def send_message(self, msg):
        try:
            logger.debug(
                "Sending message to Teamserver %s", type(msg), direct_to_teamserver=1
            )

            cert = None
            url = msg.base_url + msg.path

            if self.settings.is_cert_verification_enabled:
                if (
                    not self.settings.ca_file
                    or not self.settings.client_cert_file
                    or not self.settings.client_private_key
                ):
                    logger.error(
                        "Unable to communicate with Contrast. "
                        "Certificate configuration is not set properly.",
                        direct_to_teamserver=1,
                    )
                    self.settings.config.put("enable", False)
                    return None

                cert = (
                    self.settings.client_cert_file,
                    self.settings.client_private_key,
                )

            response = put_request(
                url,
                json=msg.body,
                proxies=msg.proxy,
                headers=msg.headers,
                allow_redirects=False,
                verify=self.settings.ca_file if self.settings.ca_file else True,
                cert=cert,
            )

            logger.debug("Teamserver response: %s", response, direct_to_teamserver=1)

            if self.request_audit:
                self.request_audit.audit(msg, response)

            return response

        except Exception as e:
            logger.exception(
                "Failed to send message to Contrast: %s",
                e,
                direct_to_teamserver=1,
            )
            self.settings.config.put("enable", False)

        return None

    def add_message(self, msg, response_handler=None):
        if msg is None or not isinstance(msg, BaseTsMessage):
            return

        logger.debug(
            "Adding msg to reporting queue: %s", type(msg), direct_to_teamserver=1
        )

        self.message_q.put(msg)
