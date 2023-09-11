import json
import logging
from typing import Dict

import boto3
import pyspark.sql.functions as sf
from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

SNOWFLAKE_SOURCE_NAME = "net.snowflake.spark.snowflake"
SNOWFLAKE_SCHEMA = "JAN"


def get_snowflake_credentials():
    sms = boto3.client("secretsmanager", region_name="eu-west-1")
    secret = sms.get_secret_value(SecretId="snowflake/capstone/login")

    return json.loads(secret["SecretString"])


def get_spark_session(name: str = None) -> SparkSession:
    return (
        SparkSession.builder.config(
            "spark.jars.packages",
            ",".join(
                [
                    "org.apache.hadoop:hadoop-aws:3.3.5",
                    "net.snowflake:spark-snowflake_2.12:2.9.0-spark_3.1",
                    "net.snowflake:snowflake-jdbc:3.13.3",
                ]
            ),
        )
        .config(
            "fs.s3a.aws.credentials.provider",
            "com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
        )
        .appName(name)
        .getOrCreate()
    )


def snowflake_config() -> Dict[str, str]:
    credentials = get_snowflake_credentials()
    return {
        "sfURL": credentials["URL"],
        "sfUser": credentials["USER_NAME"],
        "sfPassword": credentials["PASSWORD"],
        "sfDatabase": credentials["DATABASE"],
        "sfWarehouse": credentials["WAREHOUSE"],
        "sfRole": credentials["ROLE"],
        "sfSchema": SNOWFLAKE_SCHEMA,
    }


if __name__ == "__main__":
    spark = get_spark_session("ingest")
    spark.sparkContext.setLogLevel("ERROR")

    logger.info("Reading data from S3...")
    df = spark.read.json("s3a://dataminded-academy-capstone-resources/raw/open_aq/")

    clean = df.select(
        [
            sf.col(colname)
            if df.schema[colname].dataType.typeName() != "struct"
            else sf.col(f"{colname}.*")
            for colname in df.columns
        ]
    )

    logger.info("Writing data to Snowflake...")

    clean.write.format(SNOWFLAKE_SOURCE_NAME).options(
        **snowflake_config()
    ).option("dbtable", "open_aq").mode("overwrite").save()

    logger.info("Done!")
