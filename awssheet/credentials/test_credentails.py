import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import openai
from openai.error import AuthenticationError
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from google.cloud import storage
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError
import os
import subprocess

import boto3
from botocore.exceptions import NoCredentialsError

def set_aws_credentials_with_cli(access_key_id, secret_access_key):
    """
    Sets the AWS credentials using the AWS CLI 'aws configure set' command.

    Parameters:
    - access_key_id (str): AWS Access Key ID.
    - secret_access_key (str): AWS Secret Access Key.
    """
    try:
        # Set AWS Access Key ID
        subprocess.run(['aws', 'configure', 'set', 'aws_access_key_id', access_key_id], check=True)
        
        # Set AWS Secret Access Key
        subprocess.run(['aws', 'configure', 'set', 'aws_secret_access_key', secret_access_key], check=True)
        
        print("AWS credentials have been set successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while setting AWS credentials: {e}")


def set_environment_variables(access_key, secret_key):
    """
    Sets environment variables for AWS credentials and corresponding Terraform variables.

    Parameters:
    access_key (str): AWS access key ID.
    secret_key (str): AWS secret access key.
    """
    command=['steampipe','service','restart']
    try:
        # Execute the command
     
        env = os.environ.copy()
        set_aws_credentials_with_cli(access_key,secret_key)
        subprocess.Popen(command,  env=env)

    except Exception as e:
        return None, str(e), 1

def f_test_aws_credentials(access_key, secret_key):
    try:
        print("Access key",access_key)
        s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        s3.list_buckets()  # Attempt a simple operation
        set_environment_variables(access_key,secret_key)
        return True
    except (NoCredentialsError, PartialCredentialsError):
        return False

def f_test_azure_credentials(client_id, client_secret, tenant_id, subscription_id):
    try:
        credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
        client = ResourceManagementClient(credential, subscription_id)
        client.resource_groups.list()  # Attempt a simple operation
        return True
    except Exception as e:
        return False

def f_test_gcp_credentials(json_path):
    """
    Tests Google Cloud Platform credentials by attempting to list storage buckets.

    Parameters:
    - json_path (str): The file system path to the Google Cloud credentials JSON file.

    Returns:
    - bool: True if credentials are valid and buckets can be listed, False otherwise.
    """
    print("Json_path", json_path)

    # Set environment variable for Google Cloud credentials
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = json_path

    # Restarting Steampipe service
    command = ['steampipe', 'service', 'restart']
    try:
        subprocess.run(command, check=True, env=os.environ.copy())
        print("Steampipe service restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart Steampipe service: {e}")
        return False

    try:
        # Load credentials and create a client for the storage service
        credentials = service_account.Credentials.from_service_account_file(json_path)
        storage_client = storage.Client(credentials=credentials)

        # Attempt a simple operation (list buckets)
        buckets = list(storage_client.list_buckets())
        print(f"Successfully listed {len(buckets)} buckets.")
        return True
    except DefaultCredentialsError:
        print("Failed to authenticate with the provided credentials.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

import openai
from openai.error import OpenAIError



def f_test_chatgpt_credentials(api_key):
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test message"}]
        )
        
        # Assuming the API either raises an exception on error,
        # or we manually inspect the response for error indicators.
        if hasattr(response, 'error') and response.error:  # Pseudo-code: adjust based on actual response structure
            print("API returned an error:", response.error.message)
            return False
        return True
    except openai.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        return False
    except openai.RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
        return False
    except openai.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
        return False
    except Exception as e:
        print("Exception caught during API call:", e)
        # Optionally, parse exception or error response here for more granularity
        return False

