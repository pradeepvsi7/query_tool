from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_2),
    path('status/', views.get_qc_list_view),
    path('qc_individual/', views.qc_individual_count),
    path('dev_individual/', views.dev_individual_count),
    path('jr_dev_individual/', views.jr_dev_individual_count),
    path('qc_team/', views.qc_team_count),
    path('dev_team/', views.dev_team_count),
    path('qc_monthly/', views.qc_month_count),
    path('unassigned_files/', views.get_files),
    path('test/', views.sample),
    path('download/', views.download_file)
]
