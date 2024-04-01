# decorators.py
from django.shortcuts import redirect
import boto3
from django.contrib import messages
import time
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


# check how much time taken by function
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} took {elapsed_time:.4f} seconds")
        return result
    return wrapper