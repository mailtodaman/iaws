import re,json
import django
from django.core.cache import cache
import subprocess
import hashlib
import logging,os
import zipfile
import signal,yaml
import tempfile
from django.conf import settings
from django.utils.safestring import mark_safe
import openai
import time

def run_single_batch_command(command, dir="/tmp/steampipe-mod-aws-compliance"):
    os.chdir(dir)
    cache_command=command+"-"+dir
    # Create a hash of the command to use as the cache key
    command_hash = hashlib.md5(cache_command.encode()).hexdigest()
    # command="steampipe query --output=json query.log_group_encryption_at_rest_enabled"
    command=command.split()
    # Check if the command result is already in the cache
    if cache.get(command_hash):
        logging.info("Cache used: %s", command)
        return cache.get(command_hash)

    try:
        logging.info("Cache unavailable: %s", command)
        # Run the command and capture the output
        result = subprocess.run(command,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # result = subprocess.run(command,  check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # logging.info("Cache unavailable result: %s", result)
        output = result.stdout
        # logging.info("Cache unavailable output: %s", output)
        # Store the result in the cache using the hash as the key
        cache.set(command_hash, output, timeout=settings.CACHE_TIMEOUT)  # Cache for 5 minutes
        return output
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}" 

def run_command(command, dir):
    try:
        # Run the command and capture the output
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=dir)
        
        # Check if the command was successful
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Command failed with error: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Command failed with error: {e.stderr}"

def run_batch_command(command, dir="/tmp/steampipe-mod-aws-compliance"):
    result = run_command(command, dir) 
    # if command.count('\n') == 0:
    #     print(f"Single Line command =========> ")
    #     return run_single_batch_command(command, dir)
    
    # elif command.count('\n') > 0:
    #     print('Multiple Line ===========> ', command)
    #     lst = list(command.split('\n'))
    #     # result = run_shell_command(command, dir)
    #     result = run_command(command, dir)
    #     # result = []
    #     # for l in lst:
    #     #     result.append(run_single_batch_command(l, dir))
    #     return result
    return result





