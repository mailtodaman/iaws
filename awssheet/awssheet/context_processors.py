import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
# context_processors.py
import yaml,json
from django.core.cache import cache
from django.conf import settings

dynamic_form_file = settings.DYNAMIC_FORM

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

def dynamic_form_yaml_data_processor_yaml(request):
    file_path = dynamic_form_file
    cache_key = f"yaml_data_{file_path}"
    cache_duration = 0  # cache duration in seconds

    # Try to get data from cache
    data = cache.get(cache_key)

    # If not in cache, read the file and store in cache
    if data is None:
        try:
            with open(file_path, 'r') as file:
                # Load all documents from the YAML file
                documents = yaml.safe_load_all(file)
                # Convert the generator to a list
                data = list(documents)
            cache.set(cache_key, data, cache_duration)
        except FileNotFoundError:
            data = []

    return {
        'yaml_data': data
    }


def dynamic_form_yaml_data_processor(request):
    file_path = dynamic_form_file
    cache_key = f"yaml_data_{file_path}"
    cache_duration = 0  # cache duration in seconds

    # Try to get data from cache
    data = cache.get(cache_key)

    # If not in cache, read the file and store in cache
    if data is None:
        try:
            with open(file_path, 'r') as file:
                # Load all documents from the YAML file
                documents = yaml.safe_load_all(file)
                # Convert the generator to a list
                data = list(documents)
            # Convert data to JSON string for JavaScript compatibility
            data_json = json.dumps(data)
            cache.set(cache_key, data_json, cache_duration)
        except FileNotFoundError:
            data_json = '[]'

    return {
        'dynamic_form': data_json  # Return JSON string
    }
 
