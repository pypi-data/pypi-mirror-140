from typing import List
from google.cloud import bigquery
import logging

logger = logging.getLogger(__file__)


class MerchantList:
    query = """
    SELECT distinct
        id,
        restaurantuid,
        restaurantname,
        country_code
    FROM
        `dataengineering-250604.sgaurora_chopereservedb.restaurant_info`
    where 1=1
        and not _fivetran_deleted
        and is_display
    """

    def __init__(self):
        pass

    def get(self) -> List:
        logger.info("Getting list of restaurantuids as merchant_uids...")
        bq_client = bigquery.Client()
        df = bq_client.query(self.query).to_dataframe()
        list_merchant = df["restaurantuid"].values
        return list_merchant
