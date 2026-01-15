import logging
import os
from botcity.core import DesktopBot  # Import for Desktop Bot
from botcity.maestro import (AutomationTask, AutomationTaskFinishStatus,
                             BotMaestroSDK)
from botcity.web import WebBot  # Import for Web Bot
from dataclasses import asdict, dataclass, field
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

'''
state.py
    Implements a state management system that works seamlessly with BotCity Orchestrator features.
    The State class maintains the execution state of automation tasks, providing features such as:
        - Count successfull and failed items
        - Check for interruption request
        - Stores WebBot(), DesktopBot() instances
        - And more
'''

# aaaaaaaaaaaaaaaaaaa


@dataclass
class State:
    maestro: BotMaestroSDK = None
    task_id: str = ""
    item: dict = field(default_factory=dict)
    success_count: int = 0
    error_count: int = 0
    has_error: bool = False
    has_success: bool = False
    webbot: WebBot = None
    desktopbot: DesktopBot = None

    @property
    def total_items(self):
        """
        Sums success and error items.
        Returns: Total items.
        """
        return self.success_count + self.error_count

    def register_success(self):
        """
        Registers item success.
        """
        self.has_success = True
        self.success_count += 1

    def register_error(self):
        """
        Registers item error.
        """
        self.has_error = True
        self.error_count += 1

    def compute_finish_status(self) -> AutomationTaskFinishStatus:
        """
        Calculates the finish status of a task.
        Returns: AutomationTaskFinishStatus
        """
        if self.has_success and self.has_error:
            return AutomationTaskFinishStatus.PARTIALLY_COMPLETED
        elif self.has_error:
            return AutomationTaskFinishStatus.FAILED
        else:
            return AutomationTaskFinishStatus.SUCCESS

    def raise_for_interrupt_requested(self) -> bool:
        """
        Checks whether or not this task received an interrupt request.
        Returns: bool
        """
        task_info = self.maestro.get_task(self.task_id)
        if task_info.is_interrupted():
            raise InterruptException("Interrupt requested via BotCity.")
        return False

    def task_info(self) -> AutomationTask:
        """
        Returns details about a given task.
        Returns: AutomationTask
        """
        return self.maestro.get_task(self.task_id)

    def as_dict(self):
        """
        Returns:
            Dictionary representation of this object.
        """
        return asdict(self)


'''
Initializes the STATE variable based on the execution environment.
It checks if the bot is running in BotCity Runner environment or locally with/without authentication.
Returns: STATE
'''

load_dotenv()
SERVER = os.getenv('SERVER')
LOGIN = os.getenv('LOGIN')
KEY = os.getenv('KEY')
TASK_ID = os.getenv('TASK_ID')
try:
    if BotMaestroSDK.from_sys_args().server != '':
        STATE = State()
        STATE.maestro = BotMaestroSDK.from_sys_args()
        STATE.task_id = STATE.maestro.task_id
        STATE.execution = STATE.maestro.get_execution(STATE.task_id)
        print("\n ######### Bot is running in a BotCity Runner environment. \n")
    elif all((SERVER, LOGIN, KEY, TASK_ID)):
        # Set your credentials in the .env file order to run your bot locally
        # with connection to the Orchestrator.
        STATE = State()
        STATE.maestro = BotMaestroSDK()
        STATE.maestro.login(
            server=SERVER, login=LOGIN, key=KEY,)

        STATE.task_id = TASK_ID
        STATE.execution = STATE.maestro.get_execution(STATE.task_id)
        print("\n ######### Bot is running locally with connection to the Orchestrator. \n")
    else:
        raise Exception(
            "No valid .env configuration found. Set your credentials in the .env file order to run your bot locally.")
except Exception as e:
    # If any error occurs, we assume the bot is running locally without
    # authentication.
    print(f"Error: {e}")
    STATE = State()
    STATE.maestro = BotMaestroSDK()
    # Disable errors if we are not connected to the Orchestrator
    STATE.maestro.RAISE_NOT_CONNECTED = False
    # Opt-in to receive mock objects when not connected to the Orchestrator
    STATE.maestro.MOCK_OBJECT_WHEN_DISCONNECTED = True
    STATE.execution = STATE.maestro.get_execution(STATE.task_id)
    print("\n ######### Bot is running in test mode (locally without authentication). \n")
