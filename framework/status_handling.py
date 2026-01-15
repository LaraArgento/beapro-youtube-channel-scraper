import datetime
import logging
from .datasources import *
from .finalize import *
from .state import STATE
from atexit import register
from botcity.maestro import *

'''
status_handling.py
    Provides exception handling, error reporting, and success registration for BotCity automation.
    Handles business exceptions, system exceptions, and interruption requests
    with alerting and screenshot capabilities.
'''

logger = logging.getLogger(__name__)
maestro = STATE.maestro


def handle_business_exception(exception: Exception):
    STATE.register_error()
    data_source.report_error("BUSINESS EXCEPTION", exception)
    logger.error(
        f"Business Exception {exception} occurred for item {STATE.item}.")
    maestro.alert(
        task_id=STATE.task_id,
        title="Business Exception ocurred.",
        message=f"Exception: {exception}, Item: {
            STATE.item}.",
        alert_type=AlertType.ERROR)
    screenshot_error_report(exception)
    # You can add more steps here if needed!
    # What should be done when a business exception occurs?
    append_finish_status_message("Business Exception occurred during process.")


def handle_system_exception(exception: Exception):
    STATE.register_error()
    data_source.report_error("SYSTEM EXCEPTION", exception)
    logger.error(
        f"System Exception {exception} occurred for item {STATE.item}.")
    maestro.alert(
        task_id=STATE.task_id,
        title="System Exception ocurred.",
        message=f"Check the logs for more information. Item: {
            STATE.item}.",
        alert_type=AlertType.ERROR)
    screenshot_error_report(exception)
    # You can add more steps here if needed!
    # What should be done when a system exception occurs?
    ...


def handle_interrupt_requested(exception: Exception):
    # The Automation will be stopped and end gracefully.
    STATE.register_error()
    data_source.report_error("INTERRUPTION REQUESTED", exception)
    logger.warning(f"Interruption requested via the BotCity Orchestrator.")
    maestro.alert(
        task_id=STATE.task_id,
        title="Interruption requested.",
        message="Interruption requested via the BotCity Orchestrator. Check the logs for more information.",
        alert_type=AlertType.WARN)

    raise exception


def screenshot_error_report(exception):
    """
    Tries to save a screenshot and registers the error in the BotCity Orchestrator.
    Returns: None
    """
    try:
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_filepath = f".\\temp\\error-{date}.png"
        STATE.desktopbot.save_screenshot(screenshot_filepath)
        maestro.error(task_id=STATE.task_id, exception=exception,
                      screenshot=screenshot_filepath)
    except Exception as ex:
        logger.error(f"Error: {ex}. Uploading error without a screenshot.")
        # todo add extra tags item, etc.
        maestro.error(task_id=STATE.task_id, exception=exception)


def register_success(message):
    """
    Logs a successful item processing and records it in State and Datasource.
    """
    logger.info(f"Item processing successfull: item: {STATE.item}, {message}")
    STATE.register_success()
    data_source.report_success(message)

    # You can add more steps here if needed!
    # According to your business logic, what else should be done when an item
    # is processed successfully?
    ...
