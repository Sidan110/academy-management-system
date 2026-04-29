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

    path('attendance/report/', views.attendance_report, name='attendance_report'),

    path('consultations/', views.consultation_list, name='consultation_list'),
    path('consultations/new/', views.consultation_create, name='consultation_create'),
    path('consultations/<int:pk>/', views.consultation_detail, name='consultation_detail'),
    path('consultations/<int:pk>/edit/', views.consultation_update, name='consultation_update'),
    path('consultations/<int:pk>/status/<str:status>/', views.consultation_set_status, name='consultation_set_status'),
    path('consultations/<int:pk>/delete/', views.consultation_delete, name='consultation_delete'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('apply/', views.public_apply, name='public_apply'),
    path('apply/done/', views.public_apply_done, name='public_apply_done'),

    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/sent/', views.notification_mark_sent, name='notification_mark_sent'),
    path('notifications/<int:pk>/failed/', views.notification_mark_failed, name='notification_mark_failed'),

    path('payments/', views.payment_list, name='payment_list'),
    path('payments/new/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/edit/', views.payment_update, name='payment_update'),
    path('payments/<int:pk>/paid/', views.payment_mark_paid, name='payment_mark_paid'),
    path('payments/<int:pk>/overdue/', views.payment_mark_overdue, name='payment_mark_overdue'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),

    path('checkin/', views.public_checkin, name='public_checkin'),
]
