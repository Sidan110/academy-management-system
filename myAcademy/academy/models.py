from django.db import models
from django.utils import timezone


class Student(models.Model):
    name = models.CharField("학생명", max_length=50)
    school = models.CharField("학교", max_length=100, blank=True)
    grade = models.CharField("학년", max_length=20, blank=True)
    phone = models.CharField("학생 연락처", max_length=30, blank=True)
    parent_phone = models.CharField("학부모 연락처", max_length=30, blank=True)
    address = models.CharField("주소", max_length=255, blank=True)
    memo = models.TextField("메모", blank=True)
    created_at = models.DateTimeField("등록일", auto_now_add=True)

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.CharField("수업명", max_length=100)
    teacher = models.CharField("담당 선생님", max_length=50)
    day_of_week = models.CharField("수업 요일", max_length=50)
    start_time = models.TimeField("시작 시간")
    end_time = models.TimeField("종료 시간")
    room = models.CharField("강의실", max_length=50, blank=True)
    description = models.TextField("수업 설명", blank=True)
    created_at = models.DateTimeField("생성일", auto_now_add=True)

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments", verbose_name="학생")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="enrollments", verbose_name="수업반")
    enrolled_at = models.DateField("수강 등록일", auto_now_add=True)

    class Meta:
        unique_together = ("student", "classroom")

    def __str__(self):
        return f"{self.student.name} - {self.classroom.name}"


class ProgressRecord(models.Model):
    UNDERSTANDING_CHOICES = [
        ("good", "좋음"),
        ("normal", "보통"),
        ("need_help", "추가 지도 필요"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="progress_records", verbose_name="학생")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="progress_records", verbose_name="수업반")
    date = models.DateField("수업 날짜", default=timezone.localdate)
    topic = models.CharField("수업 진도", max_length=200)
    homework = models.CharField("숙제", max_length=200, blank=True)
    understanding = models.CharField("이해도", max_length=20, choices=UNDERSTANDING_CHOICES, default="normal")
    memo = models.TextField("메모", blank=True)
    created_at = models.DateTimeField("작성일", auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.topic}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "출석"),
        ("absent", "결석"),
        ("late", "지각"),
        ("early", "조퇴"),
        ("makeup", "보강"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances", verbose_name="학생")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="attendances", verbose_name="수업반")
    date = models.DateField("출석 날짜", default=timezone.localdate)
    status = models.CharField("출석 상태", max_length=20, choices=STATUS_CHOICES, default="present")
    note = models.CharField("비고", max_length=200, blank=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        unique_together = ("student", "classroom", "date")

    def __str__(self):
        return f"{self.date} {self.student.name} {self.get_status_display()}"

class ConsultationReservation(models.Model):
    STATUS_CHOICES = [
        ("waiting", "예약 접수"),
        ("scheduled", "상담 예정"),
        ("completed", "상담 완료"),
        ("canceled", "취소"),
    ]

    parent_name = models.CharField("학부모 이름", max_length=50)
    student_name = models.CharField("학생 이름", max_length=50)
    school = models.CharField("학교", max_length=100, blank=True)
    grade = models.CharField("학년", max_length=20, blank=True)
    phone = models.CharField("연락처", max_length=30)
    preferred_date = models.DateField("희망 상담 날짜")
    preferred_time = models.TimeField("희망 상담 시간")
    purpose = models.TextField("상담 목적")
    status = models.CharField(
        "상담 상태",
        max_length=20,
        choices=STATUS_CHOICES,
        default="waiting"
    )
    result_memo = models.TextField("상담 결과 메모", blank=True)
    created_at = models.DateTimeField("신청일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        ordering = ["preferred_date", "preferred_time", "-created_at"]

    def __str__(self):
        return f"{self.preferred_date} {self.student_name} 상담"
