"""
Module that define Analyzer base class to inherit when implementing a new data analysis methods.

Classes
-------
Analyzer
    Abstract base class for data analysis classes.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional
import numpy as np
    

class Analyzer(ABC):
    """
    Abstract base class for data analysis classes.
    Implement _analyze method with the desired method, return the result at the end.
    _pretreatment has to be override to any pretreatment to the analyzer.
    _posttreament has to be override for any postreatment to the analyzer or result.
    
    Attributes
    -------
    result (read-only)
    """
    _result: Optional[np.ndarray]

    def __init__(self) -> None:
        super().__init__()
        self._result = None

    def analyze(self, data: np.ndarray) -> np.ndarray:
        """
        Apply the analysis method to data. 
        Call _pretreatment, _analyze and _posttreatment.
        Results are stored inside result and returned.

        Parameters
        ----------
        data : np.ndarray
            Input data.

        Returns
        -------
        np.ndarray
            Data analysis results.
        """
        self._pretreatment(data)
        self._result = self._analyze(data)
        self._posttreatment(data)
        return self.result

    def _pretreatment(self, data: np.ndarray) -> None:
        """Method to apply any pretreatment.

        Parameters
        ----------
        data : np.ndarray
            Input data.
        """
        ...
    
    @abstractmethod
    def _analyze(self, data: np.ndarray) -> np.ndarray:
        """Method where implement method.

        Parameters
        ----------
        data : np.ndarray
            Input data

        Returns
        -------
        np.ndarray
            Data analysis results.
        """
        ...

    def _posttreatment(self, data: np.ndarray) -> None:
        """Method to apply any posttreatmnent.

        Parameters
        ----------
        data : np.ndarray
            Input data.
        """
        ...

    @property
    def result(self) -> Optional[np.ndarray]:
        """Optional[np.ndarray]: Method results (read-only)."""
        return self._result
