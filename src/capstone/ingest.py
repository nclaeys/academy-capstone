import json
import logging

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

    credentials = json.loads(secret["SecretString"])
    return credentials


if __name__ == "__main__":
    spark = (
        SparkSession.builder.config(
            "spark.jars.packages",
            ",".join(
                [
                    "org.apache.hadoop:hadoop-aws:3.3.2",
                    "net.snowflake:spark-snowflake_2.12:2.9.0-spark_3.1",
                    "net.snowflake:snowflake-jdbc:3.13.3",
                ]
            ),
        )
        .config(
            "fs.s3a.aws.credentials.provider",
            "com.amazonaws.auth.InstanceProfileCredentialsProvider,com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
        )
        .getOrCreate()
    )

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
    credentials = get_snowflake_credentials()

    sfOptions = {
        "sfURL": credentials["URL"],
        "sfUser": credentials["USER_NAME"],
        "sfPassword": credentials["PASSWORD"],
        "sfDatabase": credentials["DATABASE"],
        "sfWarehouse": credentials["WAREHOUSE"],
        "sfRole": credentials["ROLE"],
        "sfSchema": SNOWFLAKE_SCHEMA,
    }

    clean.write.format(SNOWFLAKE_SOURCE_NAME).options(**sfOptions).option(
        "dbtable", "open_aq"
    ).save()

    logger.info("Done!")
