import time
import os
import pandas as pd
from google.cloud import bigquery

import logging

# Need to add the project name as prefix so that we can set logger config for chope_data_haidilao when using the package
logger = logging.getLogger(f"chope_data_haidilao.{__name__}")


def load_cfg():
    from hydra import initialize_config_dir, compose
    from dotenv import load_dotenv

    load_dotenv()

    cur_dir = os.path.abspath(os.path.join(__file__, "../"))
    conf_dir = f"{cur_dir}/conf"

    with initialize_config_dir(config_dir=conf_dir):
        cfg = compose("config")

    return cfg


def upload_request_df_to_bigquery(df: pd.DataFrame, destination_table_uri: str):
    temp_local_path = f"temp_{int(time.time())}.parquet"
    logger.info(f"Create request file at {temp_local_path}...")
    df.to_parquet(temp_local_path, index=False)

    logger.info(f"Uploading {temp_local_path} to {destination_table_uri}...")
    upload_parquet_file_to_bq(temp_local_path, destination_table_uri)

    # TODO: Register this logger to chope_haidilao_data
    logger.debug(f"Deleting file {temp_local_path}...")
    os.remove(temp_local_path)


def upload_parquet_file_to_bq(file_path: str, destination_table_uri: str):
    client = bigquery.Client()
    project_id, dataset_name, table_name = destination_table_uri.split(".")
    dataset_full_name = f"{project_id}.{dataset_name}"
    dataset = bigquery.Dataset(dataset_full_name)
    table_ref = dataset.table(table_name)
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job_config.source_format = bigquery.SourceFormat.PARQUET

    logger.info(f"Uploading {file_path} to BigQuery table {destination_table_uri}...")
    with open(file_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, job_config=job_config)

    job.result()
    return job
