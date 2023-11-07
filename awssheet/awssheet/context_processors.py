import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def get_regions(request):
    try:
        AWS_ACCESS_KEY = request.session.get('aws_access_key_id')
        AWS_SECRET_KEY = request.session.get('aws_secret_access_key')
        AWS_REGION_NAME = "eu-west-1"
      
       
        if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
            raise ValueError("AWS credentials are not set in the session.")

        boto3.setup_default_session(
            aws_access_key_id=AWS_ACCESS_KEY, 
            aws_secret_access_key=AWS_SECRET_KEY, 
            region_name=AWS_REGION_NAME
        )

        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_regions()
        regions = [region['RegionName'] for region in response['Regions']]
       

    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Credentials Error: {e}")
        regions = []
    except Exception as e:
        print(f"An error occurred: {e}")
        regions = []
    
  
    return {'get_regions': regions}



