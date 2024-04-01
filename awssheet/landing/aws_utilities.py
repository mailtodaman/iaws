import re,json
import django
from django.core.cache import cache
import subprocess
import hashlib
import logging,os
import zipfile
import signal,yaml
import tempfile
from django.conf import settings
from django.utils.safestring import mark_safe
import openai
import time

import threading


def timeit(func):
    """
    Decorator that reports the execution time of the function.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Call the function being decorated
        end_time = time.time()  # Record the end time
        print(f"{func.__name__} executed in {end_time - start_time:.4f} seconds.")
        return result
    return wrapper

# def run_batch_command(command):
#     # Command to be executed
    

#     try:
#         # Run the command and capture the output
#         result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#         return result.stdout
#     except subprocess.CalledProcessError as e:
#         return f"An error occurred: {e.stderr}"

class FastProcess:
    def __init__(self, cmd, stdin=None, stdout=None, stderr=None, env=None):
        self.waited = False
        file_actions = []
        if stdin:
            file_actions.append((os.POSIX_SPAWN_DUP2, stdin.fileno(), 0))
        if stdout:
            self.stdout_file = tempfile.TemporaryFile(mode="w+")
            file_actions.append((os.POSIX_SPAWN_DUP2, self.stdout_file.fileno(), 1))
        if stderr:
            file_actions.append((os.POSIX_SPAWN_DUP2, stderr.fileno(), 2))
        self.pid = os.posix_spawnp(cmd[0], cmd, env if env else os.environ, file_actions=file_actions)

    def __del__(self):
        if not self.waited:
            os.kill(self.pid, signal.SIGTERM)

    def terminate(self):
        os.kill(self.pid, signal.SIGTERM)

    def signal(self, sig):
        os.kill(self.pid, sig)

    def wait(self):
        self.waited = True
        return os.WEXITSTATUS(os.waitpid(self.pid, 0)[1])

    def get_stdout(self):
        if hasattr(self, 'stdout_file'):
            self.stdout_file.seek(0)  # Move the file pointer to the beginning
            return self.stdout_file.read()
        else:
            return None  # No stdout redirection

def run_command_with_posix_spawnp(command, env=None):
    try:
        # Split the command if it's a string
        # Example usage:
        print(command + " & \ ")
        command = command.split()
        pid = FastProcess(command, stdout=True)
        pid.wait()  # Wait for the process to finish
        stdout_data = pid.get_stdout()
        # print("Stdout:", stdout_data)
        return stdout_data
    
    except FileNotFoundError as e:
        return f"Command not found: {command[0]}"
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

# command is cd /tmp/steampipe-mod-aws-compliance; steampipe query --output=json query.s3_bucket_mfa_delete_enabled
def run_batch_command(command,dir="/tmp/steampipe-mod-aws-compliance"):
    os.chdir(dir)
    cache_command=command+"-"+dir
    # Create a hash of the command to use as the cache key
    command_hash = hashlib.md5(cache_command.encode()).hexdigest()
    # command="steampipe query --output=json query.log_group_encryption_at_rest_enabled"
    command=command.split()
    # Check if the command result is already in the cache
    if cache.get(command_hash):
        logging.info("Cache used: %s", command)
        return cache.get(command_hash)

    try:
        logging.info("Cache unavailable: %s", command)
        # Run the command and capture the output
        result = subprocess.run(command,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # result = subprocess.run(command,  check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # logging.info("Cache unavailable result: %s", result)
        output = result.stdout
        # logging.info("Cache unavailable output: %s", output)
        # Store the result in the cache using the hash as the key
        cache.set(command_hash, output, timeout=settings.CACHE_TIMEOUT)  # Cache for 5 minutes
        return output
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"



# | Name                                                                                    |
# +-----------------------------------------------------------------------------------------+
# | query.account_alternate_contact_security_registered                                     |
# | query.account_part_of_organizations                                                     |
# | query.acm_certificate_expires_30_days                                                   |
# Converted to list

def convert_to_list(para):
    # Split the command output into lines
    lines = para.split("\n")
    # Extract the names from the lines
    names = []
    for line in lines:
        if "|" in line and "Name" not in line and "-" not in line:  # Exclude header and separators
            name = line.split("|")[1].strip()  # Extract the name and strip whitespace
            names.append(name)
    return names

def format_aws_string(input_data):
    # Handle common AWS service abbreviations
    abbreviations = {
        'ec2': 'EC2',
        's3': 'S3',
        'efs': 'EFS',
        'aws': 'AWS',
        'drs': 'DRS',
        'api': 'API',
        'vpc': 'VPC',
        'iam': 'IAM',
        'ecs': 'ECS',
        'elb':'ELB',
        'ebs':'EBS',
        'db': 'DB',
        'acl': 'ACL',
        'eks': 'EKS',
        'kms': 'KMS',
        'rds':'RDS',
        'sns':'SNS',
        'dms':'DMS',
        'ecr':'ECR',
        'cloudtrail':'CloudTrail',
        'acm':'ACM',
        'cloudwatch':'CloudWatch',
        'Guardduty':'GuardDuty',
        'sqs':'SQS',
        'ssm':'SSM',
        'elasticache':'Elasticache',
        'dynamodb':'DynamoDB',
        'codebuild':'CodeBuild',
        'dlm':'DLM',
        'autoscaling':'AutoScaling',
        'es':'ES',
        'emr':'EMR',
        'networkfirewall':'NetworkFirewall',
        'secretsmanager':'SecretManager',
        'codedeploy':'CodeDeploy',
        'apigateway':'APIGateway',
        'gcp':'GCP'

        # Add more abbreviations as needed
    }

    # Check if input_data is a string or a list
    if isinstance(input_data, str):
        return format_string(input_data, abbreviations)
    elif isinstance(input_data, list):
        return [format_string(item, abbreviations) for item in input_data]
    else:
        raise ValueError("Input data must be a string or a list of strings.")

def format_string(input_string, abbreviations):
    # Replace known abbreviations
    for abbr, full in abbreviations.items():
        input_string = re.sub(r'\b' + abbr + r'\b', full, input_string, flags=re.IGNORECASE)

    # Capitalize the first letter of each word and replace underscores with spaces
    transformed = ' '.join(word.capitalize() for word in input_string.split('_'))

    # Special handling to keep abbreviations uppercase
    for abbr in abbreviations.values():
        transformed = transformed.replace(abbr.capitalize(), abbr)

    return transformed

# # Test the function with a string
# test_string = "ec2_instance_details"
# print(format_aws_string(test_string))

# # Test the function with a list of strings
# test_list = ["ec2_instance_details", "s3_bucket_info"]
# print(format_aws_string(test_list))


# input S3
# output query.s3_
def transform_string_to_steampipe_compliance_query(input_string):
    # Convert the string to lowercase
    lowercase_string = input_string.lower()
    # Add 'query.' prefix and '_' suffix
    transformed_string = "query." + lowercase_string + "_"
    return transformed_string



# Python program to find a specific string in a list of strings and return results in a list

def find_string_in_list(target_string, string_list):
    # List to store the results
    results = []

    # Iterate over each string in the list
    for string in string_list:
        # Check if the target string is in the current string
        if target_string in string:
            results.append(string)

    return results


def list_files(directory):
    """
    List all files in a given directory.

    :param directory: Path to the directory whose files are to be listed.
    :return: List of file names contained in the directory.
    """
    files = []
    # Walk through the directory
    for filename in os.listdir(directory):
        # Join the two strings to form the full filepath.
        filepath = os.path.join(directory, filename)
        # Check if it's a file and not a directory
        if os.path.isfile(filepath):
            files.append(filename)
    
    return files


def remove_file_extension(filename):
    """
    Remove the file extension from a given filename.

    :param filename: The filename from which the extension is to be removed.
    :return: Filename without the extension.
    """
    # Find the last dot position
    last_dot_position = filename.rfind(".")
    # If there is no dot, or it's the first character, return the filename as is
    if last_dot_position == -1 or last_dot_position == 0:
        return filename
    # Return the filename up to the last dot
    return filename[:last_dot_position]

def remove_file_extension_from_list(filenames):
    """
    Remove the file extension from each filename in a given list.

    :param filenames: List of filenames from which the extensions are to be removed.
    :return: List of filenames without the extensions.
    """


    return [remove_file_extension(filename) for filename in filenames]


def convert_to_lowercase_and_remove_spaces(input_string):
    """
    Convert a string to lowercase and remove all spaces.

    :param input_string: The string to be converted.
    :return: Modified string with all lowercase characters and no spaces.
    """
    # Convert to lowercase
    lower_case_string = input_string.lower()
    # Remove spaces
    no_space_string = lower_case_string.replace(" ", "")
    return no_space_string


def get_summary_from_json(json_str):
    # Load JSON data
    data = json.loads(json_str)

    # Extract summary
    summary = data.get("summary", {}).get("status", {})
    
    # Create a dictionary for summary counts
    summary_counts = {
        'ok': summary.get("ok", 0),
        'info': summary.get("info", 0),
        'alarm': summary.get("alarm", 0),
        'skip': summary.get("skip", 0),
        'error': summary.get("error", 0)
    }

    return summary_counts


def generate_progress_bars(status_counts):
    """
    Generate HTML for Bootstrap 5 progress bars.

    :param status_counts: Dictionary containing status counts.
    :return: HTML string for progress bars.
    """
    total = sum(status_counts.values())
    progress_bars_html = ''

    for status, count in status_counts.items():
        percentage = (count / total * 100) if total > 0 else 0
        color = {
            'ok': 'bg-success',
            'info': 'bg-info',
            'alarm': 'bg-danger',
            'skip': 'bg-warning',
            'error': 'bg-secondary'
        }.get(status, 'bg-secondary')

        bar_html = f'''
            <div class="progress-bar {color}" role="progressbar" style="width: {percentage}%" aria-valuenow="{count}" aria-valuemin="0" aria-valuemax="{total}">
                {status.title()}: {count}
            </div>
        '''
        progress_bars_html += bar_html

    return mark_safe(f'<div class="progress">{progress_bars_html}</div>')

# Example usage in your Django view
# status_counts = {'ok': 19, 'info': 2, 'alarm': 43, 'skip': 0, 'error': 0}
# progress_bars_html = generate_progress_bars(status_counts)
#   <div class="container">
#         <h2>Compliance Status</h2>
#         {{ progress_bars_html|safe }}
#     </div>



def run_steampipe_query_to_json(query):
    command = ["steampipe", "query", query, "--output=json"]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout  # This is a JSON string
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error during query execution: {str(e)}")
        # return (f"Error during query execution: {str(e)}")
        

def get_compliance_json(json_str):
    # Load JSON data
    data = json.loads(json_str)

    # Initialize an empty list to store all results
    all_results = []

    # Check if 'groups' key is in the data
    if 'groups' in data and isinstance(data['groups'], list):
        for group in data['groups']:
            # Check if 'controls' key is in each group and is a list
            if 'controls' in group and isinstance(group['controls'], list):
                for control in group['controls']:
                    # Check if 'results' key is in each control and is a list
                    if 'results' in control and isinstance(control['results'], list):
                        # Add the results to the all_results list
                        all_results.extend(control['results'])

    return all_results


def extract_detailed_results(json_str):
    """
    Extract detailed result information (reason, resource, status, dimensions) from the JSON data.
    
    Args:
    json_str (str): A string representation of JSON data.
    
    Returns:
    list: A list of dictionaries, each containing reason, resource, status, and dimensions for each result.
    """
    data = json.loads(json_str)
    detailed_results = []

    def traverse_groups(groups):
        """
        Recursively traverse the nested groups and controls to find and extract details from results.
        
        Args:
        groups (list): The list of group objects to traverse.
        """
        for group in groups:
            # Process controls if present
            if 'controls' in group and isinstance(group['controls'], list):
                for control in group['controls']:
                    # Check for and process results
                    if 'results' in control and isinstance(control['results'], list):
                        for result in control['results']:
                            # Extract required details and add to the detailed_results list
                            if all(key in result for key in ['reason', 'resource', 'status', 'dimensions']):
                                detailed_results.append({
                                    'reason': result['reason'],
                                    'resource': result['resource'],
                                    'status': result['status'],
                                    'dimensions': result['dimensions']
                                })
            # Recursively process any nested groups
            if 'groups' in group and isinstance(group['groups'], list):
                traverse_groups(group['groups'])

    if 'groups' in data and isinstance(data['groups'], list):
        traverse_groups(data['groups'])

    return detailed_results



def flatten_json(data):
    def flatten(x, name='', out={}):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], f"{name}{a}_", out)
        elif isinstance(x, list):
            for i, a in enumerate(x):
                flatten(a, f"{name}{i}_", out)
        else:
            out[name[:-1]] = x
        return out

    return [flatten(item) for item in data]

def flatten_compliance_result(results):
    flattened_results = []

    for result in results:
        # Flatten the dimensions into the main dictionary
        flattened_result = {key: value for key, value in result.items() if key != 'dimensions'}
        for dimension in result.get('dimensions', []):
            flattened_result[dimension['key']] = dimension['value']

        flattened_results.append(flattened_result)

    return flattened_results


# INPUT  +--------------------------------------------------+------------------------------------------------------------+
# | Name                                             | Title                                                      |
# +--------------------------------------------------+------------------------------------------------------------+
# | benchmark.all_controls                           | All Controls                                               |
# | benchmark.audit_manager_control_tower            | AWS Audit Manager Control Tower Guardrails                 |
# | benchmark.cis_controls_v8_ig1                    | CIS Controls v8 IG1                                        |
# OUTPUT {benchmark.all_controls: "All controls",benchmark.audit_manager_control_tower:"AWS Audit Manager Control Tower Guardrails   " }

def parse_benchmark_table(table):
    lines = table.strip().split('\n')
    benchmark_dict = {}
    benchmark_list = []

    for line in lines:
        if line.startswith('|') and '|' in line[1:]:
            # Splitting the line and stripping whitespace
            parts = line[1:].split('|')
            if len(parts) >= 2:
                name = parts[0].strip()
                title = parts[1].strip()
                # Exclude the specific line with 'Name' as key and 'Title' as value
                if name.lower() != 'name' and title.lower() != 'title':
                    benchmark_dict = {
                        "table_name": name,
                        "table_description": title
                    }
                    benchmark_list.append(benchmark_dict)
    return benchmark_list

def process_json(json_data):
    """
    Recursively extracts 'results' from a JSON structure with nested 'groups' and 'controls'.

    :param json_data: JSON data represented as a Python dictionary.
    :return: A list of all 'results' extracted from the JSON data.
    """
    results = []

    # Function to handle nested 'groups'
    def handle_group(group):
        if 'controls' in group and group['controls']:
            for control in group['controls']:
                if 'results' in control and control['results']:
                    results.extend(control['results'])
        if 'groups' in group:
            for subgroup in group['groups']:
                handle_group(subgroup)

    # Start processing with the top-level group
    if 'groups' in json_data:
        for group in json_data['groups']:
            handle_group(group)

    return results

# Example usage:
# json_data = { ... }  # Your JSON data here
# extracted_results = extract_results(json_data)
# print(extracted_results)



def run_steampipe_query_for_platform(platform="aws"):
    if platform == "all":
        query = """
                SELECT 
                    obj_description((table_schema || '.' || table_name)::regclass) AS table_description, 
                    table_name 
                FROM 
                    information_schema.tables 
                WHERE 
                    table_schema IN ('aws', 'azure', 'gcp','kubernetes');
            """

    else:
        query = f"SELECT obj_description(('{platform}.' || table_name)::regclass) AS table_description, table_name FROM information_schema.tables WHERE table_schema = '{platform}';"
        print("THIS IS QUERY",query)
    command = ["steampipe", "query", query, "--output=json"]

    try:
        # Execute the command
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        # result=run_batch_command("steampipe query "+ query + "--output=json")
        print("result")
        # Parse the JSON output
        data = json.loads(result.stdout)

        # Save to a file
        # with open('output.json', 'w', encoding='utf-8') as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)

        # print("Output saved to output.json")
        return data
    except subprocess.CalledProcessError as e:
        print("Error during query execution:", e)
    # return "String return"




def read_and_cache_yaml(file_path, cache_duration=0):
    """
    Reads a YAML file and caches its contents using the file path as the cache key.

    :param file_path: Path to the YAML file.
    :param cache_duration: Cache duration in seconds.
    :return: The contents of the YAML file.
    """
    cache_key = file_path  # Using the file path as the cache key
    yaml_data = cache.get(cache_key)
    if not yaml_data:
        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
            cache.set(cache_key, yaml_data, cache_duration)
    return yaml_data








def find_all_occurrences_of_form_and_table(yaml_file, target_table_path, target_form_heading):
    matching_occurrences = []

    with open(yaml_file, 'r') as file:
        yaml_data = yaml.safe_load_all(file)
        
        for doc in yaml_data:
            if 'form_heading' in doc and 'table_path' in doc:
                if doc['table_path'] and doc['form_heading']:
                    if target_table_path in doc['table_path'] and doc['form_heading'] == target_form_heading:
                        matching_occurrences.append(doc)
    
    return matching_occurrences



def process_json_data_null_to_empty(data):
    """
    Process data for use in Handsontable by replacing all None values with empty strings.

    :param json_data: List of dictionaries representing the data.
    :return: Processed data with None values replaced by empty strings.
    """
    def replace_none(obj):
        if isinstance(obj, dict):
            return {k: replace_none(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_none(elem) for elem in obj]
        elif obj is None:
            return ""
        else:
            return obj

    return [replace_none(item) for item in data]


def convert_string_to_json(json_string):
    try:
        # Convert string to Python object (list or dict)
        json_data = json.loads(json_string)

        # Function to recursively convert None to empty string
        def replace_none(obj):
            if isinstance(obj, dict):
                return {k: replace_none(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_none(elem) for elem in obj]
            elif obj is None:
                return ""
            else:
                return obj

        # Apply the replacement function
        processed_data = replace_none(json_data)

        # Convert back to JSON string format
        return json.dumps(processed_data)
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {e}"


def add_quotes_to_json_objects(data):
    """
    Recursively adds quotes to JSON object values if they are JSON objects themselves.

    :param data: The JSON data (dict or list) to process.
    :return: The processed JSON data with quotes added where necessary.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                # Convert the JSON object to a string and add quotes
                data[key] = json.dumps(value)
            else:
                # Recurse into nested structures
                data[key] = add_quotes_to_json_objects(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = add_quotes_to_json_objects(item)

    return data

def get_command_to_run(data):
    """
    Extracts the 'command_to_run' value from a list of dictionaries.

    :param data: List of dictionaries containing configuration data.
    :return: The 'command_to_run' value if it exists, otherwise None.
    """
    for item in data:
        if 'command_to_run' in item:
            return item['command_to_run']
    return None


# postgresql_functions.py


from django.db import connections

def get_tablename_region_arns_old(arns, table_name_prefix):
    """
    Create PostgreSQL functions and retrieve table information (TableName, Region, ARN)
    based on ARNs and a specified table name prefix.

    Args:
        arns (list of str): A list of ARNs for which to retrieve table information.
        table_name_prefix (str): The prefix of table names to filter on.

    Returns:
        list of tuples: A list of tuples containing table information (TableName, Region, ARN).
    """
    print("get_tablename_region_arns",arns,table_name_prefix)
    table_info_list = []

    with connections['default'].cursor() as cursor:
        print("cursor",cursor)
        cursor.execute("""
                    SELECT table_name FROM information_schema.tables ;
                      """)
        query_result=cursor.fetchall()
        print("query_resukt",query_result)

    # Now you can call the get_table_info_from_arn function with ARNs to get the corresponding table information
    # for arn in arns:
    #     with connections['default'].cursor() as cursor:
    #         cursor.execute("SELECT * FROM get_table_info_from_arn(%s)", [arn])
    #         table_info = cursor.fetchone()
    #         if table_info:
    #             table_info_list.append(table_info)
    table_info_list=[]

    return table_info_list


def get_cached_table_names(table_starts_with, database_alias='default', cache_timeout=3000):
    """
    Fetches table names starting with a specified prefix from the cache or the database.

    :param table_starts_with: The prefix to search for in table names.
    :param database_alias: The database alias to use.
    :param cache_timeout: How long to cache the results, in seconds.
    :return: A list of table names.
    """
    cache_key = f'table_names_{table_starts_with}_{database_alias}'
    
    # Try to get the result from cache
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    # If not in cache, query the database
    with connections[database_alias].cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s;", [table_starts_with + '%'])
        query_result = cursor.fetchall()

    # Cache the result for future requests
    cache.set(cache_key, query_result, cache_timeout)

    return query_result



@timeit
def get_table_names_with_prefix_and_search(database_alias, table_starts_with, search_string, search_in_column, ignore_tables=None):
    # Open a cursor using the specified database connection
    # with connections[database_alias].cursor() as cursor:
    #     # Execute the SQL query to retrieve table names that start with the specified prefix
    #     cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s;", [table_starts_with + '%'])
        
    #     # Fetch all the results
    #     query_result = cursor.fetchall()
    query_result=get_cached_table_names(table_starts_with)
    # Extract and return the table names as a list
    table_names = [row[0] for row in query_result]
    
    # Filter the table names based on the search string and column
    filtered_tables = []
    for table_name in table_names:
        # Check if the table should be ignored
        if ignore_tables and table_name in ignore_tables:
            continue
        print("table_name",table_name)
        try:
            with connections[database_alias].cursor() as cursor:
                # Check if "region" and "arn" columns exist in the table
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = %s AND column_name IN ('region', 'arn');
                """, [table_name])
                columns_exist = cursor.fetchall()
                
                if len(columns_exist) == 2:  # Both "region" and "arn" columns exist
                    # Use placeholders for search_string and search_in_column

                    sql = f"SELECT region, arn FROM {table_name} WHERE {search_in_column} LIKE %s;"
                    cursor.execute(sql, [search_string])  # Use single quotes around search_string
                    result = cursor.fetchone()
                    if result:
                        print("result-------",result)
                        region, arn = result
                        filtered_tables.append((table_name, region, arn))
                        break
        except django.db.utils.OperationalError as e:
            # Check if the error message contains the specific message to be ignored
            if "AccessDeniedException: No default admin could be found" not in str(e):
                raise e  # Re-raise the exception if it's not the specific error to be ignored
    
    return filtered_tables



import concurrent.futures
from django.db import connections

def query_table(database_alias, table_name, search_in_column, search_string):
    try:
        with connections[database_alias].cursor() as cursor:
            # Check if "region" and "arn" columns exist in the table
            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = %s AND column_name IN ('region', 'arn');
            """, [table_name])
            columns_exist = cursor.fetchall()

            if len(columns_exist) == 2:  # Both "region" and "arn" columns exist
                sql = f"SELECT region, arn FROM {table_name} WHERE {search_in_column} LIKE %s LIMIT 1;"
                cursor.execute(sql, [search_string])
                return cursor.fetchone()
    except Exception as e:
        print(f"Error querying table {table_name}: {e}")
    return None

def get_table_names_with_prefix_and_search_with_thread(database_alias, table_starts_with, search_string, search_in_column, ignore_tables=None):
    # Retrieve table names
    with connections[database_alias].cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s;", [table_starts_with + '%'])
        table_names = [row[0] for row in cursor.fetchall()]

    # Filter out ignored tables
    if ignore_tables:
        table_names = [name for name in table_names if name not in ignore_tables]

    # Using ThreadPoolExecutor to query in parallel
    filtered_tables = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_table = {executor.submit(query_table, database_alias, table_name, search_in_column, search_string): table_name for table_name in table_names}

        for future in concurrent.futures.as_completed(future_to_table):
            table_name = future_to_table[future]
            result = future.result()
            if result:
                region, arn = result
                filtered_tables.append((table_name, region, arn))
                break  # Stop if data is found

    return filtered_tables




import json

def extract_arns(data_list):
    """
    Extracts all ARNs from a list of dictionaries.

    :param data_list: A list of dictionaries.
    :return: A list of ARN strings.
    """
    try:
        # Ensure data_list is a list
        if not isinstance(data_list, list):
            raise ValueError("Input must be a list")

        # Extract ARNs
        arns = [item['arn'] for item in data_list if 'arn' in item]

        return arns

    except ValueError as e:
        print(f"Error: {e}")
        return []




def run_terraformer_import_with_thread(cloud_provider, resources, regions, name, value, output_path, base_path="/tmp/terraformer", additional_options=""):
    """
    Runs the Terraformer import command with specified parameters and prints output dynamically.

    Args:
        cloud_provider (str), resources (str), regions (str), name (str), value (str), output_path (str): Parameters for Terraformer.
        base_path (str): Base path for the working directory.
        additional_options (str): Additional options for the Terraformer command.

    Returns:
        bool: True if the process completes successfully, False otherwise.
    """
    # Construct the working directory path
    working_directory = os.path.join(base_path, cloud_provider)

    original_directory = os.getcwd()
    print("ENV",env)
    try:
        # Change to the specified working directory
        os.chdir(working_directory)

        # Build the command
        cmd = [
            "terraformer",
            "import",
            cloud_provider,
            "--resources={}".format(resources),
            "--regions={}".format(regions),
            "--filter=\"Name={};Value='{}'\"".format(name, value),
            "-o", output_path
        ]

        # Add additional options if provided
        if additional_options:
            cmd += additional_options.split()

       
        # Execute the command and print output dynamically
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,env=env)

        # Function to continuously read and print output
        def print_output(stream):
            for line in iter(stream.readline, b''):
                print(line.decode().strip())

        # Start a thread to print stdout
        thread = threading.Thread(target=print_output, args=(process.stdout,))
        thread.start()

        # Wait for the process to complete and the thread to finish
        process.wait()
        thread.join()

        return process.returncode == 0

    except Exception as e:
        print("An error occurred: {}".format(e))
        return False
    finally:
        # Change back to the original directory
        os.chdir(original_directory)



@timeit
def run_terraformer_import(cloud_provider, resources, regions, name, value, output_path, base_path="/tmp/terraformer", additional_options=""):
    """
    Runs the Terraformer import command with specified parameters.

    Args:
        cloud_provider (str): Cloud provider for Terraformer (e.g., 'aws').
        resources (str): Resources to import (e.g., 's3').
        regions (str): AWS regions (e.g., 'eu-west-1').
        name (str): Filter name (e.g., 'arn').
        value (str): Filter value (e.g., 'arn:aws:s3:::prod-data-01').
        output_path (str): Path to store the generated Terraform files.
        base_path (str): Base path for the working directory.
        additional_options (str): Additional options for the Terraformer command.

    Returns:
        str: Output from the Terraformer command.
    """
    # Construct the working directory path
    working_directory = os.path.join(base_path, cloud_provider)

    original_directory = os.getcwd()
    


    try:
        # Change to the specified working directory
        os.chdir(working_directory)

        # Build the command
        cmd = [
            "terraformer",
            "import",
            cloud_provider,
            "--resources={}".format(resources),
            "--regions={}".format(regions),
            "--filter=\"Name={};Value='{}'\"".format(name, value),
            "-o", output_path
        ]

        # Add additional options if provided
        if additional_options:
            cmd += additional_options.split()

        # Execute the command
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if output:
            print("Output:\n", output.decode())
        if error:
            print("Error:\n", error.decode())

        if process.returncode != 0:
            return "Error occurred with exit code {}".format(process.returncode)

        return True

    except Exception as e:
        return "An error occurred: {}".format(e)
    finally:
        # Change back to the original directory
        os.chdir(original_directory)

import re

def replace_colons(input_string):
    """
    Replace all occurrences of ':' with '_' in the input string.
    If there are two or more ':' in a row, they are replaced with a single '_'.

    Args:
    input_string (str): The string to process.

    Returns:
    str: The processed string with ':' replaced by '_'.
    """
    # Replace two or more ':' with a single '_'
    modified_string = re.sub(r':{2,}', '_', input_string)
    
    # Replace remaining single ':' with '_'
    modified_string = re.sub(r':', '_', modified_string)

    return modified_string

def compress_directory(directory_path, ignore_list=[]):
    """
    Compress the specified directory into a ZIP file at the same location,
    ignoring files and folders specified in the ignore list.

    Args:
    directory_path (str): The path to the directory to be compressed.
    ignore_list (list): List of file and folder names to ignore.

    Returns:
    str: The path to the created ZIP file, or None if an error occurred.
    """
    if not os.path.isdir(directory_path):
        print(f"The specified path '{directory_path}' is not a directory.")
        return None

    # Name of the zip file will be the directory name
    zip_file_path = f"{directory_path}.zip"

    # Creating the zip file
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_list]

            for file in files:
                if file not in ignore_list:
                    # Create a relative path for files to maintain the directory structure
                    relative_path = os.path.relpath(os.path.join(root, file), os.path.dirname(directory_path))
                    zipf.write(os.path.join(root, file), arcname=relative_path)

    print(f"Directory '{directory_path}' has been compressed to '{zip_file_path}'")
    return zip_file_path



# Convert list to json for all_platforms webpage


# Always include a docstring in your functions
def query_openai_model(prompt, openapi_key, model="text-davinci-003" ):
    """
    Query an OpenAI GPT model with a given prompt. Automatically decides whether to use
    the standard completions endpoint or the chat completions endpoint based on the model.

    Parameters:
    - prompt (str): The prompt to send to the model.
    - model (str): The model to use for the query. Default is 'text-davinci-003'.

    Returns:
    - str: The model's response to the prompt, or an error message if the query fails.
    """
    # IMPORTANT: Replace 'your_api_key_here' with your actual OpenAI API key.
    openai.api_key = openapi_key
    
    try:
        
        # Check if the model is a chat model
        if "gpt-3.5-turbo" in model or "chat" in model:  # Add more chat models as needed
            # Use the chat completions API for chat models
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
        
            # Extracting chat response
            return response.choices[0].message['content']
        else:
            # Use the standard completions API for non-chat models
            response = openai.Completion.create(
                engine=model,
                prompt=prompt,
                max_tokens=100
            )
         
            return response.choices[0].text.strip()
    except Exception as e:
    
        # Handle any exceptions that occur during the API request
        print(f"An error occurred: {e}")
        return e

def list_openai_models():
    """
    List all models available in the OpenAI API.

    This function uses the OpenAI API to fetch and print a list of all models
    available to the user based on their API key.
    """
    # Set your OpenAI API key here

    try:
        # Fetch the list of available models
        models = openai.Model.list()

        # Print the list of model names
        print("Available models:")
        for model in models['data']:
            print(f"- {model['id']}")
    except Exception as e:
        # Handle any exceptions that occur during the API request
        print(f"An error occurred while fetching the model list: {e}")





