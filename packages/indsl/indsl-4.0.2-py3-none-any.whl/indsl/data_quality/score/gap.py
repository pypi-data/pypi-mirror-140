# Copyright 2021 Cognite AS
from __future__ import annotations

from typing import List, Literal, Optional

import numpy as np
import numpy.typing as npt
import pandas as pd

from ...exceptions import UserValueError
from ...type_check import check_types
from ..gaps_identification import (
    gaps_identification_iqr,
    gaps_identification_modified_z_scores,
    gaps_identification_z_scores,
)
from .base import DataQualityScore, DataQualityScoreAnalyser


class GapDataQualityScore(DataQualityScore):
    @check_types
    def __init__(
        self, analysis_start: pd.Timestamp, analysis_end: pd.Timestamp, events: List[npt.NDArray[np.datetime64]]
    ):
        """Data class storing the result of a gap data quality analysis

        Args:
            analysis_start (pd.Timestamp): Analysis start time
            analysis_end (pd.Timestamp): Analysis end time
            events (list): List of gap events
                Represented as pairs of timestamps
            degradation (list): Degradation factors
        """
        for (gap_start, gap_end) in events:
            if gap_start > gap_end:
                raise UserValueError(
                    f"Expected start date of gap to be before end date, got gap_start='{gap_start}' and gap_end='{gap_end}'"
                )
            if gap_start < analysis_start or gap_end > analysis_end:
                raise UserValueError(
                    f"Expected gap to be in analysis window, got gap='{gap_start}-{gap_end}' and analysis_window='{analysis_start}-{analysis_end}'"
                )

        self.analysis_start = analysis_start
        self.analysis_end = analysis_end
        self.events = events
        total_timespan: pd.Timedelta = analysis_end - analysis_start
        self.degradation: list = [(gap[1] - gap[0]) / total_timespan for gap in events]

    @check_types
    def __add__(self, otherScore: GapDataQualityScore) -> GapDataQualityScore:
        """Return the union of two gap data quality score

        Args:
            otherScore (dict): Other gap data quality score

        Returns:
            DataQualityScore: The merged scores

        Raises:
            UserValueError: If the two input scores do not have a consequeny analysis window
        """
        if self.analysis_end != otherScore.analysis_start:
            raise UserValueError(
                f"Expected consecutive analysis periods in self and otherScore, got self.analysis_end='{self.analysis_end}' for score1 and otherScore.analysis_start='{otherScore.analysis_start}'"
            )

        gaps1 = self.events
        gaps2 = otherScore.events

        # Merge the last gap of first score with the
        # first gap of the second score if they are subsequent
        if len(gaps1) > 0 and len(gaps2) > 0 and gaps1[-1][1] == gaps2[0][0]:

            # Create copies of gap lists to avoid side effects
            gaps1 = gaps1.copy()
            gaps2 = gaps2.copy()
            last_gap = gaps1.pop()
            gaps2[0][0] = last_gap[0]

        return GapDataQualityScore(self.analysis_start, otherScore.analysis_end, gaps1 + gaps2)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, GapDataQualityScore):
            return (
                self.analysis_start == other.analysis_start
                and self.analysis_end == other.analysis_end
                and self.degradation == other.degradation
                and (np.asarray(self.events) == np.asarray(other.events)).all()
            )
        else:
            raise NotImplementedError(
                f"Equality comparision between type {type(self)} and {type(other)} is not implemented"
            )


class GapDataQualityScoreAnalyser(DataQualityScoreAnalyser):
    @check_types
    def __init__(self, series: pd.Series):
        """Gap based data quality scores

        Args:
            series (pd.Series): Series to be analysed

        raises:
            UserValueError: If the series has less than 2 values
            UserValueError: If series has no time index
        """
        super().__init__(series)

    @check_types
    def compute_score(
        self,
        analysis_start: pd.Timestamp,
        analysis_end: pd.Timestamp,
        gap_detection_method: Literal["iqr", "z_scores", "modified_z_scores"] = "iqr",
        **gap_detection_options: Optional[dict],
    ) -> GapDataQualityScore:
        """Compute the gap analysis score

        Args:
            analysis_start (pd.Timestamp): Analyis start time
            analysis_end (pd.Timestamp): Analyis end time
            gap_detection_method (str): Gap detection method
                Must be one of "iqr", "z_scores", "modified_z_scores"
            gap_detection_options (dict, optional): Arguments to gap detection method
                Provided as a keyword dictionary

        Returns:
            DataQualityScore: A GapDataQualityScore object

        raises:
            UserValueError: If analysis_start < analysis_end
            UserValueError: If the analysis start and end timestamps are outside the range of the series index
        """

        if analysis_start > analysis_end:
            raise UserValueError(
                f"Expected analysis_start < analysis_end, got analysis_start '{analysis_start}' and analysis_end '{analysis_end}'"
            )

        # Treat empty series as one gap
        if len(self.series) == 0:
            return GapDataQualityScore(
                analysis_start, analysis_end, [np.array([analysis_start.to_datetime64(), analysis_end.to_datetime64()])]
            )

        if analysis_start < self.series.index[0]:
            raise UserValueError(
                f"Expected analysis_start to be equal or after the first timestamp in series, got analysis_start={analysis_start} and series.index[0]={self.series.index[0]}"
            )
        if analysis_end > self.series.index[-1]:
            raise UserValueError(
                f"Expected analysis_end to be before or equal the last timestamp in series, got analysis_end={analysis_end} and series.index[-1]={self.series.index[-1]}"
            )

        self._gap_detection_methods = {
            "iqr": gaps_identification_iqr,
            "z_scores": gaps_identification_z_scores,
            "modified_z_scores": gaps_identification_modified_z_scores,
        }

        method = self._gap_detection_methods[gap_detection_method]
        gaps = method(self.series, **gap_detection_options)

        gaps_events = self._convert_gaps_series_to_events(gaps)
        gaps_events = self._filter_gaps_outside_analysis_period(gaps_events, analysis_start, analysis_end)
        # The first and last gap might range outside the analysis period. Let's fix this...
        gaps_events = self._limit_first_and_last_gaps_to_analysis_period(gaps_events, analysis_start, analysis_end)

        return GapDataQualityScore(analysis_start, analysis_end, gaps_events)

    @staticmethod
    def _convert_gaps_series_to_events(series) -> List[npt.NDArray[np.datetime64]]:
        # Each gap in the input series is represented as a consecutive (1, 1) pair.
        # Hence filtering the 1 values and re-arranging the associated index as pairs
        # yields a list of the (start, end) gap events.
        return list(series[series == 1].index.values.reshape(-1, 2))

    @staticmethod
    def _filter_gaps_outside_analysis_period(
        gaps: List[npt.NDArray[np.datetime64]], analysis_start: pd.Timestamp, analysis_end: pd.Timestamp
    ) -> List[npt.NDArray[np.datetime64]]:

        # Find index of first gap that ends within analysis period
        idx_start = 0
        for idx_start, (_, gap_end) in enumerate(gaps):
            if gap_end > analysis_start:
                break

        # Find index (by traversing the gaps from last to first) of last gap that starts within analysis period
        idx_end = 0
        for idx_end, (gap_start, _) in enumerate(reversed(gaps)):
            if gap_start < analysis_end:
                break
        idx_end = len(gaps) - idx_end

        return gaps[idx_start:idx_end]

    @staticmethod
    def _limit_first_and_last_gaps_to_analysis_period(
        gaps: List[npt.NDArray[np.datetime64]], analysis_start: pd.Timestamp, analysis_end: pd.Timestamp
    ) -> List[npt.NDArray[np.datetime64]]:

        if len(gaps) == 0:
            return gaps

        first_gap = gaps[0]
        first_gap[0] = max(first_gap[0], analysis_start)

        last_gap = gaps[-1]
        last_gap[1] = min(last_gap[1], analysis_end)

        return gaps
