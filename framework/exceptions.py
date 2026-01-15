import logging

logger = logging.getLogger(__name__)

'''
Exceptions
    Custom exception hierarchy for categorizing bot errors:
    - BusinessException: For business logic and validation errors
    - SystemException: For technical/infrastructure failures
    - InterruptException: For process interruptions and cancellations
'''


class BusinessException(RuntimeError):
    ...


class SystemException(RuntimeError):
    ...


class InterruptException(RuntimeError):
    ...
