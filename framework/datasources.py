import datetime
import logging
from .state import STATE
from botcity.maestro import *
from botcity.plugins.csv import BotCSVPlugin

logger = logging.getLogger(__name__)

'''
datasources.py
    Sets up data sources. Provides ready-to-use DatapoolSource and CSVSource classes.
    To create your own data source class, inherit from BaseSource.
'''


class BaseSource():
    """Base source for batch processing of items."""

    def report_success(self, status_message):
        raise NotImplementedError

    def report_error(self, error_type, status_message):
        raise NotImplementedError


class DatapoolSource(BaseSource):
    def __init__(self, label: str):
        self.dp = STATE.maestro.get_datapool(label)
        self.current_item = None

    def __str__(self):
        return f"Datapool {self.dp.label}"

    def __iter__(self):
        return self

    def __next__(self):
        if not self.dp.is_active():
            logger.warning(
                f"Datapool {self.dp.label} isn't active. You can activate it in the BotCity Orchestrator.")
            raise StopIteration
        if not self.dp.has_next():
            logger.info(f"Datapool {self.dp.label} has no more items.")
            raise StopIteration
        item = self.dp.next(STATE.task_id)
        self.current_item = item
        STATE.item = item.values
        return item.values if item else None

    def report_success(self, status_message):
        if not self.current_item:
            return
        self.current_item.report_done(status_message)

    def report_error(self, error_type, status_message):
        if not self.current_item:
            return
        error_type_map = {
            "SYSTEM EXCEPTION": ErrorType.SYSTEM,
            "BUSINESS EXCEPTION": ErrorType.BUSINESS,
            "INTERRUPTION REQUESTED": ErrorType.SYSTEM
        }
        error_type_enum = error_type_map.get(error_type, ErrorType.SYSTEM)
        message = str(status_message)
        self.current_item.report_error(error_type_enum, message)


class CSVSource(BaseSource):
    def __init__(self, file: str):
        self._file = file
        self.csv = BotCSVPlugin()
        self.csv_out = BotCSVPlugin()
        self.csv.read(file)
        self.csv_out_file = self.csv_result_file()
        self.csv_out.set_header(
            self.csv.header + ["TIMESTAMP", "STATUS", "MESSAGE"])
        self.index = 0
        self.count = len(self.csv.as_dataframe().index)
        self.current_item = None

    def __str__(self):
        return f"CSV {self._file}"

    def __iter__(self):
        return self

    def __next__(self):
        """
        Fetch the next pending entry.
        Returns: item
        """
        if self.index >= self.count:
            logger.info(f"CSV {self._file} has no more items.")
            raise StopIteration
        item = self.csv.as_dataframe().loc[self.index].to_dict()
        self.index += 1
        STATE.item = item
        self.current_item = item
        return item

    def _report(self, status, status_message):
        if not self.current_item:
            return

        self.current_item.update({
            "TIMESTAMP": datetime.datetime.now().isoformat(),
            "STATUS": status,
            "MESSAGE": status_message
        })
        self.csv_out.add_row(self.current_item)
        self.csv_out.write(self.csv_out_file)

    def report_success(self, status_message):
        return self._report("SUCCESS", status_message)

    def report_error(self, error_type, status_message):
        return self._report(error_type, status_message)

    def csv_result_file(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        task_id = STATE.task_id
        csv_result_file = f"./output/CSV_BotCity_task-{task_id}_date-{date}.csv"
        return csv_result_file


"""
Setting Datasource: Datapool | CSV
"""

# data_source = DatapoolSource("BeaPro-YoutubeChannels")
data_source = CSVSource(r"./resources/datapool-input-channels-3.csv")
logger.info(f"Datasource set to {data_source}.")
