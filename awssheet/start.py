import socket
import subprocess
import sys

def is_steampipe_running(host='localhost', port=9193):
    """
    Check if Steampipe is running by attempting to connect to its default port.
    
    :param host: The hostname where Steampipe is expected to run.
    :param port: The port number where Steampipe listens.
    :return: True if connection is successful, False otherwise.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def start_steampipe():
    """
    Start Steampipe using the 'steampipe service start' command.
    
    Exits the script if Steampipe fails to start.
    """
    try:
        print("Starting Steampipe...")
        subprocess.check_call(['steampipe', 'service', 'start'])
        print("Steampipe started successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to start Steampipe: ", e)
        sys.exit(1)

if __name__ == "__main__":
    # Check if Steampipe is running
    if not is_steampipe_running():
        print("Steampipe is not running, attempting to start it...")
        start_steampipe()
    else:
        print("Steampipe is already running.")

    # Here you can place the code to start your Django project or Gunicorn server.
    # For example, to run a Django project:
    # subprocess.call(['python', 'manage.py', 'runserver'])
    # Or to start Gunicorn:
subprocess.call(['gunicorn', 'awssheet.wsgi:application'])
