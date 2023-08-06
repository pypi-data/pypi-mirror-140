from abc import ABC, abstractmethod
from typing import Any, Dict

from graphdatascience.graph.graph_object import Graph
from graphdatascience.model.model import Model
from graphdatascience.query_runner.query_runner import QueryResult, Row


class TrainedModel(Model, ABC):
    @abstractmethod
    def _query_prefix(self) -> str:
        pass

    def metrics(self) -> Dict[str, Any]:
        return self._list_info()["modelInfo"]["metrics"]  # type: ignore

    def predict_stream(self, G: Graph, **config: Any) -> QueryResult:
        query = f"{self._query_prefix()}stream($graph_name, $config)"
        config["modelName"] = self.name()
        params = {"graph_name": G.name(), "config": config}

        return self._query_runner.run_query(query, params)

    def predict_mutate(self, G: Graph, **config: Any) -> Row:
        query = f"{self._query_prefix()}mutate($graph_name, $config)"
        config["modelName"] = self.name()
        params = {"graph_name": G.name(), "config": config}

        return self._query_runner.run_query(query, params)[0]
