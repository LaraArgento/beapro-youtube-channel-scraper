from framework.state import STATE
from framework.exceptions import BusinessException, SystemException, InterruptException
from framework.status_handling import handle_interrupt_requested, handle_business_exception, handle_system_exception, register_success
from framework.process import process_item
from framework.datasources import *
from framework.initialize import initialize
from framework.finalize import cleanup, finalize
import time

logger = logging.getLogger(__name__)

"""BeaPro Automation Outline

This is the main automation file that orchestrates the bot execution flow.
It handles initialization, item processing, exception handling, and finalization.

To customize your automation:
- Adjust initialization settings in framework/initialize.py
- Configure your data source in framework/datasources.py
- Add your automation steps in the process_item() function located in framework/process.py

The BeaPro framework automatically handles:
- System exceptions (technical failures with restart capability)
- Interruption requests from BotCity Orchestrator
- Success/error reporting and alerting
- Logging, and more. Read the Readme.md for more information.
"""


def action():
    try:
        initialize()

        for item in data_source:

            try:
                result_message = process_item(item)
            except InterruptException as ex:
                handle_interrupt_requested(ex)
            except BusinessException as ex:
                handle_business_exception(ex)
            except (SystemException, Exception) as ex:
                handle_system_exception(ex)
                initialize(restart=True)
            else:
                register_success(
                    f"Item processed successfuly: {result_message}")

    except Exception as ex:
        logger.error(f"Error: {ex}")

    finally:
        cleanup()
        finalize()


if __name__ == "__main__":
    action()
