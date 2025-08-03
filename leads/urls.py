from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('create/', views.lead_create_view, name='lead_create'),
    path('list/', views.lead_list_view, name='lead_list'),
    path('detail/<uuid:lead_id>/', views.lead_detail_view, name='lead_detail'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('add-activity/<uuid:lead_id>/', views.add_activity_view, name='add_activity'),
    path('mark-task-complete/<int:activity_id>/', views.mark_task_complete, name='mark_task_complete'),
    path('add-task-note/<int:activity_id>/', views.add_task_note, name='add_task_note'),
    path('postpone-task/<int:activity_id>/', views.postpone_task, name='postpone_task'),
    path('call-recordings/', views.call_recordings_view, name='call_recordings'),
]