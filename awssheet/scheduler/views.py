# scheduler/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import ScheduledTask
from .forms import ScheduledTaskForm
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import ScheduledTask
from django.contrib.auth.decorators import login_required

import schedule
import time
import subprocess

def schedule_task(cron_expr, job_func):
    # Parse the cron expression
    cron_fields = list(map(int, cron_expr.split()))
    print('=========>', cron_fields)

    # Convert the cron expression to schedule format
    minute = cron_fields[0]
    hour = cron_fields[1]
    day_of_month = cron_fields[2]
    month = cron_fields[3]
    day_of_week = cron_fields[4]

    # Schedule the task
    schedule.every(minute).seconds.do(job_func)
    # schedule.every(hour).hours.do(job_func)
    # schedule.every(day_of_month).days.do(job_func)
    # schedule.every(month).months.do(job_func)
    # schedule.every(day_of_week).day.of_week.do(job_func)


# def schedule_task(cmd):
#     tasks = ScheduledTask.objects.all()
#     print(f'========> {cmd} ======')
#     # for task in tasks:
#     #     # Execute the command specified in the ScheduledTask object
#     #     # subprocess.run(task.command, shell=True)
#     #     print(f'========> {cmd} ======')

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

@login_required
def add_task(request):
    """
    View to add a new scheduled task.
    """
    if request.method == 'POST':
        form = ScheduledTaskForm(request.POST, request.FILES)
        if form.is_valid():
            command = form.cleaned_data['command']
            cron_expr = form.cleaned_data['schedule']
            job_func = lambda: print(f"=========> {command}")
            # form.save()
            # schedule.every(3).seconds.do(schedule_task,command)
            schedule_task(cron_expr, job_func)
            return redirect('list_tasks')
    else:
        form = ScheduledTaskForm()
    return render(request, 'scheduler/add_task.html', {'form': form})

@login_required
def list_tasks(request):
    """
    View to list all scheduled tasks.
    """
    tasks = ScheduledTask.objects.all()
    return render(request, 'scheduler/list_tasks.html', {'tasks': tasks})

# Existing views...

@login_required
def edit_task(request, task_id):
    """
    View to edit an existing scheduled task.
    """
    task = get_object_or_404(ScheduledTask, id=task_id)
    if request.method == 'POST':
        form = ScheduledTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('list_tasks')
    else:
        form = ScheduledTaskForm(instance=task)
    return render(request, 'scheduler/edit_task.html', {'form': form, 'task': task})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(ScheduledTask, id=task_id)
    return render(request, 'scheduler/task_detail.html', {'task': task})

@login_required
@require_POST
def delete_scheduled_task(request, task_id):
    task = get_object_or_404(ScheduledTask, id=task_id)
    task.delete()
    return redirect('list_tasks')

@require_POST
def delete_task_result(request, result_id):
    result = get_object_or_404(TaskResult, id=result_id)
    task_id = result.task.id  # Capture the associated task's id to redirect back to it
    result.delete()
    return redirect('task_detail', task_id=task_id)

# Start the scheduler in a separate thread
import threading
threading.Thread(target=run_scheduler).start()
