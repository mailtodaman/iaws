# scheduler/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import ScheduledTask
from .forms import ScheduledTaskForm
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import ScheduledTask
from django.contrib.auth.decorators import login_required
from crontab.views import task_result_view

import schedule
from croniter import croniter
import time
import subprocess
import threading

# scheduler =======================
def parse_crontab_expression(expression):
	# Split the expression by space to get individual components
	components = expression.split()

	# Initialize parsed values to None
	minute = hour = day_of_month = month = day_of_week = None

	# Parse minute component
	if components[0] == '*':
		minute = '*'
	elif '-' in components[0]:
		start, end = map(int, components[0].split('-'))
		minute = list(range(start, end + 1))
	elif '/' in components[0]:
		start, step = map(int, components[0].split('/'))
		minute = list(range(0, 60, step))
	else:
		minute = [int(components[0])]

	# Parse hour component
	if components[1] == '*':
		hour = '*'
	elif '-' in components[1]:
		start, end = map(int, components[1].split('-'))
		hour = list(range(start, end + 1))
	elif '/' in components[1]:
		start, step = map(int, components[1].split('/'))
		hour = list(range(0, 24, step))
	else:
		hour = [int(components[1])]

	# Parse day of month component
	if components[2] == '*':
		day_of_month = '*'
	elif '-' in components[2]:
		start, end = map(int, components[2].split('-'))
		day_of_month = list(range(start, end + 1))
	elif '/' in components[2]:
		start, step = map(int, components[2].split('/'))
		day_of_month = list(range(1, 32, step))
	else:
		day_of_month = [int(components[2])]

	# Parse month component
	if components[3] == '*':
		month = '*'
	elif '-' in components[3]:
		start, end = map(int, components[3].split('-'))
		month = list(range(start, end + 1))
	else:
		month = [int(components[3])]

	# Parse day of week component
	if components[4] == '*':
		day_of_week = '*'
	elif '-' in components[4]:
		start, end = map(int, components[4].split('-'))
		day_of_week = list(range(start, end + 1))
	else:
		day_of_week = [int(components[4])]

	return minute, hour, day_of_month, month, day_of_week

def your_task_to_run():
	print("Task is running! ==========> ")

def schedule_task(task, expression):
	minute, hour, day_of_month, month, day_of_week = parse_crontab_expression(expression)
	
	# Build the schedule based on parsed values
	if minute == '*' and hour == '*' and day_of_month == '*' and month == '*' and day_of_week == '*':
		# If all fields are '*', run task every minute
		schedule.every().minute.do(task_result_view,task)
		# schedule.every(3).seconds.do(task_result_view,task)
	elif minute == '*' and hour != '*' and day_of_month != '*' and month != '*' and day_of_week != '*':
		# If only hour, day of month, month, and day of week are specified
		schedule.every().day.at(f"{hour}:00").do(task_result_view,task)
	elif minute != '*' and hour != '*' and day_of_month != '*' and month != '*' and day_of_week != '*':
		# If all fields are specified
		for m in minute:
			for h in hour:
				for d in day_of_month:
					for mo in month:
						for dow in day_of_week:
							schedule.every().minute.at(f"{h:02d}:{m:02d}").day.at(f"{d}").month.at(f"{mo}").day.at(f"{dow}").do(task_result_view,task)
	else:
		print('else criteria ===========> ')
		for m in minute:
			for h in hour:
				for d in day_of_month:
					for mo in month:
						for dow in day_of_week:
							schedule.every().minute.at(f"{h:02d}:{m:02d}").day.at(f"{d}").month.at(f"{mo}").day.at(f"{dow}").do(task_result_view, task)


def run_scheduler():
	while True:
		schedule.run_pending()
		time.sleep(1)

threading.Thread(target=run_scheduler).start()
# ================= end scheduler =================== 

@login_required
def add_task(request):
	"""
	View to add a new scheduled task.
	"""
	if request.method == 'POST':
		form = ScheduledTaskForm(request.POST, request.FILES)
		if form.is_valid():
			task = form.save()
			# cmd = form.cleaned_data['command']
			# print('Tesing comand ==> ', cmd, cmd.count('\n'))
			# user_cron_expr = task.schedule
			# task_result_view(task)
			# schedule_task(task)
			# schedule_task(task, user_cron_expr)
   
			# schedule input will be in minutes 
			schedul_time = int(task.schedule)
			schedule.every(schedul_time).seconds.do(task_result_view,task)
			# schedule.every(schedul_time).minutes.do(task_result_view,task)
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

