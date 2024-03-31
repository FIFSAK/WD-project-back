# from django.test import TestCase
#
# # Create your tests here.
# import boto3
# from botocore.exceptions import NoCredentialsError
#
# try:
#     s3 = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='YOUR_SECRET_KEY')
#     response = s3.list_buckets()
#     for bucket in response['Buckets']:
#         print(f'Bucket Name: {bucket["Name"]}')
# except NoCredentialsError:
#     print("Credentials not available")
#
#

import psycopg2
import psycopg2.extras


def main():
    conn_string = "host='hh-pgsql-public.ebi.ac.uk' dbname='pfmegrnargs' user='reader' password='NWDMCE5xdipIjRrp'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # retrieve a list of RNAcentral databases
    query = "SELECT * FROM rnc_database"

    cursor.execute(query)
    for row in cursor:
        print(row)


if __name__ == "__main__":
    main()