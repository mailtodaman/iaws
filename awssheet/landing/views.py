from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .forms import AWSCredentialsForm

# Create your views here.

from .forms import AWSCredentialsForm
import boto3
from django.contrib.auth import logout
from django.shortcuts import redirect

from django.shortcuts import render
from django.conf import settings

def my_view(request):
    context = {
        'availability_zones': settings.AWS_AVAILABILITY_ZONES
    }
    return render(request, 'my_template.html', context)


def index(request):
    template =loader.get_template("landing/index.html")
    context={
        "data":"My data"
    }
    return HttpResponse(template.render(context,request))



def login(request):
    if request.method == "POST":
        form = AWSCredentialsForm(request.POST)
        if form.is_valid():
            aws_access_key_id = form.cleaned_data['aws_access_key_id']
            aws_secret_access_key = form.cleaned_data['aws_secret_access_key']

            # Store the credentials in the session
            request.session['aws_access_key_id'] = aws_access_key_id
            request.session['aws_secret_access_key'] = aws_secret_access_key
            return render(request, 'landing/index.html', {'form': form})

            # Create an S3 client using the credentials
            # s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

            # Your secret script here using the s3 client
            
    else:
        form = AWSCredentialsForm()
    
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



