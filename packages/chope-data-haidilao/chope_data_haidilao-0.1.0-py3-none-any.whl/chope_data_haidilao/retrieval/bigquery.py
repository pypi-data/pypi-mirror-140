from google.cloud import bigquery
import logging

logger = logging.getLogger(__name__)


class BigQueryTableRetriever:
    def __init__(self):
        self.bq_client = bigquery.Client()

    def retrieve(self, table_uri: str):
        logger.info("Downloading features...")
        query = f"select * from {table_uri}"
        df = self.bq_client.query(query).to_dataframe()
        return df
