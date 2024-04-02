# scheduler/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import ScheduledTask
from .forms import ScheduledTaskForm
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import ScheduledTask
from django.contrib.auth.decorators import login_required

@login_required
def add_task(request):
    """
    View to add a new scheduled task.
    """
    if request.method == 'POST':
        form = ScheduledTaskForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
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