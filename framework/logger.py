import datetime
import logging
from .state import STATE
from botcity.maestro import *
from logging import basicConfig, getLogger

'''
Logger
    Configure logging for the automation process. This module sets up both file-based and BotCity logging.
    - Creates dated log files in the output directory
    - Sets up logging format with timestamps
    - Configures BotCity's built-in Execution Log 
    - Provides a reusable logger instance

    Usage:
        Import the logger in other files with:
        logger = logging.getLogger(__name__)
        logger.info(f"Add your message including {variables}.")
'''


logger = logging.getLogger(__name__)


def log_result_file() -> str:
    """
    Returns the path to the log file.
    """
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    task_id = STATE.task_id
    log_result_file = f".\\output\\Log_BotCity_task-{task_id}_date-{date}.log"
    return log_result_file


def setup_logger():
    """
    Setups Python logger.
    """
    log_file = log_result_file()
    basicConfig(filename=log_file,
                level=logging.INFO,
                datefmt='%Y-%m-%d %H:%M:%S',
                format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                encoding='utf-8'
                )
    logger.info(ascii_text)
    logger.info(f"Log created at {log_file}.")


def setup_botcity_log():
    try:
        STATE.maestro.new_log(STATE.task_info().activity_name, [
            Column("Message", "message", 100)])
        logger.info(
            f"BotCity log created \"{STATE.task_info().activity_name}\"")
    except Exception as ex:
        logger.error(
            f"{ex} (The log \"{STATE.task_info().activity_name}\" probably already exists.)")
        pass


ascii_text = r"""
!                                                                             
!  88888888ba                           88888888ba                            
!  88      "8b                          88      "8b                           
!  88      ,8P                          88      ,8P                           
!  88aaaaaa8P'   ,adPPYba,  ,adPPYYba,  88aaaaaa8P'  8b,dPPYba,   ,adPPYba,   
!  88"'''""8b,  a8P_____88  '      `Y8  88"'''"''    88P'   "Y8  a8"     "8a  
!  88      `8b  8PP"''''''  ,adPPPPP88  88           88          8b       d8  
!  88      a8P  "8b,        88,    ,88  88           88          "8a,   ,a8"  
!  88888888P"    `"Ybbd8"'  `"8bbdP"Y8  88           88           `"YbbdP"'   
!                                                                            
"""
