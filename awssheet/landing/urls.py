from django.urls import path

from . import views

# path("", views.login, name="login"),
urlpatterns = [
    
    path("", views.login_view, name='login'),
    path('aws_logout', views.aws_logout, name='aws_logout'),
    path("index/", views.index, name="index"),
    path("table/<str:table_name>/", views.table_view, name="table"),
    path("table_object_view/<str:table_name>/", views.table_object_view, name="table_object_view"),
    path("platform_tables/", views.platform_tables, name="platform_tables"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("compliance_by_servicename_view/<str:platform_name>/", views.compliance_by_servicename_view, name="compliance_by_servicename_view"),
    path("compliance_report_by_servicename/<str:platform_name>/<str:service_name>/", views.compliance_report_by_servicename, name="compliance_report_by_servicename"),
    path("benchmark_view/<str:platform_name>/", views.benchmark_view, name="benchmark_view"),
    path("benchmark_report/<str:platform_name>/<str:benchmark_name>/", views.benchmark_report, name="benchmark_report"),
    path("custom_query_view", views.custom_query_view, name="custom_query_view"),
    path('execute-command/', views.command_view, name='execute-command'),
    path('execute-ai-command/', views.ai_command_view, name='execute-ai-command'),
    path('terminal/', views.terminal_view, name='terminal'),
    path('store_heading_path_data/', views.store_heading_path_data,name='store_heading_path_data'),
    path('dynamic_view_form/', views.dynamic_view_form, name='dynamic_view_form'),
    path('yaml_handler/', views.yaml_handler, name='yaml_handler'),
    path('dynamic_form_process/',  views.dynamic_form_process, name='dynamic_form_process'),
    path('terraform_import_process/',  views.terraform_import_process, name='terraform_import_process'),
    path('search/',  views.search, name='search'),

    
    # path('dynamic_form_poll/', views.dynamic_form_poll, name='dynamic_form_poll'),

]

