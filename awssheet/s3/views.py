from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from s3.s3 import list_s3_bucket,create_s3_bucket,list_s3_bucket_cached,remove_s3_bucket
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
# Create your views here.
from landing.decorators import aws_login_required

@aws_login_required
def index(request):
    aws_access_key_id=request.session.get('aws_access_key_id')
    aws_secret_access_key=request.session.get('aws_secret_access_key')
    AWS_REGION=settings.AWS_REGION_NAME
    template =loader.get_template("s3/index.html")
    context={
        "heading":"S3",
        "data":list_s3_bucket_cached(aws_access_key_id,aws_secret_access_key),
        "messages": messages.get_messages(request),
    }
    return HttpResponse(template.render(context,request))


def f_createS3_bucket(request):
    aws_access_key_id=request.session.get('aws_access_key_id')
    aws_secret_access_key=request.session.get('aws_secret_access_key')
    AWS_REGION=settings.AWS_REGION_NAME
    bucketName = request.POST.get('bucketName')
    print(type(bucketName))
    create_s3_bucket(bucketName,aws_access_key_id,aws_secret_access_key,AWS_REGION)
    messages.success(request, f'Successfully created bucket {bucketName}.')
    return redirect('index')

def f_removeS3_bucket(request):
    aws_access_key_id=request.session.get('aws_access_key_id')
    aws_secret_access_key=request.session.get('aws_secret_access_key')
    AWS_REGION=settings.AWS_REGION_NAME
    bucketName = request.POST.get('bucketName')
    print(type(bucketName))
    remove_s3_bucket(bucketName,aws_access_key_id,aws_secret_access_key)
    messages.success(request, f'Successfully removed bucket {bucketName}.')
    return redirect('index')