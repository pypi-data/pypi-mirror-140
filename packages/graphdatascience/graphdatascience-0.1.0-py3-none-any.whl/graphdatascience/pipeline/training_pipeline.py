from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from graphdatascience.model.trained_model import TrainedModel

from ..graph.graph_object import Graph
from ..model.model import Model
from ..query_runner.query_runner import QueryRunner, Row


class TrainingPipeline(Model, ABC):
    @abstractmethod
    def _query_prefix(self) -> str:
        pass

    @abstractmethod
    def _create_trained_model(
        self, name: str, query_runner: QueryRunner
    ) -> TrainedModel:
        pass

    def addNodeProperty(self, procedure_name: str, **config: Any) -> Row:
        query = f"{self._query_prefix()}addNodeProperty($pipeline_name, $procedure_name, $config)"
        params = {
            "pipeline_name": self.name(),
            "procedure_name": procedure_name,
            "config": config,
        }
        return self._query_runner.run_query(query, params)[0]

    def configureParams(self, parameter_space: List[Dict[str, Any]]) -> Row:
        query = (
            f"{self._query_prefix()}configureParams($pipeline_name, $parameter_space)"
        )
        params = {
            "pipeline_name": self.name(),
            "parameter_space": parameter_space,
        }
        return self._query_runner.run_query(query, params)[0]

    def train(self, G: Graph, **config: Any) -> Tuple[TrainedModel, Row]:
        query = f"{self._query_prefix()}train($graph_name, $config)"
        config["pipeline"] = self.name()
        params = {
            "graph_name": G.name(),
            "config": config,
        }

        result = self._query_runner.run_query(query, params)[0]

        return (
            self._create_trained_model(config["modelName"], self._query_runner),
            result,
        )

    def configureSplit(self, **config: Any) -> Row:
        query = f"{self._query_prefix()}configureSplit($pipeline_name, $config)"
        params = {"pipeline_name": self.name(), "config": config}

        return self._query_runner.run_query(query, params)[0]

    def node_property_steps(self) -> List[Dict[str, Any]]:
        return self._list_info()["modelInfo"]["featurePipeline"]["nodePropertySteps"]  # type: ignore

    def split_config(self) -> Dict[str, Any]:
        return self._list_info()["modelInfo"]["splitConfig"]  # type: ignore

    def parameter_space(self) -> List[Dict[str, Any]]:
        return self._list_info()["modelInfo"]["trainingParameterSpace"]  # type: ignore
