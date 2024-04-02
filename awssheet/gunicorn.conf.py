# Sample Gunicorn configuration file: gunicorn.conf.py

import multiprocessing
import os

# Configuration to preload the application before starting the worker processes
preload_app = True
# gunicorn.conf.py

accesslog = "-"  # "-" means log to stdout
errorlog = "-"  # "-" means log to stderr
loglevel = "debug"
capture_output = True  # To capture stdout/stderr in the error log

# Define the log directory and file
log_base_dir = "/tmp/iaws/logs"
if not os.path.exists(log_base_dir):
    os.makedirs(log_base_dir)
log_file_path = os.path.join(log_base_dir, "gunicorn.log")

# Additional configuration to write logs to a file
import logging
from logging.handlers import RotatingFileHandler

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(log_file_path, maxBytes=1024*1024*100, backupCount=20)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root_logger.addHandler(handler)

# The socket to bind.
# A string of the form: 'HOST', 'HOST:PORT', 'unix:PATH'. An IP is a valid HOST.
bind = '0.0.0.0:8001'  # Change to '127.0.0.1:8000' if you want to bind to localhost

# The number of worker processes for handling requests.
workers = multiprocessing.cpu_count() * 2 + 1

# The number of worker threads for handling requests. This is only relevant if you're using Gthread workers.
threads = 3
worker_class = 'gevent'  # For IO-bound applications

worker_class = 'gthread'
threads = 3  # Number of threads per worker

# Workers silent for more than this many seconds are killed and restarted.
timeout = 30

# A base to use with setproctitle for process naming.
# This affects things like `ps` and `top`. It's useful for identifying Gunicorn processes.
proc_name = 'iaws_gunicorn'



# The granularity of Error log outputs.
loglevel = 'debug'

# The Access log format.
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Whether to send Django output to the error log
capture_output = True

# The maximum number of requests a worker will process before restarting.
# This is a simple method to help limit the damage of memory leaks.
max_requests = 1000

# If a worker does not notify the master process in this number of
# seconds, it is killed and a new worker is spawned to replace it.
timeout = 30

# To avoid load balancers sending requests to workers that are about to be
# restarted, use this parameter. It will put the worker to sleep for a
# set number of seconds just before the restart, effectively signaling
# the load balancer to avoid sending requests to this process.
graceful_timeout = 30

