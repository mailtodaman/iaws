import boto3
import logging
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.cache import cache
import datetime
# Initialize a logger

logger = logging.getLogger(__name__)



def create_s3_bucket(bucketName,aws_access_key_id,aws_secret_access_key,AWS_REGION):
    logger.info(AWS_REGION)
    client = boto3.client("s3", region_name=AWS_REGION,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    bucket_name = bucketName
    location = {'LocationConstraint': AWS_REGION}
    response = client.create_bucket(Bucket=bucket_name)
    logger.info("Amazon S3 bucket has been created")


def list_s3_bucket(aws_access_key_id,aws_secret_access_key):
    s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    cloudwatch = boto3.client('cloudwatch', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,region_name="eu-west-1")
    
    response = s3.list_buckets()

    bucket_list = []
    # bucket_info = {}
    for bucket in response['Buckets']:
        bucket_info = {}
        bucket_name=bucket['Name']
        bucket_info['Name'] = bucket_name     
        logger.info(bucket_name)   
        # Creation time
        try:
            response = s3.head_bucket(Bucket=bucket_name)
            creation_time = response['ResponseMetadata']['HTTPHeaders']['date']
            bucket_info['CreationTime'] = creation_time
            
        except Exception as e:
            logger.error(e)
        # bucket_info = s3.head_bucket(Bucket=bucket_name)
        # Get bucket versioning status
        # versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        try:
            versioning = s3.get_bucket_versioning(Bucket=bucket_name)
            bucket_info['Versioning'] = versioning.get('Status', 'Disabled')
        except Exception as e:
            logger.error("No Access to bucket")
            continue
        # Get bucket lifecycle configuration
        try:
            lifecycle = s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)         
            if 'Rules' in lifecycle:
                bucket_info['Lifecycle'] = lifecycle['Rules']
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                bucket_info['Lifecycle'] = "No LifeCycle"
            else:
                logger.error(e)
        # Get bucket policy
        try:
            policy = s3.get_bucket_policy(Bucket=bucket_name)['Policy']
            bucket_info['Policy'] = policy
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                
                bucket_info['Policy'] = "No policy"
            else:
                logger.error(e)
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
            logger.error(e)

        # Get bucket KMS encryption configuration
        try:
            encryption = s3.get_bucket_encryption(Bucket=bucket_name)
            if 'ServerSideEncryptionConfiguration' in encryption:
                pass
                # bucket_info['kms_encryption'] = encryption['ServerSideEncryptionConfiguration']
        except Exception as e:
            logger.error(e)
        
        # Get TAG information

        try:
            response = s3.get_bucket_tagging(Bucket=bucket_name)
            if 'TagSet' in response:
                bucket_tags = {tag['Key']: tag['Value'] for tag in response['TagSet']}
                # bucket_info['Tags']=bucket_tags
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchTagSet':
                
                bucket_tags=None
                # bucket_info['Tags']=None
            else:
                logger.error(e)
            
        # Transfer acceleration
        try:
            response = s3.get_bucket_accelerate_configuration(Bucket=bucket_name)
            if 'Status' in response:
                acceleration_status = response['Status']
                bucket_info['Acceleration Status'] = acceleration_status
               
            else:
                bucket_info['Acceleration Status'] = "Disabled"

        except Exception as e:
            logger.error(e)
        # Check encryption
        try:
            response = s3.get_bucket_encryption(Bucket=bucket_name)
            server_side_encryption_configuration = response.get('ServerSideEncryptionConfiguration')
            if server_side_encryption_configuration:
                bucket_info['Encryption'] = "Enabled"
                
            else:
                bucket_info['Encryption'] = "Disabled"
                logger.info(f"Encryption status: Disabled")
        except Exception as e:
            logger.error(e)


        # Get CORS configuration
        try:
            cors_info = s3.get_bucket_cors(Bucket=bucket_name)
            bucket_info['CORS'] = cors_info['CORSRules']
        except ClientError:
            bucket_info['CORS'] = 'No CORS Rules'   

        # Get public access block settings
        try:
            access_block_response = s3.get_public_access_block(Bucket=bucket_name)
            # print(access_block_response['PublicAccessBlockConfiguration'])
            bucket_info['PublicAccessBlockConfiguration'] = str(access_block_response['PublicAccessBlockConfiguration'])

            # bucket_info['PublicAccessBlockConfiguration']="error"
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                bucket_info['PublicAccessBlockConfiguration'] = 'Not Configured'
            else:
                logger.error(f"Error getting public access block info for bucket {bucket_name}: {e}")
        
  # Get Object Ownership settings
        try:
            ownership_controls = s3.get_bucket_ownership_controls(Bucket=bucket_name)
            bucket_info['ObjectOwnership'] = ownership_controls['OwnershipControls']['Rules'][0]
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchOwnershipControls':
                bucket_info['ObjectOwnership'] = 'Not Set'
            else:
                logger.error(f"Error getting object ownership for bucket {bucket_name}: {e}")
                bucket_info['ObjectOwnership'] = 'Error'

        # Get static website hosting info
        try:
            website_info = s3.get_bucket_website(Bucket=bucket_name)
            bucket_info['Website'] = website_info.get('IndexDocument', {'Suffix': 'Not Configured'})
        except ClientError:
            bucket_info['Website'] = 'Not Configured'

         # Get bucket size and total number of objects from CloudWatch
        size_datapoints = cloudwatch.get_metric_statistics(
            Namespace="AWS/S3",
            MetricName="BucketSizeBytes",
            Dimensions=[
              
                {"Name": "BucketName", "Value": bucket_name},
                {"Name": "StorageType", "Value": "StandardStorage"}
            ],
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=2),
            EndTime=datetime.datetime.utcnow(),
            Period=86400,
            Statistics=['Average']
        )['Datapoints']
        logger.info(size_datapoints)

        count_datapoints = cloudwatch.get_metric_statistics(
            Namespace="AWS/S3",
            MetricName="NumberOfObjects",
            Dimensions=[

                {"Name": "BucketName", "Value": bucket_name},
                {"Name": "StorageType", "Value": "AllStorageTypes"}
            ],
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=2),
            EndTime=datetime.datetime.utcnow(),
            Period=86400,
            Statistics=['Average']
        )['Datapoints']

        bucket_info['Size'] = size_datapoints[0]['Average'] if size_datapoints else 'Unknown'
        bucket_info['ObjectCount'] = count_datapoints[0]['Average'] if count_datapoints else 'Unknown'


        bucket_list.append(bucket_info)
    return bucket_list

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