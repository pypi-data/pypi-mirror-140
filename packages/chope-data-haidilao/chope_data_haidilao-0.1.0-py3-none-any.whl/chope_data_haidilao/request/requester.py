from typing import List
import pandas as pd

from google.cloud.aiplatform_v1.types import (
    featurestore_service as featurestore_service_pb2,
)
from google.cloud.aiplatform_v1.types import io as io_pb2
from google.cloud.aiplatform_v1.types import FeatureSelector, IdMatcher

import sys
import os

CUR_DIR = os.path.abspath(os.path.join(__file__, "../../"))
sys.path.insert(0, CUR_DIR)
from utils import upload_request_df_to_bigquery

import logging

logger = logging.getLogger(__name__)


class Requester:
    def __init__(
        self,
        gcp_project_id: str,
        gcp_region: str,
        feature_store_id: str,
        admin_client,
    ):
        self.gcp_project_id = gcp_project_id
        self.gcp_region = gcp_region
        self.feature_store_id = feature_store_id
        self.admin_client = admin_client
        self.featurestore = self.admin_client.featurestore_path(
            gcp_project_id, gcp_region, feature_store_id
        )

    def create_request(
        self,
        entity_type: str,
        features: List[str],
        request_df: pd.DataFrame,
        request_table_uri: str,
        output_table_uri: str,
    ) -> str:
        logger.debug(f"request_df:\n{request_df.head(5)}")
        upload_request_df_to_bigquery(request_df, request_table_uri)
        batch_serving_request = featurestore_service_pb2.BatchReadFeatureValuesRequest(
            featurestore=self.featurestore,
            bigquery_read_instances=io_pb2.BigQuerySource(
                input_uri=f"bq://{request_table_uri}"
            ),
            destination=featurestore_service_pb2.FeatureValueDestination(
                bigquery_destination=io_pb2.BigQueryDestination(
                    output_uri=f"bq://{output_table_uri}"
                )
            ),
            entity_type_specs=[
                featurestore_service_pb2.BatchReadFeatureValuesRequest.EntityTypeSpec(
                    entity_type_id=entity_type,
                    feature_selector=FeatureSelector(
                        id_matcher=IdMatcher(ids=features)
                    ),
                )
            ],
        )

        logger.info("Awaiting request to be processed...")
        # Execute the batch read
        batch_serving_lro = self.admin_client.batch_read_feature_values(
            batch_serving_request
        )
        # This long runing operation will poll until the batch read finishes.
        result = batch_serving_lro.result()
        logger.info(f"Request process results: {result}")
