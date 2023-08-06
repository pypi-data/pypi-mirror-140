# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

from contrast.configuration import AgentConfig
from contrast.reporting import teamserver_messages, reporting_client
from contrast.utils.loggers import logger


def validate_config():
    try:
        exit_status = _validate()
        sys.exit(exit_status)
    except Exception as e:
        _log("Unexpected error while validating agent config:")
        _log(f"{e!r}")
        _log("Unable to validate agent config")
        sys.exit(1)


def _log(msg):
    print(f"[contrast-validate-config] {msg}")


def _validate():
    """
    Validates the config and returns an appropriate exit status
    """
    _log("Validating Contrast configuration")
    _log("You may see agent logs in structured log format")

    logger.setup_basic_agent_logger()

    if not _check_config():
        return 1

    if not _check_connection():
        return 1

    return 0


def _check_config():
    _log("Loading config")

    config = AgentConfig()
    config.is_service_bypassed = True

    _log("Config loaded successfully")

    # TODO: PYT-2082 Add proxy and cert validation

    missing_values = config.check_for_api_config()
    if not missing_values:
        return True
    for missing_value in missing_values:
        _log(f"Missing required config value: {missing_value}")
    return False


def _check_connection():
    client = reporting_client.ReportingClient()
    msg = teamserver_messages.ServerActivity()

    _log("Sending test request to Contrast UI")

    resp = client.send_message(msg)

    if resp is None:
        _log("Request failed")
        _log("Unable to establish a connection with current configuration")
        return False

    _log(f"Response: {resp.status_code} {resp.reason}")
    if resp.text:
        _log(resp.text)

    # note: status code 400 for ServerActicity just means the server doesn't exist
    # it still indicates a successful connection to teamserver
    # TODO: PYT-2080 Use ServerCreate instead

    if resp.status_code == 401:
        _log("You are connecting to the Contrast UI but have improper authorization")
        return False

    if resp.status_code > 401:
        _log("You are connecting to the Contrast UI but are seeing an unexpected error")
        return False

    _log(f"{resp.status_code} status code indicates success for this endpoint")
    _log("Connection to the Contrast UI successful")
    return True
