# decorators.py
from django.shortcuts import redirect
import boto3
from django.contrib import messages

# decorators.py
from django.shortcuts import redirect

def aws_login_required(f):
    def wrap(request, *args, **kwargs):
        aws_access_key_id = request.session.get('aws_access_key_id')
        aws_secret_access_key = request.session.get('aws_secret_access_key')
        
        if aws_access_key_id and aws_secret_access_key:
            return f(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, 'You must be logged in to view this page.')
            return redirect('landing:login')
    return wrap