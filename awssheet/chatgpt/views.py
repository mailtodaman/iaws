from django.shortcuts import render, redirect
from .models import ChatGPTModel
from .forms import ChatGPTForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

def list(request):
    rows = request.GET.get('rows', 10)  # Default to 10 rows if not specified
    query = request.GET.get('q', '').strip()
    
    if query:
        # Split the query into individual words
        query_words = query.split()
        
        # Build a query that checks if any field contains any of the words
        query_filter = Q()
        for word in query_words:
            query_filter |= Q(username__icontains=word) | Q(command__icontains=word) | Q(result__icontains=word)
        
        logs_list = ChatGPTModel.objects.filter(query_filter).distinct().order_by('-created_at')
    else:
        logs_list = ChatGPTModel.objects.all().order_by('-created_at')
    
    paginator = Paginator(logs_list, int(rows))  # Make sure rows is an int for Paginator
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('chatgpt/partials/logs_table_rows.html', {'logs': logs})
        return JsonResponse({'html': html})
    else:
        return render(request, 'chatgpt/list.html', {'logs': logs, 'query': query, 'rows': rows})

def create(request):
    if request.method == 'POST':
        form = ChatGPTForm(request.POST)
        if form.is_valid():
            new_command = form.save(commit=False)
            # Assume you get the result from ChatGPT here
            new_command.result = "Result from ChatGPT"
            new_command.save()
            return redirect('list')
    else:
        form = ChatGPTForm()
    return render(request, 'chatgpt/create.html', {'form': form})


@require_POST
def delete_logs(request):
    selected_logs = request.POST.getlist('selected_logs')
    
    if selected_logs:
        ChatGPTModel.objects.filter(id__in=selected_logs).delete()

    return redirect('list')  # Adjust this to the name of your listing view