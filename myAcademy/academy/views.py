from datetime import datetime

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Student, ClassRoom, Enrollment, ProgressRecord, Attendance
from .forms import StudentForm, ClassRoomForm, EnrollmentForm, ProgressRecordForm


def dashboard(request):
    today = timezone.localdate()

    student_count = Student.objects.count()
    classroom_count = ClassRoom.objects.count()
    enrollment_count = Enrollment.objects.count()
    progress_count = ProgressRecord.objects.count()

    recent_students = Student.objects.order_by('-created_at')[:5]
    recent_progress = ProgressRecord.objects.select_related(
        'student',
        'classroom'
    ).order_by('-created_at')[:5]

    today_attendance_count = Attendance.objects.filter(date=today).count()

    return render(request, 'academy/dashboard.html', {
        'student_count': student_count,
        'classroom_count': classroom_count,
        'enrollment_count': enrollment_count,
        'progress_count': progress_count,
        'today_attendance_count': today_attendance_count,
        'recent_students': recent_students,
        'recent_progress': recent_progress,
        'today': today,
    })


def student_list(request):
    q = request.GET.get('q', '').strip()
    students = Student.objects.all()

    if q:
        students = students.filter(
            Q(name__icontains=q) |
            Q(school__icontains=q) |
            Q(grade__icontains=q) |
            Q(parent_phone__icontains=q)
        )

    return render(request, 'academy/student_list.html', {
        'students': students,
        'q': q,
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
