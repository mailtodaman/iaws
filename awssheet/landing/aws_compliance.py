import subprocess,json
from landing.aws_utilities import *
from landing.decorators import timing_decorator
from django.conf import settings
import json
from multiprocessing import Pool
import concurrent.futures







# Function to extract the first word after "." and "_"
# input query.rds_db_instance_deletion_protection_enabled   
# output rds

def extract_second_word(words):
    extracted_words = set()  # Use a set to avoid duplicates
    for word in words:
        # Split by "." then by "_" and take the second element
        first_word = word.split(".")[1].split("_")[0]
        extracted_words.add(first_word)
    return list(extracted_words)

# Get the list of first words



# input "cd /tmp/steampipe-mod-aws-compliance; steampipe query list"
# output +-----------------------------------------------------------------------------------------+
# | Name                                                                                    |
# +-----------------------------------------------------------------------------------------+
# | query.account_alternate_contact_security_registered                                     |
# | query.account_part_of_organizations                                                     |
# | query.acm_certificate_expires_30_days                                                   |
def available_compliance_list(command):
    command_output=run_batch_command(command)
    converted_list = convert_to_list(command_output)
    first_words_list=extract_second_word(converted_list)
    # Format the list
    formated_list=format_aws_string(first_words_list)
    return formated_list


def compliance_list(dir_path):
    # list all files
    files=list_files(dir_path)
    # remove any extension
    files=remove_file_extension_from_list(files)
   # Format the list
    formated_list=format_aws_string(files)
    return formated_list
    

# Input s3
# output 

# def create_aws_compliance_report(service_name):
#     final_results=[]
#     command=settings.STEAMPIPE_AWS_COMPLIANCE_LIST
#     string_of_all_compliances=run_batch_command(command)
#     list_of_all_compliances=convert_to_list(string_of_all_compliances)
#     query_servicename=transform_string_to_steampipe_compliance_query(service_name) #query.s3_
#     result=find_string_in_list(query_servicename,list_of_all_compliances)
#     print(result)
#     command=settings.STEAMPIPE_AWS_COMPLIANCES
#     for each_compliance in result:
#         print(each_compliance)
#         output=run_batch_command(command + " --output=json " + each_compliance)
#         try:
#         # Parse the JSON output
#             # parsed_json = json.loads(json_output)
#             # print(parsed_json)
#             # final_results.append(parsed_json)
#             compliance_data=eval(output)
#             final_results.extend(compliance_data) 
#         except json.JSONDecodeError:
#             print(f"Failed to parse JSON for {each_compliance}")
#     print("All data", final_results)
#     return final_results
 

def process_compliance_item(compliance_item):
    command = settings.STEAMPIPE_AWS_COMPLIANCES
    # output = run_batch_command(command + " --output=json " + compliance_item)
    environment = {'chdir': '/tmp/steampipe-mod-aws-compliance'}
    output = run_command_with_posix_spawnp(command + " --output=json " + compliance_item,environment)
    try:
        # Assuming the output is already in the correct Python list format
        compliance_data = eval(output)
        return compliance_data
    except SyntaxError as e:
        print(f"Failed to parse data for {compliance_item}: {e}")
        return []

# Main function to create complaince report
# Input service_name=s3


@timing_decorator
def create_aws_compliance_report(service_name):
    print("Hello")
    # STEAMPIPE_AWS_COMPLIANCE_LIST = "cd /tmp/steampipe-mod-aws-compliance; steampipe query list"
    command = settings.STEAMPIPE_AWS_COMPLIANCE_LIST
    string_of_all_compliances = run_batch_command(command)
    print("1")
    list_of_all_compliances = convert_to_list(string_of_all_compliances)
    print("2")
    # Create a list of compliance queries, in this case, s3 query.s3_
    query_servicename = transform_string_to_steampipe_compliance_query(service_name)
    print("3")
    # Find query.s3_ in all the compliance list
    result = find_string_in_list(query_servicename, list_of_all_compliances)
    print("4",result)
    # Using ProcessPoolExecutor to handle multiprocessing
    with concurrent.futures.ProcessPoolExecutor(max_workers=settings.CONCURRENT_MAX_WORKERS) as executor:
        # Map the process_compliance_item function to the result list for parallel execution
        compliance_data_lists = list(executor.map(process_compliance_item, result))
    # for i in result:
    #     compliance_data_lists=process_compliance_item(i)
    #     print("compliance_data_lists",compliance_data_lists)
    print("5")
    # Flatten the list of lists into a single list
    # final_results = [item for sublist in compliance_data_lists for item in sublist]
    if not compliance_data_lists:
        final_results = {}  # Create an empty JSON object
    else:
    # Flatten the list of lists into a single list
        final_results = [item for sublist in compliance_data_lists for item in sublist]
    print("6")

    # print("All data", final_results)
    print("hello-2")
    return final_results




@timing_decorator
def create_compliance_report(service_name,dir,format="json"):
    
    # change to smallcase
    
    service_name=service_name.lower()
    # STEAMPIPE_AWS_COMPLIANCE_LIST = "cd /tmp/steampipe-mod-aws-compliance; steampipe query list"
    command = settings.STEAMPIPE_AWS_COMPLIANCE_LIST
    json_of_all_compliances = run_batch_command(service_name+ " --output="+format,dir)
    # print("JSON_COMPLIANCE",json_of_all_compliances)
    status=get_summary_from_json(json_of_all_compliances)
    # final_results=get_compliance_json(json_of_all_compliances)
    final_results=extract_detailed_results(json_of_all_compliances)
    final_results=flatten_compliance_result(final_results) 
    print("final_results",final_results)
    # if not json_of_all_compliances:
    #     final_results = {}  # Create an empty JSON object
    return final_results,status

@timing_decorator
def create_benchmark_report(benchmark_name,dir,format="json"):
   
    # change to smallcase
    
    benchmark_name=benchmark_name.lower()
    # STEAMPIPE_AWS_COMPLIANCE_LIST = "cd /tmp/steampipe-mod-aws-compliance; steampipe query list"
    command = settings.STEAMPIPE_AWS_COMPLIANCE_LIST
    json_of_all_benchmark = run_batch_command(benchmark_name+ " --output="+format,dir)
    status=get_summary_from_json(json_of_all_benchmark)
    final_results=process_json(json.loads(json_of_all_benchmark))
    final_results=flatten_compliance_result(final_results) 
    if not json_of_all_benchmark:
        final_results = {}  # Create an empty JSON object
    return final_results,status




# def run_steampipe_query_to_json(query):
#     command = ["steampipe", "query", query, "--output=json"]
#     try:
#         result = subprocess.run(command, check=True, capture_output=True, text=True)
#         return result.stdout  # This is a JSON string
#     except subprocess.CalledProcessError as e:
#         raise Exception(f"Error during query execution: {str(e)}")

