from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.core.cache import cache
from ec2.ec2 import create_ec2_instance, list_ec2_instances

# Create your views here.
def index(request):
    AWS_ACCESS_KEY = request.session.get('aws_access_key_id')
    AWS_SECRET_KEY = request.session.get('aws_secret_access_key')
    AWS_REGION=settings.AWS_REGION_NAME
    # create_ec2_instance("Waheguru")
    template =loader.get_template("ec2/index.html")
    
    context={
        "heading":"EC2 Instances",
        "data":list_ec2_instances(AWS_ACCESS_KEY ,AWS_SECRET_KEY, AWS_REGION)
    }
    return HttpResponse(template.render(context,request))
    # return HttpResponse("Hello, world. You're at the polls index.")