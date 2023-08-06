from __future__ import annotations
from badook_tests.dsl.summary import Summary
from badook_tests.dsl.checks import Calculation


class TimeSeriesAnalysisSummary(Summary):
    """ Time-series analysis module aims to analyze sequential data with time intervals. At the moment is supports
        the Hampel filter method for detecting outliers in time-series data.

        The Hampel filter algorithm goes through sliding windows of predefined size and
        calculates the following metrics for each window: median,
        median absolute deviation, and
        lower and upper boundaries (according to a predefined number of
        median absolute deviations allowed from the median)

          Attributes:
          window_size: int - The size of the sliding window that we want to calculate our metrics upon.
          n_mads_allowed: float - The number of median absolute deviations allowed from the sliding window's median.
          This, along with the window's median sets the boundaries.
          time_column: string - The time column name.
          agg: string - The aggregation function for groups. Can be either sum (default) or count.
          partitions: list - The partitions to bound the Hampel filter to run upon, i.e., groups that we wish to
          calculate the outliers separately for.

          Usage example:
          cls.context.set_project_name("sales_ts_anomalies")
          cls.time_series_analysis_summary = cls.context \
             .create_summary(name='time_series_analysis_summary', dataset='sales_processed_time_series')
          TimeSeriesAnalysisSummary(
            features="Sales", name='time_series_analysis_w_multiple_groups',
            window_size=4, n_mads_allowed=2) \
            .set_time_window(time_key="YearMonth", time_format="yyyy-MM-dd",  units="MONTH", number_of_units=1)\
            .group_by("Agency") \
            .partition_by("Agency") \
            .on(cls.time_series_analysis_summary)
          hampel_filter = self.time_series_analysis_summary.get_summary('time_series_analysis_w_multiple_groups')
          hampel_filter.is_outlier \
            .check(lambda _is_outlier: _is_outlier == 1).assert_with_tolerance(0.1)
        """

    def __init__(self, features: str, name: str, window_size: int, n_mads_allowed: float, time_column: str = None):
        """
        The constructor function for the TimeSeriesAnalysisSummary

        Args:
            features: The name of the feature to analyze using the Hampel filter.
            name: The name of the summary.
            window_size: The size of the sliding window that we want to calculate our metrics upon.
            n_mads_allowed: The number of median absolute deviations allowed from the sliding window's median.
            time_column: The time column name.

        Raises:
            Exception: If Feature name provided for the Hampel filter is not a string.
                """
        super().__init__(features, name)
        if not isinstance(features, str):
            raise Exception(
                "Feature name for Hampel filter must be a string")
        self.type = 'TimeSeriesAnalysisSummary'
        self.window_size = window_size
        self.n_mads_allowed = n_mads_allowed
        self.time_column = time_column
        self.partitions = None
        self.agg = None

    @property
    def value(self):
        return Calculation(self.data, 'value', self._ctx)

    @property
    def window_rolling_median(self):
        return Calculation(self.data, 'window_rolling_median', self._ctx)

    @property
    def window_rolling_mad(self):
        return Calculation(self.data, 'window_rolling_MAD', self._ctx)

    @property
    def window_lower_boundary(self):
        return Calculation(self.data, 'window_lower_boundary', self._ctx)

    @property
    def window_upper_boundary(self):
        return Calculation(self.data, 'window_upper_boundary', self._ctx)

    @property
    def is_outlier(self):
        return Calculation(self.data, 'is_outlier', self._ctx)

    def partition_by(self, *args) -> Summary:
        self.partitions = list(args)
        return self

    def set_agg(self, agg: str) -> Summary:
        self.agg = agg
        return self
