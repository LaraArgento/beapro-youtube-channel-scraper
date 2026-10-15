from os import getenv
from dotenv import load_dotenv

load_dotenv()


def get_env_credentials():
    """
    Returns LOGIN, KEY, SERVER and TASK_ID env credentials for maestro.
    TASK_ID is only required for local development runs.
    """

    return getenv("LOGIN", ""), getenv("KEY", ""), getenv("SERVER", ""), getenv("TASK_ID", "")
