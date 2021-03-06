#!/usr/bin/env python3

# Analyze dataset and output results to CSV and Parquet
# Author: AKT (November 2020)

import argparse

from pyspark.sql import SparkSession


def main():
    args = parse_args()

    spark = SparkSession \
        .builder \
        .appName("bakery-sales") \
        .getOrCreate()

    df_bakery = spark.read \
        .format("parquet") \
        .load(f"s3a://{args.silver_bucket}/bakery/")

    df_sorted = df_bakery.cube("item").count() \
        .filter("item NOT LIKE 'NONE'") \
        .filter("item NOT LIKE 'Adjustment'") \
        .orderBy(["count", "item"], ascending=[False, True])

    # write parquet
    df_sorted.write.format("parquet") \
        .save(f"s3a://{args.gold_bucket}/bakery/bakery_sales/parquet/", mode="overwrite")

    # write single csv file for use with Excel
    df_sorted.coalesce(1) \
        .write.format("csv") \
        .option("header", "true") \
        .options(delimiter='|') \
        .save(f"s3a://{args.gold_bucket}/bakery/bakery_sales/csv/", mode="overwrite")


def parse_args():
    """Parse argument values from command-line"""

    parser = argparse.ArgumentParser(description="Arguments required for script.")
    parser.add_argument("--silver-bucket", required=True, help="Processed data location")
    parser.add_argument("--gold-bucket", required=True, help="Analyzed data location")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
