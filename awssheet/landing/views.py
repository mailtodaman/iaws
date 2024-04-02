from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from django.http import JsonResponse
from .forms import LoginForm
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import time
import datetime
import concurrent.futures
import subprocess
import re
from logs.models import LogsModel

import boto3
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import landing.aws_utilities
import landing.aws_compliance

from django.shortcuts import render
from django.http import  HttpResponse
from django.shortcuts import render
from .forms import DynamicForm
import os
import yaml
import fcntl
from django.shortcuts import render
from django.http import HttpResponse
import platform
from django.http import HttpResponse
from wsgiref.util import FileWrapper
import mimetypes
import os

dynamic_form_file = settings.DYNAMIC_FORM
dashboard_file=settings.IAWS_DASHBOARD
config_file = settings.CONFIG_FILE_PATH
command_outputs = {}

# views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import subprocess

from django.conf import settings
import uuid
from django.shortcuts import render
import landing.aws_utilities  # Assuming this is a module you have
import json
import time  # Import the time module



def login_view(request):
    """
    Handle the login process. This view authenticates a user and starts a session.
    The session expiry is controlled by SESSION_COOKIE_AGE in settings.py.
    
    Args:
    request: HttpRequest object
    
    Returns:
    HttpResponse object pointing to the login page with or without errors based on authentication result.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # This starts the session
                # Redirect to a success page.
                return redirect('index/')
            else:
                # Return an 'invalid login' error message.
                return render(request, 'landing/login.html', {'form': form, 'error': 'Invalid username or password.'})
    else:
        form = LoginForm()
    return render(request, 'landing/login.html', {'form': form})

def json_to_html_table(data):
    # Check if the data is a string and parse it as JSON
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return "<p>Invalid JSON data</p>"

    # Check if data is not empty
    if not data:
        return "<p>No data available</p>"

    categories = ["s3", "cost", "api", "lambda", "ec2", "efs", "rds", "vpc", "iam", "ecs", "ecr", "eks", "route53", "glue", "kms", "backup", "cloudwatch",
                  "redshift", "cloudtrail", "ebs", "cloudformation", "dynamodb", "opensearch", "sqs", "sns", "ses", "sso", "codedeploy","billing",
                  "inspector", "codebuild", "ssm", "guardduty", "inspector", "config", "elasticache", "drs", "dax", "cloudfront", "kinesis", "audit", "account",
                  "waf", "cognito", "step", "emr", "elasticssearch","kubernetes" ,"compute","dns","sql","bigquery","logging","monitoring","pub","redis","misc"]
    categorized_data = {category: [] for category in categories}

    # Categorize data
    for item in data:
        matched = False
        for category in categories[:-1]:  # Exclude 'misc' from this loop
            if category in item.get('table_name', '').lower():
                categorized_data[category].append(item)
                matched = True
                break
        if not matched:
            categorized_data['misc'].append(item)

    # Build tables for each category
    html_tables = '<div class="container-fluid"><div class="row">'
    count = 0
    for category, items in categorized_data.items():
        if items:  # Only build a table if there are items in the category
            if count % 3 == 0 and count != 0:
                html_tables += '</div><div class="row">'  # New row after every 3 tables
            count += 1

            html_tables += f'<div class="col-md-4"><h3>{category.upper()}</h3>'
            html_tables += '<table class="table table-hover"><thead><tr><th>Tables</th></tr></thead><tbody>'
            for row in items:
                value = row.get('table_name', '')

                url = f"/table/{value}"
                print("URL",url)
                link_text = row.get('table_description', '')
                html_tables += f'<tr><td><a href="{url}">{link_text or value}</a></td></tr>'
            html_tables += '</tbody></table></div>'

    html_tables += '</div></div>'  # Close the last row and container

    return html_tables


@login_required
def index(request):
    # query_result=landing.aws_utilities.run_steampipe_query_for_platform()
    # html_table = json_to_html_table(query_result)


    template =loader.get_template("landing/index.html")
    context={
        "data":"html_table"
    }
    return HttpResponse(template.render(context,request))

@login_required
def table_object_view(request,table_name):
    # print("table_name",table_name)
    context={}
    try:
        json_data = landing.aws_utilities.convert_string_to_json(landing.aws_utilities.run_steampipe_query_to_json("select *  from "+ table_name))
        add_quotes_to_json_objects=landing.aws_utilities.add_quotes_to_json_objects(json.loads(json_data))
        if not add_quotes_to_json_objects :
            add_quotes_to_json_objects.append("")

       
        
        context={
            "heading":landing.aws_utilities.format_aws_string(table_name),
            "json_data":json.dumps(add_quotes_to_json_objects),
        }
        return JsonResponse(context)
    except Exception as e:
        # Add the error message to Django's messages
        print("I am in exception",e)
        messages.error(request, str(e))
        context['error'] = str(e)
        context['problem'] = "Timing mismatch VM and host machine."
        context['solution'] = "Restart the VM might solve the problem."
        # your view logic...
        return render(request, 'landing/error.html', context)



def table_view(request,table_name):
    context={}
    try:
        json_data = landing.aws_utilities.convert_string_to_json(landing.aws_utilities.run_steampipe_query_to_json("select *  from "+ table_name))
        add_quotes_to_json_objects=landing.aws_utilities.add_quotes_to_json_objects(json.loads(json_data))
        if not add_quotes_to_json_objects :
            add_quotes_to_json_objects.append("")
        print((add_quotes_to_json_objects))
        # json_data_flat=landing.aws_utilities.flatten_json(json.loads(json_data))
        # # json_data=landing.aws_utilities.process_json_data_null_to_empty(json_data)
        # print("JSON_DATA",json_data_flat)
        # print(type(json.dumps(json_data_flat)))


        template =loader.get_template("landing/table.html")
        # json_data=[{"no"}]
        context={
            "heading":landing.aws_utilities.format_aws_string(table_name),
            # "data":json.dumps(json_data_flat),
            # "messages": messages.get_messages(request),
            "data":json.dumps(add_quotes_to_json_objects),
        }
        return HttpResponse(template.render(context,request))
    except Exception as e:
        # Add the error message to Django's messages
        messages.error(request, str(e))
        context['error'] = str(e)
        context['problem'] = "Timing mismatch VM and host machine."
        context['solution'] = "Restart the VM might solve the problem."
        # your view logic...
        return render(request, 'landing/error.html', context)

    


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page.
                return redirect('index/')
            else:
                # Return an 'invalid login' error message.
                return render(request, 'landing/login.html', {'form': form, 'error': 'Invalid username or password.'})
    else:
        form = LoginForm()
    return render(request, 'landing/login.html', {'form': form})

def aws_logout(request):
    # Remove AWS credentials from session
    if 'aws_access_key_id' in request.session:
        del request.session['aws_access_key_id']
    
    if 'aws_secret_access_key' in request.session:
        del request.session['aws_secret_access_key']
    
    # Log the user out
    logout(request)
    
    # Redirect to a landing page or login page
    return redirect('landing:login')  # replace with your actual login or landing page URL name or pattern


@login_required
def dashboard_old(request):
    platform_name = request.GET.get('provider','aws')
    report_type = request.GET.get('report_type','all_tables')

    if platform_name in ["aws","gcp","azure"]:
        if report_type =="all_tables":
            query_result=landing.aws_utilities.run_steampipe_query_for_platform(platform_name)
            base_url='/table_object_view/'
            for record in query_result:
                record['hyperlink']=base_url+record['table_name']
            
        if report_type == "compliance":
            services=compliance_by_servicename_view(platform_name)
            # Convert the list to a list of dictionaries
            base_url='/compliance_report_by_servicename/'+platform_name+'/'
            query_result= [{'table_name': service, 'table_description': service, 'hyperlink':base_url+service} for service in services]
        
        if report_type == "benchmark":
            query_result=benchmark_list(platform_name)
            # Convert the list to a list of dictionaries
            print("Benchmarks",query_result)
            base_url='/benchmark_report/'+platform_name+'/'
            for record in query_result:
                record['hyperlink']=base_url+record['table_name']

            # query_result= [{'table_name': service, 'table_description': service, 'hyperlink':base_url+service} for service in services]
            
           
    # html_table = json_to_html_table(query_result)
        
        html_table=query_result

    template =loader.get_template("landing/dashboard.html")
    context={
        "data":html_table
        
    }
    return HttpResponse(template.render(context,request))

# 
from datetime import datetime

def execute_query(sql_query):
    """
    Execute the given SQL query and return the labels, data, and a flag indicating whether the result should be treated as a badge.

    This version accounts for the flexibility of labels and data potentially containing datetime objects,
    converting them to strings when necessary. It's designed to handle various data shapes and improve the badge determination heuristic.

    :param sql_query: SQL query string to be executed.
    :return: Tuple containing labels, data, and a boolean indicating whether the result is a badge.
    """
    # Execute the query and fetch the results
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        rows = cursor.fetchall()

    # Function to convert datetime objects in a list to strings
    def convert_datetimes(list_items):
        """
        Converts datetime objects in a list to strings.

        :param list_items: List of items, potentially containing datetime objects.
        :return: List of items with datetime objects converted to strings.
        """
        return [item.strftime('%Y-%m-%d') if isinstance(item, datetime) else item for item in list_items]

    # Determine badge status based on the query's characteristics
    aggregate_functions = ['count(', 'sum(', 'avg(', 'min(', 'max(']
    has_aggregate = any(func in sql_query.lower() for func in aggregate_functions)
    is_group_by_present = 'group by' in sql_query.lower()
    is_badge = has_aggregate and not is_group_by_present

    if is_badge or len(rows) == 0 or len(rows[0]) < 2:
        # For badge scenario or single-column results, all data is in the first column
        labels = None  # No labels in a badge scenario
        data = [row[0] for row in rows]
    else:
        # For multi-column results suitable for charts
        labels = [row[0] for row in rows]
        data = [row[1] for row in rows]

    # Convert datetime objects to strings if present in labels and data
    labels = convert_datetimes(labels) if labels is not None else None
    data = convert_datetimes(data)



    return labels, data, is_badge




def get_dashboard_data(provider_filter=None):
    """
    Fetch dashboard data from YAML configuration, filtering by provider if specified, and determine if the data
    should be displayed as a badge based on the query structure.

    :param provider_filter: Optional filter to apply based on the provider.
    :return: List of chart data dictionaries for rendering, including is_badge flag.
    """
    # dashboard_file = 'path/to/your/dashboard.yaml'  # Ensure this points to your actual YAML file path
    with open(dashboard_file, 'r') as file:
        config = yaml.safe_load(file)

    charts_data = []
    for chart in config['charts']:
        if provider_filter and chart.get('provider') != provider_filter:
            continue

        labels, data, is_badge = execute_query(chart['query'])
        chart_type = chart.get('type', 'line')

        charts_data.append({
            'id': chart['id'],
            'title': chart['title'],
            'label': chart['label'],
            'data': data,
            'type': chart_type,
            'borderColor': chart['borderColor'],
            'labels': labels,
            'is_badge': is_badge,  # Add the is_badge flag to the chart data
        })

    return charts_data

@login_required
def dashboard(request):
    """
    Render the dashboard page with charts data filtered by provider.

    :param request: Django HTTP request object.
    :return: Rendered Django template for the dashboard.
    """
    provider = request.GET.get('provider')
    charts_data = get_dashboard_data(provider_filter=provider)
  
    # time.sleep(5)
    return render(request, 'landing/dashboard.html', {'charts_data': charts_data})
   

@login_required
def platform_tables(request):
    platform_name = request.GET.get('provider','aws')
    report_type = request.GET.get('report_type','all_tables')

    if platform_name in ["aws","gcp","azure","all","kubernetes"]:
        if report_type =="all_tables":
            query_result=landing.aws_utilities.run_steampipe_query_for_platform(platform_name)
            base_url='/table_object_view/'
            for record in query_result:
                record['hyperlink']=base_url+record['table_name']
            
        if report_type == "compliance":
            services=compliance_by_servicename_view(platform_name)
            # Convert the list to a list of dictionaries
            base_url='/compliance_report_by_servicename/'+platform_name+'/'
            query_result= [{'table_name': service, 'table_description': service, 'hyperlink':base_url+service} for service in services]
        
        if report_type == "benchmark":
            query_result=benchmark_list(platform_name)
            # Convert the list to a list of dictionaries
            print("Benchmarks",query_result)
            base_url='/benchmark_report/'+platform_name+'/'
            for record in query_result:
                record['hyperlink']=base_url+record['table_name']

            # query_result= [{'table_name': service, 'table_description': service, 'hyperlink':base_url+service} for service in services]
            
           
    # html_table = json_to_html_table(query_result)
        
        html_table=query_result

    template =loader.get_template("landing/all_platform_tables.html")
    context={
        "data":html_table
        
    }
    return HttpResponse(template.render(context,request))

def compliance_by_servicename_view(platform_name="aws"):
    if platform_name == "aws":compliance_dir = settings.GIT_AWS_COMPLIANCE_DIR
    if platform_name == "gcp":compliance_dir = settings.GIT_GCP_COMPLIANCE_DIR
    if platform_name == "azure":compliance_dir = settings.GIT_AZURE_COMPLIANCE_DIR
    dir_path = compliance_dir + "/all_controls"
    return landing.aws_compliance.compliance_list(dir_path)
  


def compliance_report_by_servicename(request,platform_name,service_name):
    print("------------------platform_name",platform_name)
    print("------------------service_name",service_name)
 
    platform_name=platform_name.lower()
    service_name=service_name.lower()
    if platform_name == "aws":compliance_dir = settings.GIT_AWS_COMPLIANCE_DIR
    if platform_name == "gcp":compliance_dir = settings.GIT_GCP_COMPLIANCE_DIR
    if platform_name == "azure":compliance_dir = settings.GIT_AZURE_COMPLIANCE_DIR
    try:
        if service_name.strip().lower() == "all controls".lower():
            print("SERVICE ")
            service_report="steampipe check "+platform_name+"_compliance.benchmark.all_controls"
        else:
            service_report="steampipe check "+platform_name+"_compliance.benchmark.all_controls_"+service_name
        json_data,status = landing.aws_compliance.create_compliance_report(service_report,compliance_dir)
        # json_data,status = landing.aws_compliance.create_compliance_report(category)
        # json_data=[{'reason': 'prod-data-01 all public access blocks enabled.', 'resource': 'arn:aws:s3:::prod-data-01', 'status': 'ok', 'dimensions': [{'key': 'region', 'value': 'eu-west-1'}, {'key': 'account_id', 'value': '867839330780'}]},{'reason': 'prod-data-01 all public access blocks enabled.', 'resource': 'arn:aws:s3:::prod-data-01', 'status': 'ok1', 'dimensions': [{'key': 'region', 'value': 'e1u-west-1'}, {'key': 'account_id', 'value': '867839330780'}]}]
       
 
        context={
            "heading":landing.aws_utilities.format_aws_string(service_name),
            "json_data":json.dumps(json_data),
            "status":status
            # "messages": messages.get_messages(request),
        }
        return JsonResponse(context)
    except Exception as e:
        # Add the error message to Django's messages
        
        messages.error(request, str(e))
        context={
            "error": str(e)
        }
        # your view logic...
        return render(request, 'landing/error.html', context)

# custom query

def custom_query_view(request):
    if request.method == 'POST':
        user_query = request.POST.get('query')
        context={}
        try:
            json_data = landing.aws_utilities.convert_string_to_json(landing.aws_utilities.run_steampipe_query_to_json(user_query))
            add_quotes_to_json_objects=landing.aws_utilities.add_quotes_to_json_objects(json.loads(json_data))
            if not add_quotes_to_json_objects :
                add_quotes_to_json_objects.append("")
            
            context={
                "status":"success",
                "json_data":json.dumps(add_quotes_to_json_objects),
            }
            return JsonResponse(context)
        except Exception as e:
            # Add the error message to Django's messages
            messages.error(request, str(e))
            context['error'] = str(e)
        # your view logic...
            return render(request, 'landing/error.html', context)
    return JsonResponse({'error': 'Invalid request'}, status=400)




def terminal_view(request):
    # Additional logic can be added here if needed
    return render(request, 'landing/terminal.html')

@csrf_exempt
@require_POST


def command_view(request):
    print("Receiveddddd data:", request.body)
    try:
        data = json.loads(request.body.decode('utf-8'))
        command = data.get('command', '')

        if command in settings.ALLOWED_COMMANDS:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30)
            response = output.decode('utf-8')
            
            
        else:
            response = "Command not allowed."

    except subprocess.CalledProcessError as e:
        response = e.output.decode('utf-8')
    except json.JSONDecodeError:
        response = "Invalid JSON data"
    except Exception as e:
        response = str(e)
    # print("I am command_view")
    username = request.user.username if request.user.is_authenticated else 'anonymous'
    LogsModel.objects.create(username=username, command=command, result=response,log_name="terminal")
    return JsonResponse({'output': response})


def get_open_api_key():
    from credentials.models import ChatGPTCredential
    openai_credential = ChatGPTCredential.objects.first()
    return openai_credential.api_key

@csrf_exempt
@require_POST


def ai_command_view(request):
    if not request.user.is_authenticated:
        # print("user not authenticated")
        return JsonResponse({'error': 'User is not authenticated', 'aioutput': ''})
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        command = data.get('aicommand', '')
        OpenAI_KEY=get_open_api_key()
        response = landing.aws_utilities.query_openai_model(command, OpenAI_KEY, model="gpt-3.5-turbo")
        # Store in ChatGPT Models
        username = request.user.username if request.user.is_authenticated else 'anonymous'
        LogsModel.objects.create(username=username, command=command, result=str(response),log_name="chatgpt")
    except json.JSONDecodeError:
        response = "Invalid JSON data"
    except Exception as e:
        response = str(e)
    
    return JsonResponse({'aioutput': str(response)})


def benchmark_view(request,platform_name):
    platform_name=platform_name.lower()

    if platform_name == "aws":compliance_dir = settings.GIT_AWS_COMPLIANCE_DIR
    if platform_name == "gcp":compliance_dir = settings.GIT_GCP_COMPLIANCE_DIR
    if platform_name == "azure":compliance_dir = settings.GIT_AZURE_COMPLIANCE_DIR
    
    steampipe_benchmark_list_command=settings.STEAMPIPE_BENCHMARK_LIST_COMMAND
    result=landing.aws_utilities.run_batch_command(steampipe_benchmark_list_command,compliance_dir)
    parsed_data=landing.aws_utilities.parse_benchmark_table(result)
   
    context={
        "platform_name":platform_name.upper(),
        "categories":parsed_data
    }
    return HttpResponse(template.render(context,request))

def benchmark_list(platform_name):
    platform_name=platform_name.lower()

    if platform_name == "aws":compliance_dir = settings.GIT_AWS_COMPLIANCE_DIR
    if platform_name == "gcp":compliance_dir = settings.GIT_GCP_COMPLIANCE_DIR
    if platform_name == "azure":compliance_dir = settings.GIT_AZURE_COMPLIANCE_DIR
    
    steampipe_benchmark_list_command=settings.STEAMPIPE_BENCHMARK_LIST_COMMAND
    result=landing.aws_utilities.run_batch_command(steampipe_benchmark_list_command,compliance_dir)
    parsed_data=landing.aws_utilities.parse_benchmark_table(result)
    return parsed_data


def benchmark_report(request,platform_name,benchmark_name):
    platform_name=platform_name.lower()

    if platform_name == "aws":compliance_dir = settings.GIT_AWS_COMPLIANCE_DIR
    if platform_name == "gcp":compliance_dir = settings.GIT_GCP_COMPLIANCE_DIR
    if platform_name == "azure":compliance_dir = settings.GIT_AZURE_COMPLIANCE_DIR
    try:
        benchmark_report="steampipe check "+benchmark_name
        json_data,status = landing.aws_compliance.create_benchmark_report(benchmark_report,compliance_dir)
        # json_data=[{'reason': 'prod-data-01 all public access blocks enabled.', 'resource': 'arn:aws:s3:::prod-data-01', 'status': 'ok', 'dimensions': [{'key': 'region', 'value': 'eu-west-1'}, {'key': 'account_id', 'value': '867839330780'}]},{'reason': 'prod-data-01 all public access blocks enabled.', 'resource': 'arn:aws:s3:::prod-data-01', 'status': 'ok1', 'dimensions': [{'key': 'region', 'value': 'e1u-west-1'}, {'key': 'account_id', 'value': '867839330780'}]}]
        # print(json_data)
        # template =loader.get_template("landing/table.html")
        context={
            "heading":landing.aws_utilities.format_aws_string(benchmark_name),
            "json_data":json.dumps(json_data),
            "status":status
            # "messages": messages.get_messages(request),
        }
        return JsonResponse(context)
    except Exception as e:
        # Add the error message to Django's messages
        messages.error(request, str(e))
        context={
            "error": str(e)
        }
        # your view logic...
        return render(request, 'landing/error.html', context)

# Dynamic form
@csrf_exempt
def store_heading_path_data(request):
     unique_key = str(uuid.uuid4())
     if 'form_heading' in request.POST and 'table_path' in request.POST and 'row_data' in request.POST:
             # Store data in the session using the unique key
            form_heading=request.POST.get('form_heading')
            table_path= request.POST.get('table_path')
            row_data= request.POST.get('row_data'),
            request.session[f'form_data_{unique_key}'] = {
            'form_heading':form_heading ,
            'table_path': table_path,
            'row_data': row_data,
            'yaml_dynamic_form': landing.aws_utilities.find_all_occurrences_of_form_and_table(dynamic_form_file, table_path, form_heading)

        }
            response_data = {
                            'status': 'success',
                            'unique_key': unique_key,
                            'message': 'Form submitted successfully',
                            'post_success_response': 'Your HTML content here',
                            'redirect_to_dynamic_form': True,
                            # 'form':form,
                             'template_file':'/dynamic_view_form'
                        }
            return JsonResponse(response_data)

def dynamic_view_form(request):
    unique_key = request.GET.get('unique_key')
    command_output = None
    form = None
    row_data = None

    if unique_key:
        form_data = request.session.get(f'form_data_{unique_key}')
        if form_data:
            form_heading = form_data['form_heading']
            table_path = form_data['table_path']
            row_data = form_data['row_data']
            # yaml_dynamic_form = landing.aws_utilities.find_all_occurrences_of_form_and_table(dynamic_form_file, table_path, form_heading)
            yaml_dynamic_form=form_data['yaml_dynamic_form']
            print("yamal_dynamic_form",yaml_dynamic_form)
            print('---------------------')
            if yaml_dynamic_form:
                form_data1 = yaml_dynamic_form[0]
                print("form_data1",form_data1)
                # Store the form_data in the session
                # request.session[f'form_data_{unique_key}'] = form_data

                form = DynamicForm(form_data1, request.POST or None)

    context = {
        'form': form, 
        'row_data': row_data,
        'unique_key': unique_key,
    }
    return render(request, 'landing/dynamic_form.html', context)


def generate_command_output(unique_key, form_filed_data, row_data, yaml_forms, table_path):
    print("yaml_forms", yaml_forms)
    print("row_data", row_data)
    print("form_filed_data", form_filed_data)
    print("unique_key", unique_key)
    print("table_path", table_path)
    command_to_run=landing.aws_utilities.get_command_to_run(yaml_forms)
    print("Command TO RUN", command_to_run)
    
    process = subprocess.Popen(command_to_run, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in process.stdout:
        current_time = time.strftime("%H:%M:%S")  # Current time in HH:MM:SS format
        current_output = f"{current_time}: {line}"  # Combine time with the output
        print(current_output)
        
        yield current_output + "\n"  # Yield the output with time
    
    process.stdout.close()
    return_code = process.wait()
    if return_code:
        error_message = f'Command failed with return code {return_code}\n'
        print(error_message)
        yield error_message
  
    

def generate_command_output_old(unique_key,form_filed_data,row_data,yaml_forms,table_path):
    print("yaml_forms",yaml_forms)
    print("row_data",row_data)
    print("form_filed_data",form_filed_data)
    print("unique_key",unique_key)
    print("table_path",table_path)
    command_to_run=landing.aws_utilities.get_command_to_run(yaml_forms)
    print("Command TO RUN",command_to_run)
    run_batch_command(command_to_run)
    
    
    command_output = ""
    command_outputs[unique_key] = command_output
    for i in range(1, 5):
        current_time = time.strftime("%H:%M:%S")  # Current time in HH:MM:SS format
        current_output = f"{current_time}: {i}"   # Combine time with the iteration's output
        print(current_output)
        command_outputs[unique_key] = current_output
        time.sleep(0.25)  # Simulate a delay
        yield current_output + "\n"  # Yield the output with time


def dynamic_form_process(request):
    
    unique_key = request.GET.get('unique_key')

    print("I am in dynamic_form_process")
    form_filed_data={}
    if unique_key:
        yaml_form_fields = request.session.get(f'form_data_{unique_key}')
       
        form_heading = yaml_form_fields['form_heading']
        table_path = yaml_form_fields['table_path']
        row_data = yaml_form_fields['row_data']
        yaml_forms=yaml_form_fields['yaml_dynamic_form']
        if yaml_form_fields and request.method == 'POST':
            form = DynamicForm(yaml_forms[0], request.POST)
            print("form-->",form)
            if form.is_valid():
                form_filed_data=form.cleaned_data
                
                # for field in form.cleaned_data:
                #     print(f"{field}: {form.cleaned_data[field]}")
            else:
                print("form is not vaild")
            

            
        # else:return JsonResponse({'status': 'error', 'message': 'Invalid request'})

        response = StreamingHttpResponse(generate_command_output(unique_key,form_filed_data,row_data,yaml_forms,table_path),status=200,content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        
        return response  # Add 'await' here
                # return StreamingHttpResponse(generate_command_output(unique_key),status=200,content_type='text/event-stream')
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


    
#  del request.session[f'form_data_{unique_key}']


# Function to check if the OS is Windows
def is_windows():
    return platform.system() == 'Windows'

# View to handle YAML file operations
@login_required
def yaml_handler(request):
    """
    This view handles opening, validating, and updating a YAML file.
    Uses fcntl for file locking on Unix-based systems.
    Displays an error message if run on Windows.
    """
    file_path = None
    file_name = request.GET.get('file_name')
  
    if file_name == "context_menu":
        file_path = dynamic_form_file
    if file_name == "config_file":
        file_path = config_file
    if file_name == "dashboard_file":
        file_path = dashboard_file



    if is_windows():
        # Display message if OS is Windows
        return HttpResponse("File locking is not supported on Windows with this implementation.")

    
    
    context = {'message': '', 'content': '', 'readonly': False}

    try:
        with open(file_path, 'r+') as file:
            # Try acquiring an exclusive lock
            fcntl.flock(file.fileno(), fcntl.LOCK_EX)

            if request.method == 'POST':
                # Update YAML file if data is posted
                try:
                    content = yaml.safe_load(request.POST['content'])
                    file.seek(0)
                    file.truncate()
                    yaml.safe_dump(content, file)
                    context['message'] = 'File successfully updated.'
                except yaml.YAMLError as exc:
                    context['message'] = 'Invalid YAML content.'

            else:
                # Read and display the content of the YAML file
                context['content'] = file.read()

            # Release the lock
            fcntl.flock(file.fileno(), fcntl.LOCK_UN)

    except IOError as e:
        context['readonly'] = True
        context['message'] = 'File is currently opened by another user. Opened in read-only mode.'
        context['file_path'] = file_path
        with open(file_path, 'r') as file:
            context['content'] = file.read()

    return render(request, 'landing/yaml_editor.html', context)

@csrf_exempt
def terraform_import_process(request):

   if request.method == 'POST':
        arns_list=[]
        try:
            data = json.loads(request.body)
            selected_data = data.get('selected_data_for_terraform_import')
            # Process selected_data
            # ...
            print("selected_data",selected_data)
            arns_list=landing.aws_utilities.extract_arns(selected_data)
            print("arns_list",arns_list)
            for i in arns_list:
                print(i)
                result=landing.aws_utilities.get_table_names_with_prefix_and_search("default","aws",i,"arn",["aws_resource_explorer_search","aws_s3_object","aws_organizations_account",\
                                                                                                            "aws_organizations_policy","aws_organizations_organizational_unit",\
                                                                                                            "aws_organizations_policy_target"])
                print("result",result)
                table_name=result[0][0]
                region_value=result[0][1]
                arn_value=result[0][2]
                output_dir=landing.aws_utilities.replace_colons(arn_value)
                # Run terraformmer import command
                print("Staring terraformer import")
                result_terraformer_import=landing.aws_utilities.run_terraformer_import(
                    'aws',
                    's3',
                    region_value,
                    'arn',
                    arn_value,
                    output_dir
                )
                print("Ending terraformer import")
                print("Creating zip file")

                working_directory = os.path.join("/tmp/terraformer", 'aws')
                # working_directory=os.path.join(working_directory, output_dir)
                try:
                # Create the directory
                # exist_ok=True allows the command to succeed even if the directory already exists
                    os.makedirs(working_directory, exist_ok=True)
                    print(f"Directory '{working_directory}' created successfully.")
                except OSError as error:
                    print(f"Error creating directory '{working_directory}': {error}")
                if result_terraformer_import:
                    # compress the folder
                    # Compress the folder and get the path of the ZIP file
                    zip_file_path = landing.aws_utilities.compress_directory(working_directory,[".terraform",".terraform.lock.hcl"]) 

                    # Serve the ZIP file as a response
                    file_wrapper = FileWrapper(open(zip_file_path, 'rb'))
                    content_type = mimetypes.guess_type(zip_file_path)[0]
                    response = HttpResponse(file_wrapper, content_type=content_type)
                    response['Content-Disposition'] = f'attachment; filename={os.path.basename(zip_file_path)}'
                    response['Content-Length'] = os.path.getsize(zip_file_path)
                    return response
                   

            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

# views.py
import logging
from django.shortcuts import render
from django.db import connection

# Set up logging
logger = logging.getLogger(__name__)

def search_old(request):
    search_term = request.GET.get('q', '')
    table_prefixes = ["aws", "azure", "gcp"]
    results = []

    # Log the received search term
    logger.info(f"Received search term: {search_term}")

    if search_term:
        with connection.cursor() as cursor:
            for prefix in table_prefixes:
                # Retrieve tables with the specified prefix
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s", [prefix + '%'])
                table_names = [row[0] for row in cursor.fetchall()]
                logger.info(f"Found tables with prefix {prefix}: {table_names}")

                for table_name in table_names:
                    try:
                        # Retrieve column names for each table
                        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", [table_name])
                        columns = [col[0] for col in cursor.fetchall()]

                        # Construct the search query
                        search_query = " OR ".join([f"{col}::text LIKE %s" for col in columns])
                        sql = f"SELECT * FROM {table_name} WHERE {search_query}"

                        # Log the constructed SQL query
                        logger.debug(f"Executing query on table {table_name}: {sql}")

                        # Execute the search query
                        cursor.execute(sql, ['%' + search_term + '%'] * len(columns))
                        table_results = cursor.fetchall()

                        if table_results:
                            results.append((table_name, table_results))
                            logger.info(f"Search results found in table {table_name}")

                    except Exception as e:
                        logger.error(f"Error querying table {table_name}: {e}")

    return render(request, 'landing/search.html', {'results': results, 'search_term': search_term})




from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
def is_ajax(request: HttpRequest) -> bool:
    """
    Check if the request is an AJAX request.
    """
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

from django.http import StreamingHttpResponse




class CustomEncoder(json.JSONEncoder):
    """ Custom JSON encoder for handling non-serializable data types. """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()  # Convert datetime objects to ISO format
        return super(CustomEncoder, self).default(obj)

# This block is to search string in all the tables starts with aws gcp and azure


def chunkify(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def search_tables_for_arn(search_term, table_names, unsupported_tables):
    results = []
    with connection.cursor() as cursor:
        for table_name in table_names:
          
     
            if table_name in unsupported_tables:
                # Skip this iteration if the table is unsupported
           
                continue
            try:
                columns_query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
                cursor.execute(columns_query, [table_name])
                columns = [col[0] for col in cursor.fetchall()]         
                if 'arn' in columns:
                    print("columns",columns)
                    columns_str = ', '.join(columns)
                    search_query = f"SELECT {columns_str} FROM {table_name} WHERE arn LIKE %s"
                    cursor.execute(search_query, [f'%{search_term}%'])
                    table_results = cursor.fetchall()
                   
                    if table_results:
                        results.append((table_name, columns, table_results))
            except Exception as e:
                logger.error(f"Error querying table {table_name}: {e}")
                continue
    
    return results




# def search_tables_for_gcp_identifier(search_term, table_names, unsupported_tables):
#     results = []
#     with connection.cursor() as cursor:
#         for table_name in table_names:
#             print("Table Name:", table_name)
#             if table_name in unsupported_tables:
#                 # Skip this iteration if the table is unsupported
#                 continue
#             try:
#                 # Retrieve the column names for the current table
#                 columns_query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
#                 cursor.execute(columns_query, [table_name])
#                 columns = [col[0] for col in cursor.fetchall()]

#                 # Define the common identifier for GCP tables you're interested in
#                 # This could be 'resource_id', 'name', 'id', or another field based on your tables
#                 common_identifier = 'resource_id'  # Adjust this based on the actual identifier used

#                 if common_identifier in columns:
#                     columns_str = ', '.join(columns)
#                     # Construct and execute a query to search for the identifier in the current table
#                     search_query = f"SELECT {columns_str} FROM {table_name} WHERE {common_identifier} LIKE %s"
#                     cursor.execute(search_query, [f'%{search_term}%'])
#                     table_results = cursor.fetchall()

#                     if table_results:
#                         # Append the results for the current table to the results list
#                         results.append((table_name, columns, table_results))
#             except Exception as e:
#                 logger.error(f"Error querying table {table_name}: {e}")
#                 continue
#     return results


# def search_tables_for_azure_identifier(search_term, table_names, unsupported_tables):
#     results = []
#     with connection.cursor() as cursor:
#         for table_name in table_names:
#             print("Table Name:", table_name)
#             if table_name in unsupported_tables:
#                 # Skip this iteration if the table is unsupported
#                 continue
#             try:
#                 # Retrieve the column names for the current table
#                 columns_query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
#                 cursor.execute(columns_query, [table_name])
#                 columns = [col[0] for col in cursor.fetchall()]

#                 # Define the common identifier for Azure tables you're interested in
#                 # Azure resources typically use 'resource_id' as a universal identifier
#                 common_identifier = 'resource_id'  # Adjust if your tables use a different identifier

#                 if common_identifier in columns:
#                     columns_str = ', '.join(columns)
#                     # Construct and execute a query to search for the identifier in the current table
#                     search_query = f"SELECT {columns_str} FROM {table_name} WHERE {common_identifier} LIKE %s"
#                     cursor.execute(search_query, [f'%{search_term}%'])
#                     table_results = cursor.fetchall()

#                     if table_results:
#                         # Append the results for the current table to the results list
#                         results.append((table_name, columns, table_results))
#             except Exception as e:
#                 logger.error(f"Error querying table {table_name}: {e}")
#                 continue
#     return results



# def data_generator(search_term, table_prefixes=["aws_s3_e%"]):
#     table_names = []
#     unsupported_tables = [
#         'aws_organizations_policy', 'aws_organizations_organizational_unit', 'aws_fms_policy',
#         'aws_organizations_account', 'aws_s3_object', 'aws_appstream_image',
#         'aws_organizations_policy_target', 'aws_fms_app_list', 'aws_ssm_document','azure_monitor_activity_log_event','azure_api_management_backend'
#     ]  # Extend this list based on your requirements

#     with connection.cursor() as cursor:
#         for pattern in table_prefixes:
#             cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s", [pattern])
#             table_names.extend([row[0] for row in cursor.fetchall()])

#     chunk_size = 5  # Adjust based on your needs
#     chunked_tables = list(chunkify(table_names, chunk_size))

#     # Assuming search functions are defined and mapped to their prefixes
#     function_map = {
#         "aws_": search_tables_for_arn,
#         "gcp_": search_tables_for_gcp_identifier,
#         "azure_": search_tables_for_azure_identifier,
#     }

#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future_to_result = {}
#         for tables_chunk in chunked_tables:
#             # Determine the correct function based on table prefix
#             prefix = tables_chunk[0].split("_")[0] + "_"  # Extract prefix from table name
#             print("Using prefix:", prefix)  # Debug print
#             search_function = function_map.get(prefix)

#             if search_function:
#                 # Submit the chunk to the appropriate function
#                 future = executor.submit(search_function, search_term, tables_chunk, unsupported_tables)
               
#                 future_to_result[future] = tables_chunk
             

#         # Collect and yield results
#         for future in concurrent.futures.as_completed(future_to_result):
#             tables_chunk = future_to_result[future]
#             try:
#                 results = future.result()
#                 logger.info(f"Received results for chunk {tables_chunk}: {results}")
#                 for table_name, columns, table_results in results:
#                     search_result_json = json.dumps(table_results, default=str)
#                     yield f"Table_Name: {table_name}, Headers:{columns}, Search_result: {search_result_json}\n"
#             except Exception as exc:
#                 logger.error(f"Error with chunk {tables_chunk}: {exc}")

# # Example usage within your data_generator function
# def data_generator_old(search_term, table_prefixes=["aws_%"]):
#     # Fetch tables based on the prefixes
#     table_names = []
#     unsupported_tables = ['aws_organizations_policy', 
#                         'aws_organizations_organizational_unit', 
#                         'aws_fms_policy',
#                         'aws_organizations_account',
#                         'aws_s3_object',
#                         'aws_appstream_image',
#                         'aws_organizations_policy_target',
#                         'aws_fms_app_list',
#                         'aws_ssm_document'
#                         ]  # Example list

#     with connection.cursor() as cursor:
#         for pattern in table_prefixes:
#             print("pattern",pattern)
#             cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s", [pattern])
#             table_names.extend([row[0] for row in cursor.fetchall()])
            

#     # Chunk the list of table names for parallel processing
#     chunk_size = 5  # Or whatever size works best for your scenario
#     chunked_tables = list(chunkify(table_names, chunk_size))

#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         # Now your comprehension has a defined 'chunked_tables'
#         future_to_table_name = {
#             executor.submit(search_tables_for_arn, search_term, tables_chunk,unsupported_tables): tables_chunk 
#             for tables_chunk in chunked_tables
#             }
#         for future in concurrent.futures.as_completed(future_to_table_name):
#             tables_chunk = future_to_table_name[future]
#             try:
#                 results = future.result()
#                 for table_name, columns, table_results in results:
#                     print("Table_Name",table_name)
#                     search_result_json = json.dumps(table_results, default=str)  # Ensure you have a suitable JSON encoder for your data
#                     yield f"Table_Name: {table_name}, Headers:{columns},Search_result: {search_result_json}\n"
#             except Exception as exc:
#                 logger.error(f"{tables_chunk} generated an exception: {exc}")


# def search(request):
#     if 'search_term' not in request.GET:
#         return render(request, 'landing/search.html')
#     search_term = request.GET.get('search_term', '')
#     return StreamingHttpResponse(data_generator(search_term))

unsupported_tables = [
            'aws_organizations_policy', 'aws_organizations_organizational_unit', 'aws_fms_policy',
            'aws_organizations_account', 'aws_s3_object', 'aws_appstream_image',
            'aws_organizations_policy_target', 'aws_fms_app_list', 'aws_ssm_document',
            'azure_monitor_activity_log_event', 'azure_api_management_backend',
            'aws_ec2_ami_shared'
        ]


def create_postgresql_free_text_search_query(columns, table_name, search_terms):
    """
    Generates a SQL query for performing a free text search in a PostgreSQL database.
    This query utilizes PostgreSQL's full-text search capabilities.

    :param columns: A list representing the columns to select.
    :param table_name: The name of the table to search within.
    :param search_terms: The terms to search for, which will be converted into a tsquery.
    :return: A tuple containing the SQL query string and the formatted search terms.
    """
    # Join the column names into a comma-separated string
    columns_str = ", ".join(columns)

    # Preparing the tsvector by combining the columns with explicit type casting
    ts_vector = ' || '.join(f"to_tsvector(CAST({col} AS text))" for col in columns)
    
    # Forming the complete SQL query
    sql_query = f"""SELECT {columns_str} FROM {table_name}
                    WHERE ({ts_vector}) @@ to_tsquery(%s);"""

    # Format search terms for to_tsquery
    formatted_search_terms = ' & '.join(search_terms.split())

    return sql_query, (formatted_search_terms,)


def create_search_query(table_name, columns, search_term):
    """
    Constructs a SQL query to search for a given search term across all specified columns of a table.
    It dynamically generates a WHERE clause that uses the LIKE operator on each column, casting non-text columns to text.

    Args:
    table_name (str): The name of the database table to search.
    columns (list of str): A list of column names to include in the search.
    search_term (str): The search term to look for across all columns.

    Returns:
    str: A SQL query string.
    """
    # Base query template
    sql_query = f"SELECT {', '.join(columns)} FROM {table_name} WHERE "

    # Generate the WHERE clause, casting each column to text and checking if the search term is present
    where_conditions = [f"CAST({column} AS TEXT) LIKE %s" for column in columns]

    # Combine all conditions with OR as we're searching across all fields
    combined_conditions = ' OR '.join(where_conditions)

    # Finalize the query
    final_query = sql_query + combined_conditions

    return final_query





@login_required
def search(request):
    """
    Stream search results using StreamingHttpResponse.
    """
    if 'search_term' not in request.GET:
        return render(request, 'landing/search.html')
    def data_generator():
        table_prefixes = ["aws_s3_%","gcp_%"]  # SQL LIKE patterns
     
        if request.method == 'GET':
            search_term = request.GET.get('search_term', None)
            with connection.cursor() as cursor:
                for pattern in table_prefixes:
                    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s", [pattern])
                    table_names = [row[0] for row in cursor.fetchall()]

                    for table_name in table_names:
                        if table_name in unsupported_tables:
                            continue
                        try:
                            print("OK Table_name",table_name)
                            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", [table_name])
                            columns = [col[0] for col in cursor.fetchall()]
                  
                            # Example usage
                            
                            if 'arn' in columns:
                                columns = ', '.join(columns)

                                sql_query = f"SELECT {columns} FROM {table_name} WHERE arn LIKE %s"
                                cursor.execute(sql_query, ['%' + search_term + '%'])
                                results = cursor.fetchall()

                                # Include column headers
                                column_headers = columns.split(', ')
                                # results_with_headers = [column_headers] + list(results)
                                search_result_json = json.dumps(results, cls=CustomEncoder)
                                if results:
                                    print("table_name",table_name)
                                    print("results-----",results)
                                    yield f"Table_Name: {table_name}, Headers:{column_headers},Search_result: {search_result_json}\n"

                            if 'akas' in columns:
                                columns = ', '.join(columns)
                                sql_query = f"SELECT {columns} FROM {table_name} WHERE CAST(akas AS TEXT) LIKE %s"
                                print("SQl_QUERY",sql_query)
                                cursor.execute(sql_query, ['%' + search_term + '%'])
                                results = cursor.fetchall()

                                # Include column headers
                                column_headers = columns.split(', ')
                                # results_with_headers = [column_headers] + list(results)
                                search_result_json = json.dumps(results, cls=CustomEncoder)
                                if results:
                                    print("table_name",table_name)
                                    print("results-----",results)
                                    yield f"Table_Name: {table_name}, Headers:{column_headers},Search_result: {search_result_json}\n"
                                    
                        except Exception as e:
                            logger.error(f"Error querying table {table_name}: {e}")
                            continue

    return StreamingHttpResponse(data_generator())


# Setup logger for error logging
logger = logging.getLogger(__name__)

def search_new(request):
    """
    Stream search results using StreamingHttpResponse.
    """
    if 'search_term' not in request.GET:
        return render(request, 'landing/search.html')

    def data_generator():
        table_prefixes = ["aws_s3_buck", ]  # SQL LIKE patterns for AWS and Azure
       

        search_term = request.GET.get('search_term', '')

        with connection.cursor() as cursor:
            for pattern in table_prefixes:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s", [pattern])
                table_names = [row[0] for row in cursor.fetchall()]

                for table_name in table_names:
                    if table_name in unsupported_tables:
                        logger.info(f"Skipping unsupported table: {table_name}")
                        continue

                    try:
                        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", [table_name])
                        columns = [col[0] for col in cursor.fetchall()]

                        valid_columns = [col for col in columns if col]
                        if valid_columns:
                            columns_joined = ', '.join(valid_columns)
                            # Explicitly cast each column to text
                            tsvector_expression = " || ' ' || ".join([f"COALESCE(CAST({col} AS TEXT), '')" for col in valid_columns])

                            sql_query = f"""
                            SELECT {columns_joined} 
                            FROM {table_name} 
                            WHERE to_tsvector('english', {tsvector_expression}) @@ plainto_tsquery('english', %s);
                            """
                            cursor.execute(sql_query, [search_term])
                            results = cursor.fetchall()

                            if results:
                                column_headers = columns_joined.split(', ')
                                search_result_json = json.dumps(results, cls=CustomEncoder)
                                yield f"Table_Name: {table_name}, Headers: {column_headers}, Search_result: {search_result_json}\n"

                    except Exception as e:
                        logger.error(f"Error querying table {table_name}: {e}")

    return StreamingHttpResponse(data_generator())