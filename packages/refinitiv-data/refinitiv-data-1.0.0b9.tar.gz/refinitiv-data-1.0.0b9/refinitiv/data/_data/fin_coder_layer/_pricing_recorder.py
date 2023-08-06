import asyncio
import threading
import math

from datetime import datetime
from typing import Callable, List

import numpy as np
import pandas as pd
from refinitiv.data._data.delivery.stream import StreamEvent

from ..tools import ohlc, RepeatedTimer
from ..content.streaming import StreamingPrice
from ..core.session import get_default


class PricingRecorder:
    """
    Pricing recorder class allows to record updates from server.
    Create dataframes based on received updates.

    Parameters
    ----------

    stream : StreamingPrices
        StreamingPrices object

    """

    def __init__(self, stream: StreamingPrice):
        self._logger = get_default().logger()
        self._stream = stream
        self.is_running = False
        self._recorded_ohlc_data = None
        self._frequency = None
        self._count = None
        self._timer = threading.Event()
        self._event = threading.Event()
        self._recorded_updates = {}
        self._on_data = None
        self._message_index = 0
        self._calculate_ohlc_based_on_count = False
        self._duration = None
        self._repeat_is_running = False
        self._recorded_dataframes = []

    def _record_ohlc_data(self, df: "pd.Dataframe"):
        df.fillna(pd.NA, inplace=True)

        if self._recorded_ohlc_data is None:
            self._recorded_ohlc_data = df
        else:
            self._recorded_ohlc_data = self._recorded_ohlc_data.append(df)

    @staticmethod
    def _parse_input_frequency_and_duration(input_: str) -> int:
        last_char = input_[-1]
        if last_char not in ["s", "h", "d", "m"] and not input_.endswith("min"):
            raise ValueError(
                "Please provide 'duration' or 'frequency' value in "
                "valid format. For example: '10s', '2min', '1h'"
            )
        try:
            if "s" == last_char:
                input_ = int(input_[:-1])
            elif input_.endswith("min"):
                seconds = int(input_[:-3])
                input_ = seconds * 60
            elif "h" == last_char:
                seconds = int(input_[:-1])
                input_ = seconds * 3600
            elif "d" == last_char:
                seconds = int(input_[:-1])
                input_ = seconds * 3600 * 24
            elif "m" == last_char:
                seconds = int(input_[:-1])
                input_ = seconds * 3600 * 24 * 30
        except ValueError:
            raise ValueError(
                "Please provide 'duration' value"
                " in valid format. For example: '10s', '2min', '1h'"
            )

        return input_

    @staticmethod
    def _merge_dataframes(dfs: List[pd.DataFrame]) -> pd.DataFrame:
        df = dfs.pop()
        df = df.join(dfs, how="outer")  # noqa
        df = df.convert_dtypes()
        df.index.name = "Timestamp"

        df.ohlc = ohlc.__get__(df, None)
        return df

    @staticmethod
    def _create_df(
        _data: list, _timestamps: list, _fields: list, stream_name: str
    ) -> pd.DataFrame:
        _numpy_array = np.array(_data)
        _timestamp_array = np.array(_timestamps)

        if np.size(_numpy_array):
            dataframe = pd.DataFrame(
                _numpy_array, columns=_fields, index=_timestamp_array
            )
        else:
            dataframe = pd.DataFrame()

        dataframe.sort_index(inplace=True)
        dataframe.columns = pd.MultiIndex.from_product(
            [[stream_name], dataframe.columns]
        )
        return dataframe

    def _on_update_handler(self, stream: StreamingPrice, message: dict):
        message["Timestamp"] = datetime.now()
        if stream.name not in self._recorded_updates:
            self._recorded_updates[stream.name] = [message]
        else:
            self._recorded_updates[stream.name].append(message)

        if self._calculate_ohlc_based_on_count:
            self._message_index += 1

            if self._message_index == self._count:
                self._repeat()
                self._message_index = 0

    @staticmethod
    def _validate_count_argument(count):
        try:
            count = int(count)
        except ValueError:
            raise ValueError(
                "Invalid argument. Please provide 'count'"
                " in the following format: '10', '100', '500'"
            )

        if count <= 0:
            raise ValueError("Invalid argument. 'count' should be more then 0")

    def _validate_arguments(self, frequency: str, duration: str, count: str):
        if count != "1" and frequency != "tick":
            raise ValueError(
                "Please provide 'tick' value as frequency when you are using 'count' argument."
            )
        self._validate_count_argument(count)

        if duration and frequency != "tick":
            frequency = self._parse_input_frequency_and_duration(frequency)
            duration = self._parse_input_frequency_and_duration(duration)

            self._expected_count_of_callbacks = duration / frequency

            float_part, self._expected_count_of_callbacks = math.modf(
                self._expected_count_of_callbacks
            )

            self._callback_called_count = 0
            if duration % frequency:
                self._expected_count_of_callbacks += 1

            if frequency > duration:
                raise ValueError(
                    "Please check your arguments, 'duration'"
                    " should be higher that 'frequency'."
                )

    def record(
        self,
        frequency: str = "tick",
        duration: "str" = None,
        count: str = "1",
        on_data: Callable = None,
    ):
        """
        Starts recording updates from server and save it in memory

        Parameters
        ----------
        frequency : str, optional
            Using to calculate ohlc based on received updates during period that was provided
        duration : str, optional
            Duration of recording data. Could be provided in seconds, minutes, hours
        count : str, optional
            Count of ticks to record
        on_data : function, optional
             Callback which is calling with 'frequency' and receive dataframe
             with calculated ohlc from last updates and recorder object.
             Frequency has to be provided

        Returns
        -------
        Examples
        -------
        Start recording all updates during 15 seconds and calculate ohlc

        >>> import refinitiv.data as rd
        >>> stream = rd.open_pricing_stream(universe=['EUR='], fields=['BID', 'ASK', 'OPEN_PRC'])
        >>> stream.recorder.record(duration="15s")
        >>> stream.recorder.stop()

        >>> stream.close()
        >>> history = stream.recorder.get_history()
        >>> history.ohlc("5s")

        Start recording updates and calculate ohlc
        by using 'frequency' and call 'callback'
        function with updated ohlc dataframe every 5 seconds
        >>> import refinitiv.data as rd
        >>> stream = rd.open_pricing_stream(universe=['EUR='], fields=['BID', 'ASK', 'OPEN_PRC'])
        >>>
        >>>
        >>> def callback(dataframe, recorder):
        ...     print(dataframe)
        >>>
        >>> stream.recorder.record(frequency="5s", duration="15s", on_data=callback)
        >>> stream.recorder.stop()
        >>> stream.close()
        >>> history = stream.recorder.get_history()

        """
        self._validate_arguments(frequency, duration, count)
        self.is_running = True
        self._frequency = frequency
        self._duration = duration
        self._count = int(count)
        self._on_data = on_data

        for universe in self._stream.universe:
            stream: "StreamingPrice" = self._stream._streaming_prices_by_name[universe]
            stream._stream.on(StreamEvent.UPDATE, self._on_update_handler)
            stream._stream.on(StreamEvent.REFRESH, self._on_update_handler)

        if frequency == "tick" and self._count != 1:
            self._calculate_ohlc_based_on_count = True

        if frequency != "tick":
            frequency = self._parse_input_frequency_and_duration(frequency)
            self._return_callback_by_frequency(frequency)

        if duration:
            duration = self._parse_input_frequency_and_duration(duration)
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(duration))

            if frequency == duration and self._repeat_is_running:
                self._event.wait()

            if hasattr(self, "_repeated_timer"):
                if not self._repeated_timer.finished._flag and self._duration:
                    if (
                        self._expected_count_of_callbacks - 1
                        == self._callback_called_count
                    ):
                        self._repeat()

            self.stop()

    def _return_callback_by_frequency(self, frequency: int):
        self._repeated_timer = RepeatedTimer(function=self._repeat, interval=frequency)
        self._repeated_timer.start()

    @staticmethod
    def _retrieve_data_for_df(stream_data: List[dict], repeat: bool = False) -> tuple:
        _timestamps = []
        _data = []
        _fields = set()

        _fields.update(*(item["Fields"] for item in stream_data))
        _fields = list(_fields)

        for idx, record in enumerate(stream_data):
            if repeat and idx == 0:
                _timestamps.append(datetime.now())
            else:
                _timestamps.append(record["Timestamp"])

            rics_data = [record["Fields"].get(field) for field in _fields]
            _data.append(rics_data)

        return _timestamps, _data, _fields

    @staticmethod
    def _create_df_based_on_ticks(df):
        first_update = df.index[0]
        last_update = df.index[-1]
        time_delta = last_update - first_update

        if hasattr(time_delta, "days") and time_delta.days != 0:
            days = time_delta.days + 1
            days = str(days) + "D"
            df = df.ohlc(days, origin="end", call_from_recorder=True)
        elif hasattr(time_delta, "hours"):
            hours = time_delta.hour + 1
            hours = str(hours) + "H"
            df = df.ohlc(hours, origin="end", call_from_recorder=True)
        elif hasattr(time_delta, "minutes"):
            minutes = time_delta.minutes + 1
            minutes = str(minutes) + "min"
            df = df.ohlc(minutes, origin="end", call_from_recorder=True)
        else:
            seconds = time_delta.seconds + 1
            seconds = str(seconds) + "s"
            df = df.ohlc(seconds, origin="end", call_from_recorder=True)

        return df

    @staticmethod
    def _replace_values_by_nan(_data):
        for rics_data in _data:
            for idx, value in enumerate(rics_data):
                try:
                    if value is not None:
                        float(value)
                except ValueError:
                    rics_data[idx] = None

    def _repeat(self):
        self._repeat_is_running = True
        if hasattr(self, "_callback_called_count"):
            self._callback_called_count += 1

        if self._frequency != "tick" and self._duration:
            if self._expected_count_of_callbacks < self._callback_called_count:
                return

        dfs = []
        df = pd.DataFrame()

        for universe, stream_data in self._recorded_updates.items():
            _timestamps, _data, _fields = self._retrieve_data_for_df(stream_data, True)

            if self._frequency:
                self._replace_values_by_nan(_data)

            self._recorded_updates[universe] = []
            dataframe = self._create_df(_data, _timestamps, _fields, universe)
            dfs.append(dataframe)

        if dfs:
            df = self._merge_dataframes(dfs)
            self._recorded_dataframes.append(df)

        if not df.empty:
            if self._frequency == "tick":
                df = self._create_df_based_on_ticks(df)
            else:
                df = df.ohlc(self._frequency, origin="end", call_from_recorder=True)

        if (
            df.empty
            and isinstance(self._recorded_ohlc_data, pd.DataFrame)
            and not self._recorded_ohlc_data.empty
        ):
            empty_row = {}
            columns = [col for col in self._recorded_ohlc_data]
            for column in columns:
                empty_row[column] = np.nan

            _timestamps = np.array([datetime.now()])
            df = pd.DataFrame(empty_row, index=_timestamps)

        self._record_ohlc_data(df)

        if self._on_data:
            try:
                if not self._recorded_ohlc_data.empty:
                    self._recorded_ohlc_data.fillna(pd.NA, inplace=True)

                callback_thread = threading.Thread(
                    target=self._on_data, args=(self._recorded_ohlc_data, self)
                )
                callback_thread.start()

            except Exception as error:
                self._logger.exception("Error occurred in user's callback function.")
                self._logger.exception(error)

        if self._frequency == self._duration:
            self._event.set()

        self._repeat_is_running = False

    def get_history(self) -> "pd.DataFrame":
        dfs = []
        if self._frequency == "tick" and self._count == 1:
            for universe, stream_data in self._recorded_updates.items():
                _timestamps, _data, _fields = self._retrieve_data_for_df(stream_data)
                dataframe = self._create_df(_data, _timestamps, _fields, universe)
                dfs.append(dataframe)

            if not dfs:
                raise ValueError(
                    f"Cannot join dfs, because dfs list is empty, dfs={dfs}"
                )
            df = self._merge_dataframes(dfs)
        else:
            df = self._check_recorded_ohlc_df()
        return df

    def _check_recorded_ohlc_df(self) -> "pd.DataFrame":
        if isinstance(self._recorded_ohlc_data, pd.DataFrame):
            df = self._recorded_ohlc_data
            df.fillna(pd.NA, inplace=True)
        else:
            df = pd.DataFrame()
        return df

    def stop(self):
        if hasattr(self, "_repeated_timer"):
            self.is_running = False
            self._repeated_timer.cancel()
            self._event.clear()
            self._recorded_dataframes = []
