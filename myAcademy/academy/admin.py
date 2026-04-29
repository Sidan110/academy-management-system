from django.contrib import admin

from .models import (
    Student,
    ClassRoom,
    Enrollment,
    ProgressRecord,
    Attendance,
    ConsultationReservation,
    NotificationLog,
    PaymentInvoice,
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "grade", "phone", "parent_phone", "created_at")
    search_fields = ("name", "school", "grade", "phone", "parent_phone")
    list_filter = ("school", "grade")


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "teacher", "day_of_week", "start_time", "end_time", "room")
    search_fields = ("name", "teacher", "room")
    list_filter = ("teacher", "day_of_week")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "classroom", "enrolled_at")
    search_fields = ("student__name", "classroom__name")
    list_filter = ("classroom", "enrolled_at")


@admin.register(ProgressRecord)
class ProgressRecordAdmin(admin.ModelAdmin):
    list_display = ("date", "student", "classroom", "topic", "understanding", "created_at")
    search_fields = ("student__name", "classroom__name", "topic", "homework", "memo")
    list_filter = ("date", "classroom", "understanding")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("date", "student", "classroom", "status", "note", "updated_at")
    search_fields = ("student__name", "classroom__name", "note")
    list_filter = ("date", "classroom", "status")


@admin.register(ConsultationReservation)
class ConsultationReservationAdmin(admin.ModelAdmin):
    list_display = (
        "preferred_date",
        "preferred_time",
        "parent_name",
        "student_name",
        "grade",
        "phone",
        "status",
        "created_at",
    )
    list_filter = ("status", "preferred_date", "grade")
    search_fields = ("parent_name", "student_name", "phone", "school")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "notification_type",
        "category",
        "recipient_name",
        "phone",
        "status",
        "sent_at",
    )
    list_filter = ("notification_type", "category", "status", "created_at")
    search_fields = ("recipient_name", "phone", "message")


@admin.register(PaymentInvoice)
class PaymentInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "billing_month",
        "student",
        "total_amount",
        "paid_amount",
        "remaining_amount",
        "status",
        "due_date",
        "paid_date",
    )
    list_filter = ("status", "billing_month", "due_date")
    search_fields = ("student__name", "student__school", "billing_month")
