from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('create/', views.lead_create_view, name='lead_create'),
    path('list/', views.lead_list_view, name='lead_list'),
    path('detail/<uuid:lead_id>/', views.lead_detail_view, name='lead_detail'),
    path('tasks/', views.tasks_view, name='tasks'),
]