from django.shortcuts import render, redirect
from .models import LogsModel
from .forms import LogsForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
def list(request):
    rows = request.GET.get('rows', 10)  # Default to 10 rows if not specified
    query = request.GET.get('q', '').strip()
    log_name = request.GET.get('log_name', 'all')  # Default to 'chatgpt' if not specified

    # Initialize the base query filter for log_type
    if log_name == "all":
        query_filter = Q()
    else:
        query_filter = Q(log_name__iexact=log_name)  # Filter by log_type matching log_name, case-insensitively

    if query:
        # Split the query into individual words
        query_words = query.split()
        
        # Extend the query filter to include checks if any field contains any of the words
        for word in query_words:
            query_filter |= Q(username__icontains=word) | Q(command__icontains=word) | Q(result__icontains=word)

    # Apply the constructed filter to the queryset
    logs_list = LogsModel.objects.filter(query_filter).distinct().order_by('-created_at')
    
    paginator = Paginator(logs_list, int(rows))  # Ensure rows is an int for Paginator
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('logs/partials/logs_table_rows.html', {'logs': logs})
        return JsonResponse({'html': html})
    else:
        return render(request, 'logs/list.html', {'logs': logs, 'query': query, 'rows': rows, 'log_name': log_name.capitalize()})

@login_required
def create(request):
    if request.method == 'POST':
        form = LogsForm(request.POST)
        if form.is_valid():
            new_command = form.save(commit=False)
            # Assume you get the result from ChatGPT here
            new_command.result = "Result from ChatGPT"
            new_command.save()
            return redirect('list')
    else:
        form = LogsForm()
    return render(request, 'logs/create.html', {'form': form})

@login_required
@require_POST
def delete_logs(request):
    selected_logs = request.POST.getlist('selected_logs')
    
    if selected_logs:
        ChatGPTModel.objects.filter(id__in=selected_logs).delete()

    return redirect('list')  # Adjust this to the name of your listing view