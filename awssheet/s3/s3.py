import boto3
import logging
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.cache import cache
# Initialize a logger
logging.basicConfig(level=logging.INFO)



def create_s3_bucket(bucketName,aws_access_key_id,aws_secret_access_key):
    client = boto3.client("s3", region_name=AWS_REGION,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    bucket_name = bucketName
    location = {'LocationConstraint': AWS_REGION}
    response = client.create_bucket(Bucket=bucket_name)
    print("Amazon S3 bucket has been created")


def list_s3_bucket(aws_access_key_id,aws_secret_access_key):
    s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    response = s3.list_buckets()
    # print("RESPONSE",response)
    bucket_list = []
    # bucket_info = {}
    for i,bucket in enumerate( response['Buckets']):
        # print(bucket, type(bucket))
        bucket_info = {}
        bucket_name=bucket['Name']
 
        bucket_info['Name'] = bucket_name
        
        
        # Creation time
        try:
            response = s3.head_bucket(Bucket=bucket_name)
            creation_time = response['ResponseMetadata']['HTTPHeaders']['date']
            bucket_info['CreationTime'] = creation_time
            logging.info(f"Bucket {bucket_name} Creation Time: {creation_time}")
        except Exception as e:
            print("")

        print("bUCKEt_INFO",bucket_info)
        # bucket_info = s3.head_bucket(Bucket=bucket_name)
        # Get bucket versioning status
        # versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        try:
            versioning = s3.get_bucket_versioning(Bucket=bucket_name)

        except Exception as e:
            print(f"An error occurred while retrieving bucket versioning: {e}")
            continue

        if 'Status' in versioning:
            bucket_info['Versioning'] = versioning['Status']
        else:
            bucket_info['Versioning'] = "Disabled"
        # Get bucket lifecycle configuration
        try:
            lifecycle = s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            print("LifeCycle",lifecycle)
            if 'Rules' in lifecycle:
                bucket_info['Lifecycle'] = lifecycle['Rules']
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                print(f"No lifecycle configuration found for bucket '{bucket_name}'")
                bucket_info['Lifecycle'] = "No LifeCycle"
            else:
                print(e)
        # Get bucket policy
        try:
            policy = s3.get_bucket_policy(Bucket=bucket_name)['Policy']
            bucket_info['Policy'] = policy
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                print(f"No bucket policy found for bucket '{bucket_name}'")
                bucket_info['Policy'] = "No policy"
            else:
                print(e)
        # Get bucket ACL
        acl = s3.get_bucket_acl(Bucket=bucket_name)['Grants']
        # bucket_info['acl'] = acl
        # Get bucket location
        location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        bucket_info['Location'] = location
        # Get bucket access logging configuration
        try:
            logging = s3.get_bucket_logging(Bucket=bucket_name)
            if 'LoggingEnabled' in logging:
                bucket_info['Access Logging'] = logging['LoggingEnabled']
            else:
                bucket_info['Access Logging'] = "Disabled"
        except Exception as e:
            print(f"Error retrieving access logging configuration: {e}")

        # Get bucket KMS encryption configuration
        try:
            encryption = s3.get_bucket_encryption(Bucket=bucket_name)
            if 'ServerSideEncryptionConfiguration' in encryption:
                pass
                # bucket_info['kms_encryption'] = encryption['ServerSideEncryptionConfiguration']
        except Exception as e:
            print(f"Error retrieving KMS encryption configuration: {e}")
        
        # Get TAG information

        try:
            response = s3.get_bucket_tagging(Bucket=bucket_name)
            if 'TagSet' in response:
                bucket_tags = {tag['Key']: tag['Value'] for tag in response['TagSet']}
                # bucket_info['Tags']=bucket_tags
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchTagSet':
                print(f"No tags found for bucket '{bucket_name}'")
                bucket_tags=None
                # bucket_info['Tags']=None
            else:
                print(e)
            
    # bucket_list.append(bucket_info)
    # print(bucket_list)
       
       
    
        # Transfer acceleration
        try:
            response = s3.get_bucket_accelerate_configuration(Bucket=bucket_name)
            if 'Status' in response:
                acceleration_status = response['Status']
                bucket_info['Acceleration Status'] = acceleration_status
                print(f"Transfer Acceleration status: {acceleration_status}")
            else:
                bucket_info['Acceleration Status'] = "Disabled"

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        

        # Check encryption
        try:
            response = s3.get_bucket_encryption(Bucket=bucket_name)
            server_side_encryption_configuration = response.get('ServerSideEncryptionConfiguration')
            if server_side_encryption_configuration:
                bucket_info['Encryption'] = "Enabled"
                logging.info(f"Encryption status: Enabled")
            else:
                bucket_info['Encryption'] = "Disabled"
                logging.info(f"Encryption status: Disabled")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")


        print("BUCKET INFO before append",bucket_info)
        bucket_list.append(bucket_info)


        
        # Create a 2D array with the keys and values of the dictionary
        # array_2d = [[key, value] for key, value in bucket_info.items()]
        # print(array_2d)

    return bucket_list


# create_S3_Bucket("hands-on-cloud-demo-bucket-jj2")
# print(list_s3())


# dict1 = {'a': 1, 'b': 2, 'c': 3}
# dict2 = {'a': 'apple', 'b': 'banana', 'c': 'cherry'}

# my_array = [[k, dict1[k], dict2[k]] for k in dict1.keys()]

# print(my_array)
# Cached the result
def list_s3_bucket_cached(aws_access_key_id,aws_secret_access_key):
    if cache.get('cached_result'):
        result = cache.get('cached_result')
    else:
        result = list_s3_bucket(aws_access_key_id,aws_secret_access_key)
        cache.set('cached_result', result, 600)  # cache for 60 seconds
    return result

def remove_s3_bucket(bucket_name,aws_access_key_id,aws_secret_access_key):
    s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    
    # Delete all objects in the bucket before deleting the bucket
    response = s3.list_objects_v2(Bucket=bucket_name)
    if 'Contents' in response:
        for obj in response['Contents']:
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])

    # Delete the bucket
    s3.delete_bucket(Bucket=bucket_name)
    return True