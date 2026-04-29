from django.db.models import Q
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import NotificationLog
from .forms import PublicConsultationForm, NotificationLogForm
from datetime import datetime

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Student, ClassRoom, Enrollment, ProgressRecord, Attendance, ConsultationReservation
from .forms import StudentForm, ClassRoomForm, EnrollmentForm, ProgressRecordForm, ConsultationReservationForm



def dashboard(request):
    today = timezone.localdate()

    student_count = Student.objects.count()
    classroom_count = ClassRoom.objects.count()
    enrollment_count = Enrollment.objects.count()
    progress_count = ProgressRecord.objects.count()

    waiting_consultation_count = ConsultationReservation.objects.filter(
        status__in=["waiting", "scheduled"]
    ).count()
    completed_consultation_count = ConsultationReservation.objects.filter(
        status="completed"
    ).count()

    total_enrollments = Enrollment.objects.count()
    checked_today_count = Attendance.objects.filter(date=today).count()
    unchecked_today_count = max(total_enrollments - checked_today_count, 0)

    recent_students = Student.objects.order_by("-created_at")[:5]
    recent_progress = ProgressRecord.objects.select_related(
        "student",
        "classroom"
    ).order_by("-created_at")[:5]

    recent_consultations = ConsultationReservation.objects.order_by(
        "-created_at"
    )[:5]

    return render(request, "academy/dashboard.html", {
        "student_count": student_count,
        "classroom_count": classroom_count,
        "enrollment_count": enrollment_count,
        "progress_count": progress_count,
        "waiting_consultation_count": waiting_consultation_count,
        "completed_consultation_count": completed_consultation_count,
        "unchecked_today_count": unchecked_today_count,
        "recent_students": recent_students,
        "recent_progress": recent_progress,
        "recent_consultations": recent_consultations,
        "today": today,
    })


def student_list(request):
    q = request.GET.get("q", "").strip()
    school = request.GET.get("school", "").strip()
    grade = request.GET.get("grade", "").strip()
    classroom_id = request.GET.get("classroom", "").strip()
    sort = request.GET.get("sort", "name").strip()

    students = Student.objects.prefetch_related("enrollments__classroom").all()

    if q:
        students = students.filter(
            Q(name__icontains=q) |
            Q(school__icontains=q) |
            Q(grade__icontains=q) |
            Q(parent_phone__icontains=q) |
            Q(phone__icontains=q)
        )

    if school:
        students = students.filter(school=school)

    if grade:
        students = students.filter(grade=grade)

    if classroom_id:
        students = students.filter(enrollments__classroom_id=classroom_id)

    sort_map = {
        "name": "name",
        "school": "school",
        "grade": "grade",
        "recent": "-created_at",
    }
    students = students.order_by(sort_map.get(sort, "name")).distinct()

    school_options = Student.objects.exclude(
        school=""
    ).values_list("school", flat=True).distinct().order_by("school")

    grade_options = Student.objects.exclude(
        grade=""
    ).values_list("grade", flat=True).distinct().order_by("grade")

    classrooms = ClassRoom.objects.all().order_by("name")

    return render(request, "academy/student_list.html", {
        "students": students,
        "q": q,
        "school": school,
        "grade": grade,
        "classroom_id": classroom_id,
        "sort": sort,
        "school_options": school_options,
        "grade_options": grade_options,
        "classrooms": classrooms,
    })

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)

    enrollments = student.enrollments.select_related('classroom')
    progress_records = student.progress_records.select_related('classroom')[:10]
    attendances = student.attendances.select_related('classroom')[:10]

    return render(request, 'academy/student_detail.html', {
        'student': student,
        'enrollments': enrollments,
        'progress_records': progress_records,
        'attendances': attendances,
    })


def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'{student.name} 학생이 등록되었습니다.')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm()

    return render(request, 'academy/student_form.html', {
        'form': form,
        'title': '학생 등록',
        'button_text': '학생 저장하기',
    })


def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'{student.name} 학생 정보가 수정되었습니다.')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)

    return render(request, 'academy/student_form.html', {
        'form': form,
        'title': '학생 정보 수정',
        'button_text': '수정하기',
    })


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        name = student.name
        student.delete()
        messages.success(request, f'{name} 학생 정보가 삭제되었습니다.')
        return redirect('student_list')

    return render(request, 'academy/student_confirm_delete.html', {
        'student': student,
    })


def classroom_list(request):
    classrooms = ClassRoom.objects.annotate(
        student_count=Count('enrollments')
    ).order_by('name')

    return render(request, 'academy/classroom_list.html', {
        'classrooms': classrooms,
    })


def classroom_detail(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)

    enrollments = classroom.enrollments.select_related('student')
    progress_records = classroom.progress_records.select_related('student')[:10]

    return render(request, 'academy/classroom_detail.html', {
        'classroom': classroom,
        'enrollments': enrollments,
        'progress_records': progress_records,
    })


def classroom_create(request):
    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            classroom = form.save()
            messages.success(request, f'{classroom.name} 수업반이 생성되었습니다.')
            return redirect('classroom_detail', pk=classroom.pk)
    else:
        form = ClassRoomForm()

    return render(request, 'academy/classroom_form.html', {
        'form': form,
        'title': '수업반 등록',
        'button_text': '수업반 저장하기',
    })


def classroom_update(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)

    if request.method == 'POST':
        form = ClassRoomForm(request.POST, instance=classroom)
        if form.is_valid():
            classroom = form.save()
            messages.success(request, f'{classroom.name} 수업반 정보가 수정되었습니다.')
            return redirect('classroom_detail', pk=classroom.pk)
    else:
        form = ClassRoomForm(instance=classroom)

    return render(request, 'academy/classroom_form.html', {
        'form': form,
        'title': '수업반 수정',
        'button_text': '수정하기',
    })


def classroom_delete(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)

    if request.method == 'POST':
        name = classroom.name
        classroom.delete()
        messages.success(request, f'{name} 수업반이 삭제되었습니다.')
        return redirect('classroom_list')

    return render(request, 'academy/classroom_confirm_delete.html', {
        'classroom': classroom,
    })


def enrollment_list(request):
    enrollments = Enrollment.objects.select_related(
        'student',
        'classroom'
    ).order_by('-enrolled_at')

    return render(request, 'academy/enrollment_list.html', {
        'enrollments': enrollments,
    })


def enrollment_create(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(
                request,
                f'{enrollment.student.name} 학생이 {enrollment.classroom.name} 수업반에 배정되었습니다.'
            )
            return redirect('enrollment_list')
    else:
        form = EnrollmentForm()

    return render(request, 'academy/enrollment_form.html', {
        'form': form,
    })


@require_POST
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    enrollment.delete()
    messages.success(request, '수강 등록 정보가 삭제되었습니다.')
    return redirect('enrollment_list')


def progress_list(request):
    q = request.GET.get('q', '').strip()
    records = ProgressRecord.objects.select_related('student', 'classroom')

    if q:
        records = records.filter(
            Q(student__name__icontains=q) |
            Q(classroom__name__icontains=q) |
            Q(topic__icontains=q)
        )

    return render(request, 'academy/progress_list.html', {
        'records': records,
        'q': q,
    })


def progress_create(request):
    if request.method == 'POST':
        form = ProgressRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '진도 기록이 저장되었습니다.')
            return redirect('progress_list')
    else:
        form = ProgressRecordForm(initial={'date': timezone.localdate()})

    return render(request, 'academy/progress_form.html', {
        'form': form,
    })


@require_POST
def progress_delete(request, pk):
    record = get_object_or_404(ProgressRecord, pk=pk)
    record.delete()
    messages.success(request, '진도 기록이 삭제되었습니다.')
    return redirect('progress_list')


def parse_date_or_today(value):
    if not value:
        return timezone.localdate()

    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return timezone.localdate()


def attendance_select(request):
    classrooms = ClassRoom.objects.all()

    if request.method == 'POST':
        classroom_id = request.POST.get('classroom')
        selected_date = request.POST.get('date') or str(timezone.localdate())

        if classroom_id:
            url = reverse('attendance_check', args=[classroom_id])
            return redirect(f'{url}?date={selected_date}')

        messages.error(request, '수업반을 선택하세요.')

    return render(request, 'academy/attendance_select.html', {
        'classrooms': classrooms,
        'today': timezone.localdate(),
    })


def attendance_check(request, classroom_id):
    classroom = get_object_or_404(ClassRoom, pk=classroom_id)

    if request.method == 'POST':
        selected_date = parse_date_or_today(request.POST.get('date'))
    else:
        selected_date = parse_date_or_today(request.GET.get('date'))

    enrollments = Enrollment.objects.filter(
        classroom=classroom
    ).select_related('student').order_by('student__name')

    if request.method == 'POST':
        for enrollment in enrollments:
            student = enrollment.student
            status = request.POST.get(f'status_{student.id}', 'present')
            note = request.POST.get(f'note_{student.id}', '').strip()

            Attendance.objects.update_or_create(
                student=student,
                classroom=classroom,
                date=selected_date,
                defaults={
                    'status': status,
                    'note': note,
                }
            )

        messages.success(request, '출석 정보가 저장되었습니다.')
        url = reverse('attendance_check', args=[classroom.id])
        return redirect(f'{url}?date={selected_date}')

    existing = {
        attendance.student_id: attendance
        for attendance in Attendance.objects.filter(
            classroom=classroom,
            date=selected_date
        )
    }

    rows = []
    counts = {
        'present': 0,
        'absent': 0,
        'late': 0,
        'early': 0,
        'makeup': 0,
    }

    for enrollment in enrollments:
        student = enrollment.student
        attendance = existing.get(student.id)
        status = attendance.status if attendance else 'present'
        note = attendance.note if attendance else ''

        counts[status] += 1

        rows.append({
            'student': student,
            'status': status,
            'note': note,
        })

    return render(request, 'academy/attendance_check.html', {
        'classroom': classroom,
        'selected_date': selected_date,
        'rows': rows,
        'counts': counts,
        'total_count': len(rows),
    })

def consultation_list(request):
    status = request.GET.get("status", "").strip()
    q = request.GET.get("q", "").strip()

    consultations = ConsultationReservation.objects.all()

    if status:
        consultations = consultations.filter(status=status)

    if q:
        consultations = consultations.filter(
            Q(parent_name__icontains=q) |
            Q(student_name__icontains=q) |
            Q(phone__icontains=q) |
            Q(school__icontains=q)
        )

    counts = {
        "waiting": ConsultationReservation.objects.filter(status="waiting").count(),
        "scheduled": ConsultationReservation.objects.filter(status="scheduled").count(),
        "completed": ConsultationReservation.objects.filter(status="completed").count(),
        "canceled": ConsultationReservation.objects.filter(status="canceled").count(),
    }

    return render(request, "academy/consultation_list.html", {
        "consultations": consultations,
        "status": status,
        "q": q,
        "counts": counts,
    })


def consultation_create(request):
    if request.method == "POST":
        form = ConsultationReservationForm(request.POST)
        if form.is_valid():
            consultation = form.save()
            messages.success(request, "방문상담 예약이 등록되었습니다.")
            return redirect("consultation_detail", pk=consultation.pk)
    else:
        form = ConsultationReservationForm()

    return render(request, "academy/consultation_form.html", {
        "form": form,
        "title": "방문상담 예약 등록",
        "button_text": "예약 저장하기",
    })


def consultation_detail(request, pk):
    consultation = get_object_or_404(ConsultationReservation, pk=pk)

    return render(request, "academy/consultation_detail.html", {
        "consultation": consultation,
    })


def consultation_update(request, pk):
    consultation = get_object_or_404(ConsultationReservation, pk=pk)

    if request.method == "POST":
        form = ConsultationReservationForm(request.POST, instance=consultation)
        if form.is_valid():
            consultation = form.save()
            messages.success(request, "방문상담 예약 정보가 수정되었습니다.")
            return redirect("consultation_detail", pk=consultation.pk)
    else:
        form = ConsultationReservationForm(instance=consultation)

    return render(request, "academy/consultation_form.html", {
        "form": form,
        "title": "방문상담 예약 수정",
        "button_text": "수정하기",
    })


@require_POST
def consultation_set_status(request, pk, status):
    consultation = get_object_or_404(ConsultationReservation, pk=pk)

    allowed = ["waiting", "scheduled", "completed", "canceled"]
    if status not in allowed:
        messages.error(request, "잘못된 상담 상태입니다.")
        return redirect("consultation_detail", pk=consultation.pk)

    consultation.status = status
    consultation.save(update_fields=["status", "updated_at"])
    messages.success(request, "상담 상태가 변경되었습니다.")
    return redirect("consultation_detail", pk=consultation.pk)


@require_POST
def consultation_delete(request, pk):
    consultation = get_object_or_404(ConsultationReservation, pk=pk)
    consultation.delete()
    messages.success(request, "방문상담 예약이 삭제되었습니다.")
    return redirect("consultation_list")


def attendance_report(request):
    selected_date = parse_date_or_today(request.GET.get("date"))
    classroom_id = request.GET.get("classroom", "").strip()
    q = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    enrollments = Enrollment.objects.select_related(
        "student",
        "classroom"
    ).order_by("classroom__name", "student__name")

    if classroom_id:
        enrollments = enrollments.filter(classroom_id=classroom_id)

    if q:
        enrollments = enrollments.filter(
            Q(student__name__icontains=q) |
            Q(student__school__icontains=q) |
            Q(student__grade__icontains=q)
        )

    attendance_qs = Attendance.objects.filter(date=selected_date)
    if classroom_id:
        attendance_qs = attendance_qs.filter(classroom_id=classroom_id)

    existing = {
        (attendance.student_id, attendance.classroom_id): attendance
        for attendance in attendance_qs
    }

    status_labels = dict(Attendance.STATUS_CHOICES)
    status_labels["unchecked"] = "미체크"

    counts = {
        "present": 0,
        "absent": 0,
        "late": 0,
        "early": 0,
        "makeup": 0,
        "unchecked": 0,
    }

    rows = []

    for enrollment in enrollments:
        key = (enrollment.student_id, enrollment.classroom_id)
        attendance = existing.get(key)

        if attendance:
            status = attendance.status
            note = attendance.note
        else:
            status = "unchecked"
            note = ""

        counts[status] += 1

        if status_filter and status != status_filter:
            continue

        rows.append({
            "student": enrollment.student,
            "classroom": enrollment.classroom,
            "date": selected_date,
            "status": status,
            "status_display": status_labels.get(status, status),
            "note": note,
        })

    classrooms = ClassRoom.objects.all().order_by("name")
    status_options = [
        ("", "전체"),
        ("present", "출석"),
        ("absent", "결석"),
        ("late", "지각"),
        ("early", "조퇴"),
        ("makeup", "보강"),
        ("unchecked", "미체크"),
    ]

    return render(request, "academy/attendance_report.html", {
        "selected_date": selected_date,
        "classroom_id": classroom_id,
        "q": q,
        "status_filter": status_filter,
        "rows": rows,
        "counts": counts,
        "classrooms": classrooms,
        "status_options": status_options,
    })

def user_is_owner(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="Owner").exists()
    )


def make_notification_for_consultation(consultation, category, message, status="waiting"):
    return NotificationLog.objects.create(
        consultation=consultation,
        notification_type="sms",
        category=category,
        recipient_name=consultation.parent_name,
        phone=consultation.phone,
        message=message,
        status=status,
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "로그인되었습니다.")
            return redirect("dashboard")
        messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")

    return render(request, "academy/login.html", {
        "form": form,
    })


def logout_view(request):
    logout(request)
    messages.success(request, "로그아웃되었습니다.")
    return redirect("login")


def public_apply(request):
    if request.method == "POST":
        form = PublicConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.status = "waiting"
            consultation.save()

            make_notification_for_consultation(
                consultation,
                "consultation_received",
                f"[EduManager] {consultation.student_name} 학생의 방문상담 예약이 접수되었습니다. 희망일: {consultation.preferred_date} {consultation.preferred_time.strftime('%H:%M')}",
            )

            return redirect("public_apply_done")
    else:
        form = PublicConsultationForm()

    return render(request, "academy/public_apply.html", {
        "form": form,
    })


def public_apply_done(request):
    return render(request, "academy/public_apply_done.html")


def notification_list(request):
    status = request.GET.get("status", "").strip()
    category = request.GET.get("category", "").strip()
    q = request.GET.get("q", "").strip()

    notifications = NotificationLog.objects.select_related("consultation").all()

    if status:
        notifications = notifications.filter(status=status)

    if category:
        notifications = notifications.filter(category=category)

    if q:
        notifications = notifications.filter(
            Q(recipient_name__icontains=q) |
            Q(phone__icontains=q) |
            Q(message__icontains=q)
        )

    counts = {
        "waiting": NotificationLog.objects.filter(status="waiting").count(),
        "sent": NotificationLog.objects.filter(status="sent").count(),
        "failed": NotificationLog.objects.filter(status="failed").count(),
    }

    return render(request, "academy/notification_list.html", {
        "notifications": notifications,
        "status": status,
        "category": category,
        "q": q,
        "counts": counts,
    })


@require_POST
def notification_mark_sent(request, pk):
    notification = get_object_or_404(NotificationLog, pk=pk)
    notification.status = "sent"
    notification.sent_at = timezone.now()
    notification.save(update_fields=["status", "sent_at"])
    messages.success(request, "알림을 발송 완료로 처리했습니다.")
    return redirect("notification_list")


@require_POST
def notification_mark_failed(request, pk):
    notification = get_object_or_404(NotificationLog, pk=pk)
    notification.status = "failed"
    notification.save(update_fields=["status"])
    messages.success(request, "알림을 발송 실패로 처리했습니다.")
    return redirect("notification_list")


@require_POST
def consultation_set_status(request, pk, status):
    consultation = get_object_or_404(ConsultationReservation, pk=pk)

    allowed = ["waiting", "scheduled", "completed", "canceled"]
    if status not in allowed:
        messages.error(request, "잘못된 상담 상태입니다.")
        return redirect("consultation_detail", pk=consultation.pk)

    consultation.status = status
    consultation.save(update_fields=["status", "updated_at"])

    category_map = {
        "waiting": "consultation_received",
        "scheduled": "consultation_scheduled",
        "completed": "consultation_completed",
        "canceled": "consultation_canceled",
    }

    message_map = {
        "waiting": f"[EduManager] {consultation.student_name} 학생의 방문상담 예약이 접수되었습니다.",
        "scheduled": f"[EduManager] {consultation.student_name} 학생의 방문상담 일정이 확정되었습니다. 희망일: {consultation.preferred_date} {consultation.preferred_time.strftime('%H:%M')}",
        "completed": f"[EduManager] {consultation.student_name} 학생의 방문상담이 완료 처리되었습니다.",
        "canceled": f"[EduManager] {consultation.student_name} 학생의 방문상담 예약이 취소 처리되었습니다.",
    }

    make_notification_for_consultation(
        consultation,
        category_map[status],
        message_map[status],
    )

    messages.success(request, "상담 상태가 변경되었고 알림 발송 로그가 생성되었습니다.")
    return redirect("consultation_detail", pk=consultation.pk)
