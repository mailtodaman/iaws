from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.
# Create your views here.
def index(request):
    # template =loader.get_template("s3/index.html")
    
    # context={
    #     "heading":"S3",
    #     "data":list_s3_bucket()
    # }
    # return HttpResponse(template.render(context,request))
    return HttpResponse("Hello, world. You're at the Lambda page.")