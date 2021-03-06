#!/usr/bin/env python3

# Upload CSV files (raw data) to S3
# Author: AKT (November 2020)

import logging
import os

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(message)s', level=logging.INFO)

s3_client = boto3.client('s3')
ssm_client = boto3.client('ssm')


def main():
    params = get_parameters()

    # upload files
    dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path = f'{dir_path}/raw_data/'
    bucket_name = params['bronze_bucket']
    upload_directory(path, bucket_name)


def upload_directory(path, bucket_name):
    """Uploads a directory of raw CSV files to Amazon S3"""

    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                if file != '_placeholder' or file != '.DS_Store':  # ignore these files
                    file_directory = os.path.basename(os.path.dirname(os.path.join(root, file)))
                    if file == 'BreadBasket_DMS.csv':  # rename this file
                        key = f'{file_directory}/bakery.csv'
                    else:
                        key = f'{file_directory}/{file}'
                    s3_client.upload_file(os.path.join(root, file), bucket_name, key)
                    print(f"File '{key}' uploaded to bucket '{bucket_name}' as key '{key}'")
            except ClientError as e:
                logging.error(e)


def get_parameters():
    """Load parameter values from AWS Systems Manager (SSM) Parameter Store"""

    params = {
        'bronze_bucket': ssm_client.get_parameter(Name='/emr_demo/bronze_bucket')['Parameter']['Value'],
    }

    return params


if __name__ == '__main__':
    main()
