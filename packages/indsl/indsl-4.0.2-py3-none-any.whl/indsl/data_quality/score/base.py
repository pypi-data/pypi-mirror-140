# Copyright 2021 Cognite AS
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

import pandas as pd

from ...validations import validate_series_has_time_index


@dataclass  # type: ignore
class DataQualityScore(ABC):
    """Data class storing the result of a data quality analysis

    Args:
        analysis_start (pd.Timestamp): Analysis start time
        analysis_end (pd.Timestamp): Analysis end time
        events (list): List of events
            The list items depend on the data quality algorithm
        degradation (list): Degradation factors
    """

    analysis_start: pd.Timestamp
    analysis_end: pd.Timestamp
    events: list
    degradation: List[float]

    @abstractmethod
    def __add__(self, otherScore: DataQualityScore) -> DataQualityScore:
        """Return the union of two data quality score

        Args:
            otherScore (dict): Other score

        Returns:
            DataQualityScore: The merged scores
        """
        pass

    @property
    def data_quality_score(self) -> float:
        """Return the degradation score calculated as 1-sum(degradation)"""
        return 1.0 - sum(self.degradation)


class DataQualityScoreAnalyser(ABC):
    def __init__(self, series: pd.Series):
        """Object to calculate data quality scores

        Args:
            series (pd.Series): time series

        Raises:
            UserValueError: If series has no time index
        """
        validate_series_has_time_index(series)

        self.series = series

    @abstractmethod
    def compute_score(self, analysis_start: pd.Timestamp, analysis_end: pd.Timestamp) -> DataQualityScore:
        """Compute data quality score

        Args:
            analysis_start (pd.Timestamp): analyis start time
            analysis_end (pd.Timestamp): analyis end time

        Returns:
            DataQualityScore: A DataQualityScore object
        """
        pass
