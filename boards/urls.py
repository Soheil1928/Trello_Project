from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserView.as_view(), name='users'),
    path('profiles/', views.ProfileView.as_view(), name='profiles'),
    path('profiles/<int:pk>', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('project-list/', views.ProjectListView.as_view(), name='project_list'),
    path('project-list/<int:pk>', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project-list/<int:pk>/members/', views.ProjectMemberListView.as_view(), name='members_list'),
    path('project-list/<int:proj_id>/members/<int:mem_id>', views.ProjectMemberDetailView.as_view(), name='members_detail'),
    path('project-list/<int:proj_id>/boards', views.BoardListView.as_view(), name='board_list'),
    path('project-list/<int:proj_id>/boards/<int:board_id>/', views.BoardDetailsView.as_view(), name='board_detail'),
    path('project-list/<int:proj_id>/boards/<int:board_id>/tasks', views.TaskListView.as_view(), name='task_list'),
    path('project-list/<int:proj_id>/boards/<int:board_id>/tasks/<int:task_id>', views.TaskEditView.as_view(), name='task_edit'),

]