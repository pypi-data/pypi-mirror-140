from typing import Union, List

import pandas as pd

from google.cloud.aiplatform_v1.types import (
    featurestore_service as featurestore_service_pb2,
)
from google.cloud.aiplatform_v1 import FeaturestoreServiceClient
from google.cloud.aiplatform_v1.types import io as io_pb2
from google.cloud.aiplatform_v1.types import FeatureSelector, IdMatcher

from .utils import load_cfg
from .pattern.formatter import PatternFormatter


class Client:
    """Establish all the required connection to GCP resources"""

    def __init__(self):
        self.cfg = load_cfg()
        self.admin_client = self._establish_admin_client()
        self.base_resource_path = self.admin_client.common_location_path(
            self.cfg.env.gcp.project_id, self.cfg.env.gcp.region
        )

    def search(self, pattern: str) -> List:
        patterns_formatted: List[str] = PatternFormatter.format(pattern)
        results = []
        for pattern_formatted in patterns_formatted:
            request = featurestore_service_pb2.SearchFeaturesRequest(
                location=self.base_resource_path, query=pattern_formatted
            )
            _results = self.admin_client.search_features(request, timeout=10)
            results.extend(list(_results))

        return results

    def retrieve(self, features: Union[List, str]) -> pd.DataFrame:
        pass

    def _establish_admin_client(self):
        admin_client = FeaturestoreServiceClient(
            client_options={"api_endpoint": self.cfg.env.gcp.api_endpoint}
        )
        return admin_client
