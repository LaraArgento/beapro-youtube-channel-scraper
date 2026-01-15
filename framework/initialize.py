import logging
import shutil
from .exceptions import *
from .finalize import cleanup
from .logger import setup_botcity_log, setup_logger
from .state import STATE
from botcity.core import DesktopBot
from botcity.maestro import *
from botcity.web import Browser, By, WebBot
from pathlib import Path
# Imports WebDriver Manager for Firefox
from webdriver_manager.firefox import GeckoDriverManager

logger = logging.getLogger(__name__)

'''
initialize.py
    Starts the automation process by setting up the logger, cleaning the output directory, and opening the browser.
    Handles both initial startup and restart scenarios.

'''


def run_once():
    """
    Steps that will be performed once the automation starts, such as setting up the logger and cleaning the output directory.
    """
    try:
        setup_temp_folders()
        setup_logger()
        setup_botcity_log()
        execution = STATE.execution
        logger.info(
            f"Automation {
                STATE.task_info().activity_name} started. Task ID: {
                execution.task_id}")
        print(f"Task ID: {execution.task_id}")
        if execution.parameters:
            print(f"Task Parameters are: {execution.parameters}")
    except Exception as ex:
        raise ex


def initialize(restart: bool = False):
    """
    Initializes the automation process by setting up the logger, cleaning the output directory, and opening the browser.
    """
    try:
        STATE.raise_for_interrupt_requested()
        if restart:
            logger.info(
                f"Recovering from exception to continue processing remaining items...")
            cleanup()
        else:
            run_once()

        # Open apps/systems
        # logger.info(f"Opening apps...")
        ...

        # Log into apps/systems
        logger.info(f"Logging in...")
        ...

        init_webbot()
        init_desktopbot()
    except Exception as ex:
        raise ex


def init_webbot():
    """
    Instantiates BotCity's WebBot, installs the DriverManager and opens the browser.
    """
    STATE.webbot = WebBot()
    STATE.webbot.headless = False

    # Sets default browser to Firefox
    STATE.webbot.browser = Browser.FIREFOX

    # Installs the latest version indicating the WebDriver to be used by the
    # bot
    STATE.webbot.driver_path = GeckoDriverManager().install()


def init_desktopbot():
    """
    Instantiates BotCity's DesktopBot.
    """
    STATE.desktopbot = DesktopBot()


def setup_temp_folders():
    shutil.rmtree("./output", ignore_errors=True)
    Path("./output").mkdir(parents=True, exist_ok=True)
    # if Path("./temp").is_dir():
    shutil.rmtree("./temp", ignore_errors=True)
    Path("./temp").mkdir(parents=True, exist_ok=True)
