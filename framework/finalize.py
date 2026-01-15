from .state import STATE
from botcity.maestro import *
from .logger import *
import logging
from .datasources import *
import glob
from pathlib import Path

logger = logging.getLogger(__name__)


'''
finalize.py
    Gracefully ends the automation process using Cleanup and Finalize steps.
'''


def cleanup():
    """
    Perform steps to gracefully clean up the environment, log out of systems, close apps, connections, sessions etc.
    """
    try:
        logger.info(f"Cleaning up...")
        # Logs out of systems
        # logger.info(f"Logging out of system/apps")
        ...

        # Close apps, connections, sessions etc
        if STATE.webbot:
            STATE.webbot.stop_browser()
            logger.info(f"Browser closed.")
    except Exception as ex:
        logger.error(f"Error during cleanup: {ex}")
        raise ex


def finalize():
    """
    Performs steps to finalize the automation process gracefully in the BotCity Orchestrator.
    Returns: None
    """
    try:
        logger.info(
            f"The automation process has finished. Task ID: {
                STATE.task_id}. {
                finish_status_message()}")

        # Send emails/Alerts
        # logger.info(f"Sending emails/alerts")
        ...

        try:
            STATE.maestro.new_log_entry(
                STATE.task_info().activity_name, {
                    "message": finish_status_message()})
        except Exception as ex:
            logger.error(
                f"Error while trying to create a new log entry in the BotCity Orchestrator: {ex}")

        # Upload output folder to BotCity Orchestrator as Result Files
        upload_output_orchestrator()

    except Exception as ex:
        logger.error(f"Error during finalize: {ex}")
        raise ex
    finally:
        finish_task_orchestrator()
        print(finish_status_message())


def upload_output_orchestrator():
    """
    Uploads the whole output folder to the BotCity Orchestrator.
    """
    try:
        logger.info(
            f"Uploading output to BotCity Orchestrator as Result Files...")
        for f in glob.iglob("./output/*"):
            fp = Path(f)
            STATE.maestro.post_artifact(
                task_id=STATE.task_id,
                artifact_name=fp.name,
                filepath=fp
            )

    except Exception as ex:
        print(f"Error uploading output to BotCity Orchestrator: {ex}")
        raise ex


def finish_task_orchestrator():
    """
    Finish task accordingly in the BotCity Orchestrator.
    Returns: None
    """
    try:
        STATE.maestro.finish_task(
            task_id=STATE.task_id,
            status=STATE.compute_finish_status(),
            message=finish_status_message(),
            total_items=STATE.total_items,
            processed_items=STATE.success_count,
            failed_items=STATE.error_count
        )

    except Exception as ex:
        print(f"Error finishing task in the BotCity Orchestrator: {ex}")
        raise ex


def finish_status_message() -> str:
    """
    Formats and outputs a simplified finish message.
    Returns: str: Message
    """
    try:
        msg = f''' Task Completed - Process: {STATE.task_info().activity_name}.
        In our run for task {STATE.task_id} we processed {STATE.total_items} items, from which {STATE.success_count} were with success.
        Check the Result Files for more details.
        '''
        # Append optional extra message from STATE.finish_message_extra if
        # present
        extra = getattr(STATE, "finish_message_extra", None)
        if extra:
            msg = msg + str(extra)
        return msg
    except Exception as ex:
        logger.error(f"Error generating finish status message: {ex}")
        return "Task completed. Check the Result Files for more details."
    # todo test error here


def append_finish_status_message(extra: str) -> None:
    """
    Append extra text to be included into finish_status_message.
    Stores a single string at STATE.finish_message_extra (concatenates with newlines).
    Will not add the text if an existing line is exactly the same (after trimming).
    """
    try:
        new = str(extra).strip()
        if not new:
            return
        current = getattr(STATE, "finish_message_extra", "")
        # check for exact duplicate among existing lines (trimmed)
        existing_lines = [line.strip()
                          for line in current.splitlines() if line.strip()]
        if new in existing_lines:
            logger.debug("Duplicate finish status message skipped.")
            return
        if current:
            STATE.finish_message_extra = f"{current} {new}"
        else:
            STATE.finish_message_extra = new
    except Exception as ex:
        logger.error(f"Error appending finish status message: {ex}")
