from django.shortcuts import render, redirect
from .models import AzureCredential, GCPCredential, AWSCredential, ChatGPTCredential
from .forms import AzureCredentialForm, GCPCredentialForm, AWSCredentialForm, ChatGPTCredentialForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .test_credentails import f_test_aws_credentials, f_test_gcp_credentials,f_test_chatgpt_credentials,f_test_azure_credentials

# Import the SDKs or libraries required for each service provider
# Import the SDKs or libraries required for each service provider
@login_required
def manage_credentials(request):
    # Try to fetch the existing credentials, or none if they don't exist
    azure_instance = AzureCredential.objects.first()
    gcp_instance = GCPCredential.objects.first()
    aws_instance = AWSCredential.objects.first()
    chatgpt_instance = ChatGPTCredential.objects.first()

    if request.method == 'POST':
        # Determine which form is being submitted based on the presence of a specific button in the request
        if 'save_azure' in request.POST:
            form = AzureCredentialForm(request.POST, instance=azure_instance)
            if form.is_valid():
                form.save()
                return redirect('manage_credentials')
        elif 'save_gcp' in request.POST:
            form = GCPCredentialForm(request.POST, request.FILES, instance=gcp_instance)
            if form.is_valid():
                form.save()
                return redirect('manage_credentials')
        elif 'save_aws' in request.POST:
            form = AWSCredentialForm(request.POST, instance=aws_instance)
            if form.is_valid():
                form.save()
                return redirect('manage_credentials')
        elif 'save_chatgpt' in request.POST:
            form = ChatGPTCredentialForm(request.POST, instance=chatgpt_instance)
            if form.is_valid():
                form.save()
                return redirect('manage_credentials')
    else:
        forms = {
            'azure_form': AzureCredentialForm(instance=azure_instance),
            'gcp_form': GCPCredentialForm(instance=gcp_instance),
            'aws_form': AWSCredentialForm(instance=aws_instance),
            'chatgpt_form': ChatGPTCredentialForm(instance=chatgpt_instance),
        }
    return render(request, 'credentials/manage_credentials.html', forms)



@csrf_exempt
@login_required
def test_azure_credentials(request):
    if request.method == 'POST':
        # Extract credentials from request.POST or request.FILES
        # Example: client_id = request.POST.get('client_id')
        
        # Here, you would use the extracted credentials to attempt to authenticate with Azure
        # This is highly dependent on the service's SDK and what "testing" entails
        try:
            # Attempt authentication with Azure using provided credentials
            # If successful, return a success response
            return JsonResponse({'result': 'Success'})
        except Exception as e:
            # If authentication fails, return a failure response
            return JsonResponse({'result': 'Failed', 'error': str(e)})
    return JsonResponse({'result': 'Invalid request'}, status=400)



@csrf_exempt
@login_required
def test_aws_credentials(request):
    
    if request.method == 'POST':
        # Extract credentials from request.POST or request.FILES
        access_key_id = request.POST.get('access_key_id')
        secret_access_key=request.POST.get('secret_access_key')
        role_arn = request.POST.get('role_arn')
        session_name=request.POST.get('session_name')
        # Here, you would use the extracted credentials to attempt to authenticate with Azure
        # This is highly dependent on the service's SDK and what "testing" entails
        try:
            # Attempt authentication with Azure using provided credentials
            # If successful, return a success response
            result=f_test_aws_credentials(access_key_id,secret_access_key)
            return JsonResponse({'result': 'Success'})
        except Exception as e:
            # If authentication fails, return a failure response
            return JsonResponse({'result': 'Failed', 'error': str(e)})
    return JsonResponse({'result': 'Invalid request'}, status=400)


# Import the SDKs or libraries required for each service provider

@csrf_exempt
@login_required
def test_gcp_credentials(request):
    if request.method == 'POST':
        # Extract credentials from request.POST or request.FILES
        # Example: client_id = request.POST.get('client_id')
        from .models import GCPCredential
        json_file=GCPCredential.objects.first()
        if json_file:
            abso_json_file=json_file.credential_file
        
       
        
        
        # Here, you would use the extracted credentials to attempt to authenticate with Azure
        # This is highly dependent on the service's SDK and what "testing" entails
        try:
            # Attempt authentication with Azure using provided credentials
            # If successful, return a success response
            f_test_gcp_credentials(abso_json_file.path)
            return JsonResponse({'result': 'Success'})
        except Exception as e:
            # If authentication fails, return a failure response
            return JsonResponse({'result': 'Failed', 'error': str(e)})
    return JsonResponse({'result': 'Invalid request'}, status=400)


# Import the SDKs or libraries required for each service provider

@csrf_exempt
@login_required
def test_chatgpt_credentials(request):
    if request.method == 'POST':
        # Extract credentials from request.POST or request.FILES
        # Example: client_id = request.POST.get('client_id')
        api_key = request.POST.get('api_key')
        description=request.POST.get('description')
        
        # Here, you would use the extracted credentials to attempt to authenticate with Azure
        # This is highly dependent on the service's SDK and what "testing" entails
        try:
            # Attempt authentication with Azure using provided credentials
            result=f_test_chatgpt_credentials(api_key)
            # If successful, return a success response
            return JsonResponse({'result': 'Success'})
        except Exception as e:
            # If authentication fails, return a failure response
            return JsonResponse({'result': 'Failed', 'error': str(e)})
    return JsonResponse({'result': 'Invalid request'}, status=400)
