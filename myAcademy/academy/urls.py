from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('students/', views.student_list, name='student_list'),
    path('students/new/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),

    path('classes/', views.classroom_list, name='classroom_list'),
    path('classes/new/', views.classroom_create, name='classroom_create'),
    path('classes/<int:pk>/', views.classroom_detail, name='classroom_detail'),
    path('classes/<int:pk>/edit/', views.classroom_update, name='classroom_update'),
    path('classes/<int:pk>/delete/', views.classroom_delete, name='classroom_delete'),

    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    path('enrollments/new/', views.enrollment_create, name='enrollment_create'),
    path('enrollments/<int:pk>/delete/', views.enrollment_delete, name='enrollment_delete'),

    path('progress/', views.progress_list, name='progress_list'),
    path('progress/new/', views.progress_create, name='progress_create'),
    path('progress/<int:pk>/delete/', views.progress_delete, name='progress_delete'),

    path('attendance/', views.attendance_select, name='attendance_select'),
    path('attendance/<int:classroom_id>/', views.attendance_check, name='attendance_check'),
]
