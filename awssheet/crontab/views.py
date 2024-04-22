from django.shortcuts import render
import schedule
import time
from batchcmd.views import run_batch_command
from scheduler.models import ScheduledTask, TaskResult
        
def task_result_view(task):
    cmd = task.command
    result = run_batch_command(cmd, "/run/media/mahmud/Data/iawstest")
    data = TaskResult(task=task, result=result)
    print('============> data save successfully', data)
    data.save()
        










