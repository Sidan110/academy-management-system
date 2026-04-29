from django.contrib import admin
from .models import Student, ClassRoom, Enrollment, ProgressRecord, Attendance, ConsultationReservation

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'grade', 'parent_phone', 'created_at')
    search_fields = ('name', 'school', 'grade', 'parent_phone')


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'day_of_week', 'start_time', 'end_time', 'room')
    search_fields = ('name', 'teacher', 'room')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'enrolled_at')
    list_filter = ('classroom',)


@admin.register(ProgressRecord)
class ProgressRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'date', 'topic', 'understanding')
    list_filter = ('classroom', 'understanding', 'date')
    search_fields = ('student__name', 'classroom__name', 'topic')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'student', 'classroom', 'status', 'note')
    list_filter = ('date', 'classroom', 'status')
    search_fields = ('student__name', 'classroom__name')

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
