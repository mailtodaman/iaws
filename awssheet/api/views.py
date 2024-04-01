from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
import subprocess
from landing.aws_utilities import *


class ReportsView(APIView):
    def get(self, request,platform):
        
        query = request.query_params.get('query', '')
           # Use the default query if no query is provided
        if not query:
            result=run_steampipe_query_for_platform(platform)
            return Response({"result": result})
        else:
            return Response({"result": "Query found"})
        
        
        # Validate and sanitize the query here
        # For example, only allow select queries for safety
        if not query.lower().startswith('select'):
            return Response({"error": "Invalid query"}, status=400)

        # Execute the query using Steampipe
        result = subprocess.run(['steampipe', 'query', query], capture_output=True, text=True)
        
        if result.returncode != 0:
            return Response({"error": result.stderr}, status=500)

        return Response({"result": result.stdout})
