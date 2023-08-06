from codecs import encode
from inspect import trace
from typing import Union, List

import pandas as pd

from google.cloud.aiplatform_v1.types import (
    featurestore_service as featurestore_service_pb2,
)
from google.cloud.aiplatform_v1 import FeaturestoreServiceClient
from google.cloud import bigquery

from .utils import load_cfg
from .pattern import PatternFormatter
from .entity_values import get_entity_list
from .request import RequestDataframeBuilder, Requester
from .retrieval import BigQueryTableRetriever

import logging
import logging.config
import os
import time

CUR_DIR = os.path.abspath(os.path.join(__file__, ".."))
logging.config.fileConfig(f"{CUR_DIR}/conf/logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class Client:
    """Establish all the required connection to GCP resources"""

    def __init__(self):
        logger.info("Initiating GCP resource clients...")
        self.cfg = load_cfg()
        self.admin_client = self._establish_admin_client()
        self.base_resource_path = self.admin_client.common_location_path(
            self.cfg.env.gcp.project_id, self.cfg.env.gcp.region
        )
        logger.info(f"Base Resource Path: {self.base_resource_path}")

        self.bq_client = bigquery.Client()

    def list_entities(self) -> List:
        resource_uri = (
            f"{self.base_resource_path}/featurestores/{self.cfg.feature_store.id}"
        )
        entities = self.admin_client.list_entity_types(parent=resource_uri)
        for entity in entities.entity_types:
            name = entity.name
            short_name = name.split("/")[-1]
            logger.info(f"Found entity: {short_name}")
        return entities

    def list_features(self, entity: str) -> List:
        uri = f"{self.base_resource_path}/featurestores/{self.cfg.feature_store.id}/entityTypes/{entity}"
        features = self.admin_client.list_features(parent=uri)
        return features

    def search(self, pattern: str) -> List:
        patterns_formatted: List[str] = PatternFormatter.format(pattern)
        results = []
        for pattern_formatted in patterns_formatted:
            logger.info(
                f"Sending SearchFeaturesRequest for pattern '{pattern_formatted}'..."
            )
            request = featurestore_service_pb2.SearchFeaturesRequest(
                location=self.base_resource_path, query=pattern_formatted
            )
            _results = self.admin_client.search_features(request, timeout=10)
            results.extend(list(_results))

        return results

    def retrieve(
        self,
        entity_type: str,
        features: Union[List, str, pd.DataFrame],
        entities: List = None,
    ) -> pd.DataFrame:

        if isinstance(features, str):
            features = [features]
        if isinstance(entities, pd.DataFrame):
            request_df = entities
            assert (
                entity_type in request_df.columns
            ), f"Entity column should have the same name as entity_type: {entity_type}"
        else:
            if entities is None:
                logger.info(f"No entities provided! Getting list of entities...")
                entities: List = get_entity_list(entity_type)
            request_df = RequestDataframeBuilder().build(
                entity_type=entity_type, entities=entities
            )

        try:
            request_table_uri = f"{self.cfg.env.gcp.project_id}.{self.cfg.feature_store.gcp.bigquery_dataset}.temp_request_{int(time.time())}"
            output_table_uri = f"{self.cfg.env.gcp.project_id}.{self.cfg.feature_store.gcp.bigquery_dataset}.temp_output_{int(time.time())}"
            requester = Requester(
                gcp_project_id=self.cfg.env.gcp.project_id,
                gcp_region=self.cfg.env.gcp.region,
                feature_store_id=self.cfg.feature_store.id,
                admin_client=self.admin_client,
            )
            requester.create_request(
                entity_type,
                features,
                request_df,
                request_table_uri,
                output_table_uri,
            )

            retriever = BigQueryTableRetriever()
            output_df = retriever.retrieve(output_table_uri)
            return output_df
        except Exception:
            # TODO: Add expiration option to the tables at creation
            import traceback

            logger.critical("Error while retrieving!")
            logger.critical(traceback.format_exc())
        finally:
            import glob

            # Clean up
            logger.debug("Removing temp tables...")
            self.bq_client.delete_table(request_table_uri, not_found_ok=True)
            self.bq_client.delete_table(output_table_uri, not_found_ok=True)
            for filename in glob.glob("temp_*"):
                os.remove(filename)

    def _establish_admin_client(self):
        admin_client = FeaturestoreServiceClient(
            client_options={"api_endpoint": self.cfg.env.gcp.api_endpoint}
        )
        return admin_client
