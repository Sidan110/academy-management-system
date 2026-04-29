from pathlib import Path
import re

BASE = Path("myAcademy/academy")
TEMPLATE_DIR = BASE / "templates" / "academy"
STATIC_DIR = BASE / "static" / "academy"

def read(path):
    return path.read_text(encoding="utf-8")

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def append_if_missing(path, marker, content):
    text = read(path)
    if marker not in text:
        write(path, text.rstrip() + "\n\n" + content.strip() + "\n")

def replace_block(text, start_regex, end_regex, replacement):
    pattern = re.compile(start_regex + r".*?" + end_regex, re.S)
    m = pattern.search(text)
    if not m:
        raise RuntimeError(f"블록을 찾지 못했습니다: {start_regex} ... {end_regex}")
    return text[:m.start()] + replacement.rstrip() + "\n\n" + text[m.end():]

# 1. models.py - 방문상담 예약 모델 추가
models_path = BASE / "models.py"
consultation_model = r'''
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
'''
append_if_missing(models_path, "class ConsultationReservation", consultation_model)

# 2. forms.py - 방문상담 예약 폼 추가
forms_path = BASE / "forms.py"
forms_text = read(forms_path)
if "ConsultationReservation" not in forms_text.split("\n")[0:20]:
    forms_text = forms_text.replace(
        "from .models import Student, ClassRoom, Enrollment, ProgressRecord",
        "from .models import Student, ClassRoom, Enrollment, ProgressRecord, ConsultationReservation"
    )
write(forms_path, forms_text)

consultation_form = r'''
class ConsultationReservationForm(BaseStyledForm):
    class Meta:
        model = ConsultationReservation
        fields = [
            "parent_name",
            "student_name",
            "school",
            "grade",
            "phone",
            "preferred_date",
            "preferred_time",
            "purpose",
            "status",
            "result_memo",
        ]
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "preferred_time": forms.TimeInput(attrs={"type": "time"}),
            "purpose": forms.Textarea(attrs={"rows": 4}),
            "result_memo": forms.Textarea(attrs={"rows": 4}),
        }
'''
append_if_missing(forms_path, "class ConsultationReservationForm", consultation_form)

# 3. admin.py - 방문상담 모델 관리자 등록
admin_path = BASE / "admin.py"
admin_text = read(admin_path)
admin_text = admin_text.replace(
    "from .models import Student, ClassRoom, Enrollment, ProgressRecord, Attendance",
    "from .models import Student, ClassRoom, Enrollment, ProgressRecord, Attendance, ConsultationReservation"
)
write(admin_path, admin_text)

consultation_admin = r'''
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
'''
append_if_missing(admin_path, "class ConsultationReservationAdmin", consultation_admin)

# 4. views.py import 수정
views_path = BASE / "views.py"
views_text = read(views_path)
views_text = views_text.replace(
    "from .models import Student, ClassRoom, Enrollment, ProgressRecord, Attendance",
    "from .models import Student, ClassRoom, Enrollment, ProgressRecord, Attendance, ConsultationReservation"
)
views_text = views_text.replace(
    "from .forms import StudentForm, ClassRoomForm, EnrollmentForm, ProgressRecordForm",
    "from .forms import StudentForm, ClassRoomForm, EnrollmentForm, ProgressRecordForm, ConsultationReservationForm"
)

# 5. dashboard 함수 개선
new_dashboard = r'''
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
'''
views_text = replace_block(
    views_text,
    r"def dashboard\(request\):",
    r"def student_list\(request\):",
    new_dashboard + "\n\ndef student_list(request):"
)

# 6. student_list 함수 필터 강화
new_student_list = r'''
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
'''
views_text = replace_block(
    views_text,
    r"def student_list\(request\):",
    r"def student_detail\(request, pk\):",
    new_student_list + "\n\ndef student_detail(request, pk):"
)

# 7. views.py 새 기능 함수 추가
new_views = r'''
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
'''
append_if_missing(views_path, "def consultation_list", new_views)

# append_if_missing 후 views_text가 덮이지 않게 최종 import/replace 반영
current_views = read(views_path)
if "ConsultationReservation" not in current_views.split("\n")[0:20]:
    current_views = current_views.replace(
        "from .models import Student, ClassRoom, Enrollment, ProgressRecord, Attendance",
        "from .models import Student, ClassRoom, Enrollment, ProgressRecord, Attendance, ConsultationReservation"
    )
if "ConsultationReservationForm" not in current_views.split("\n")[0:25]:
    current_views = current_views.replace(
        "from .forms import StudentForm, ClassRoomForm, EnrollmentForm, ProgressRecordForm",
        "from .forms import StudentForm, ClassRoomForm, EnrollmentForm, ProgressRecordForm, ConsultationReservationForm"
    )

# dashboard/student_list 교체 내용 반영
current_views = re.sub(
    r"def dashboard\(request\):.*?\n\ndef student_list\(request\):",
    new_dashboard.rstrip() + "\n\n" + "def student_list(request):",
    current_views,
    flags=re.S
)
current_views = re.sub(
    r"def student_list\(request\):.*?\n\ndef student_detail\(request, pk\):",
    new_student_list.rstrip() + "\n\n" + "def student_detail(request, pk):",
    current_views,
    flags=re.S
)
write(views_path, current_views)

# 8. urls.py 새 URL 추가
urls_path = BASE / "urls.py"
urls_text = read(urls_path)
if "consultation_list" not in urls_text:
    insert = r'''
    path('attendance/report/', views.attendance_report, name='attendance_report'),

    path('consultations/', views.consultation_list, name='consultation_list'),
    path('consultations/new/', views.consultation_create, name='consultation_create'),
    path('consultations/<int:pk>/', views.consultation_detail, name='consultation_detail'),
    path('consultations/<int:pk>/edit/', views.consultation_update, name='consultation_update'),
    path('consultations/<int:pk>/status/<str:status>/', views.consultation_set_status, name='consultation_set_status'),
    path('consultations/<int:pk>/delete/', views.consultation_delete, name='consultation_delete'),
'''
    head, tail = urls_text.rsplit("]", 1)
    urls_text = head.rstrip() + "\n" + insert + "]" + tail
    write(urls_path, urls_text)

# 9. base.html 메뉴 추가
base_path = TEMPLATE_DIR / "base.html"
base_text = read(base_path)
if "attendance_report" not in base_text:
    base_text = base_text.replace(
        "<a href=\"{% url 'attendance_select' %}\">출석 체크</a>",
        "<a href=\"{% url 'attendance_select' %}\">출석 체크</a>\n                <a href=\"{% url 'attendance_report' %}\">출석 현황</a>"
    )
if "consultation_list" not in base_text:
    base_text = base_text.replace(
        "<a href=\"{% url 'attendance_report' %}\">출석 현황</a>",
        "<a href=\"{% url 'attendance_report' %}\">출석 현황</a>\n                <a href=\"{% url 'consultation_list' %}\">방문상담 예약</a>"
    )
write(base_path, base_text)

# 10. dashboard.html 개선
dashboard_html = r'''
{% extends 'academy/base.html' %}

{% block title %}대시보드{% endblock %}
{% block page_title %}대시보드{% endblock %}
{% block page_description %}오늘의 학원 운영 현황과 처리해야 할 업무를 한눈에 확인합니다.{% endblock %}

{% block content %}
<section class="stat-grid wide-stats">
    <div class="stat-card">
        <span>전체 학생</span>
        <strong>{{ student_count }}</strong>
        <p>등록된 학생 수</p>
    </div>
    <div class="stat-card">
        <span>수업반</span>
        <strong>{{ classroom_count }}</strong>
        <p>운영 중인 수업반</p>
    </div>
    <div class="stat-card">
        <span>수강 등록</span>
        <strong>{{ enrollment_count }}</strong>
        <p>학생과 수업반 연결</p>
    </div>
    <div class="stat-card">
        <span>진도 기록</span>
        <strong>{{ progress_count }}</strong>
        <p>누적 진도 기록</p>
    </div>
    <div class="stat-card highlight">
        <span>상담 대기</span>
        <strong>{{ waiting_consultation_count }}</strong>
        <p>예약 접수/상담 예정</p>
    </div>
    <div class="stat-card warning">
        <span>오늘 미체크</span>
        <strong>{{ unchecked_today_count }}</strong>
        <p>출석 확인 필요</p>
    </div>
</section>

<section class="quick-actions">
    <a class="btn primary" href="{% url 'student_create' %}">학생 등록</a>
    <a class="btn primary" href="{% url 'classroom_create' %}">수업반 등록</a>
    <a class="btn primary" href="{% url 'enrollment_create' %}">수강 등록</a>
    <a class="btn primary" href="{% url 'progress_create' %}">진도 작성</a>
    <a class="btn primary" href="{% url 'attendance_select' %}">출석 체크</a>
    <a class="btn primary" href="{% url 'attendance_report' %}">출석 현황</a>
    <a class="btn primary" href="{% url 'consultation_create' %}">상담 예약</a>
</section>

<div class="two-column">
    <section class="card">
        <div class="section-header">
            <h2>최근 등록 학생</h2>
            <a href="{% url 'student_list' %}">전체 보기</a>
        </div>

        <div class="list-stack">
            {% for student in recent_students %}
            <a class="mini-row" href="{% url 'student_detail' student.pk %}">
                <div class="avatar small">{{ student.name|slice:":1" }}</div>
                <div>
                    <strong>{{ student.name }}</strong>
                    <p>{{ student.school|default:"학교 미입력" }} · {{ student.grade|default:"학년 미입력" }}</p>
                </div>
            </a>
            {% empty %}
            <p class="empty">아직 등록된 학생이 없습니다.</p>
            {% endfor %}
        </div>
    </section>

    <section class="card">
        <div class="section-header">
            <h2>최근 방문상담 예약</h2>
            <a href="{% url 'consultation_list' %}">전체 보기</a>
        </div>

        <div class="list-stack">
            {% for consultation in recent_consultations %}
            <a class="mini-row" href="{% url 'consultation_detail' consultation.pk %}">
                <div class="badge">상담</div>
                <div>
                    <strong>{{ consultation.student_name }} / {{ consultation.parent_name }}</strong>
                    <p>{{ consultation.preferred_date }} {{ consultation.preferred_time|time:"H:i" }} · {{ consultation.get_status_display }}</p>
                </div>
            </a>
            {% empty %}
            <p class="empty">방문상담 예약이 없습니다.</p>
            {% endfor %}
        </div>
    </section>
</div>

<section class="card">
    <div class="section-header">
        <h2>최근 진도 기록</h2>
        <a href="{% url 'progress_list' %}">전체 보기</a>
    </div>

    <div class="list-stack">
        {% for record in recent_progress %}
        <div class="mini-row">
            <div class="badge">진도</div>
            <div>
                <strong>{{ record.student.name }} - {{ record.topic }}</strong>
                <p>{{ record.classroom.name }} · {{ record.date }}</p>
            </div>
        </div>
        {% empty %}
        <p class="empty">아직 진도 기록이 없습니다.</p>
        {% endfor %}
    </div>
</section>
{% endblock %}
'''
write(TEMPLATE_DIR / "dashboard.html", dashboard_html)

# 11. student_list.html 개선
student_list_html = r'''
{% extends 'academy/base.html' %}

{% block title %}학생 관리{% endblock %}
{% block page_title %}학생 관리{% endblock %}
{% block page_description %}학교, 학년, 수업반, 정렬 기준으로 학생을 검색하고 관리합니다.{% endblock %}

{% block content %}
<section class="card">
    <div class="section-header">
        <h2>학생 목록</h2>
        <a class="btn primary" href="{% url 'student_create' %}">학생 등록</a>
    </div>

    <form class="filter-panel" method="get">
        <div class="filter-grid">
            <div class="form-group">
                <label>통합 검색</label>
                <input class="form-control" type="text" name="q" value="{{ q }}" placeholder="학생명, 학교, 학년, 연락처">
            </div>

            <div class="form-group">
                <label>학교</label>
                <select class="form-control" name="school">
                    <option value="">전체 학교</option>
                    {% for item in school_options %}
                    <option value="{{ item }}" {% if school == item %}selected{% endif %}>{{ item }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group">
                <label>학년</label>
                <select class="form-control" name="grade">
                    <option value="">전체 학년</option>
                    {% for item in grade_options %}
                    <option value="{{ item }}" {% if grade == item %}selected{% endif %}>{{ item }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group">
                <label>수업반</label>
                <select class="form-control" name="classroom">
                    <option value="">전체 수업반</option>
                    {% for classroom in classrooms %}
                    <option value="{{ classroom.id }}" {% if classroom_id == classroom.id|stringformat:"s" %}selected{% endif %}>
                        {{ classroom.name }}
                    </option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group">
                <label>정렬</label>
                <select class="form-control" name="sort">
                    <option value="name" {% if sort == "name" %}selected{% endif %}>이름순</option>
                    <option value="school" {% if sort == "school" %}selected{% endif %}>학교순</option>
                    <option value="grade" {% if sort == "grade" %}selected{% endif %}>학년순</option>
                    <option value="recent" {% if sort == "recent" %}selected{% endif %}>최근 등록순</option>
                </select>
            </div>
        </div>

        <div class="form-actions compact">
            <button class="btn primary" type="submit">검색/필터 적용</button>
            <a class="btn" href="{% url 'student_list' %}">초기화</a>
        </div>
    </form>

    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>학생명</th>
                    <th>학교</th>
                    <th>학년</th>
                    <th>수강 수업</th>
                    <th>학부모 연락처</th>
                    <th>등록일</th>
                </tr>
            </thead>
            <tbody>
                {% for student in students %}
                <tr>
                    <td>
                        <a class="table-link" href="{% url 'student_detail' student.pk %}">
                            {{ student.name }}
                        </a>
                    </td>
                    <td>{{ student.school|default:"-" }}</td>
                    <td>{{ student.grade|default:"-" }}</td>
                    <td>
                        {% for enrollment in student.enrollments.all %}
                        <span class="tag">{{ enrollment.classroom.name }}</span>
                        {% empty %}
                        <span class="muted">미배정</span>
                        {% endfor %}
                    </td>
                    <td>{{ student.parent_phone|default:"-" }}</td>
                    <td>{{ student.created_at|date:"Y-m-d" }}</td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="6" class="empty">조건에 맞는 학생이 없습니다.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</section>
{% endblock %}
'''
write(TEMPLATE_DIR / "student_list.html", student_list_html)

# 12. 방문상담 템플릿
consultation_list_html = r'''
{% extends 'academy/base.html' %}

{% block title %}방문상담 예약{% endblock %}
{% block page_title %}방문상담 예약{% endblock %}
{% block page_description %}학부모 방문상담 신청을 접수하고 상담 상태를 관리합니다.{% endblock %}

{% block content %}
<section class="stat-grid consultation-stats">
    <div class="stat-card">
        <span>예약 접수</span>
        <strong>{{ counts.waiting }}</strong>
        <p>확인 필요</p>
    </div>
    <div class="stat-card">
        <span>상담 예정</span>
        <strong>{{ counts.scheduled }}</strong>
        <p>일정 확정</p>
    </div>
    <div class="stat-card">
        <span>상담 완료</span>
        <strong>{{ counts.completed }}</strong>
        <p>처리 완료</p>
    </div>
    <div class="stat-card">
        <span>취소</span>
        <strong>{{ counts.canceled }}</strong>
        <p>취소된 예약</p>
    </div>
</section>

<section class="card">
    <div class="section-header">
        <h2>상담 예약 목록</h2>
        <a class="btn primary" href="{% url 'consultation_create' %}">방문상담 등록</a>
    </div>

    <form class="filter-panel" method="get">
        <div class="filter-grid three">
            <div class="form-group">
                <label>검색</label>
                <input class="form-control" type="text" name="q" value="{{ q }}" placeholder="학부모명, 학생명, 연락처, 학교">
            </div>
            <div class="form-group">
                <label>상담 상태</label>
                <select class="form-control" name="status">
                    <option value="">전체</option>
                    <option value="waiting" {% if status == "waiting" %}selected{% endif %}>예약 접수</option>
                    <option value="scheduled" {% if status == "scheduled" %}selected{% endif %}>상담 예정</option>
                    <option value="completed" {% if status == "completed" %}selected{% endif %}>상담 완료</option>
                    <option value="canceled" {% if status == "canceled" %}selected{% endif %}>취소</option>
                </select>
            </div>
        </div>
        <div class="form-actions compact">
            <button class="btn primary" type="submit">검색</button>
            <a class="btn" href="{% url 'consultation_list' %}">초기화</a>
        </div>
    </form>

    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>희망일</th>
                    <th>시간</th>
                    <th>학생</th>
                    <th>학부모</th>
                    <th>연락처</th>
                    <th>상태</th>
                    <th>관리</th>
                </tr>
            </thead>
            <tbody>
                {% for item in consultations %}
                <tr>
                    <td>{{ item.preferred_date }}</td>
                    <td>{{ item.preferred_time|time:"H:i" }}</td>
                    <td>
                        <a class="table-link" href="{% url 'consultation_detail' item.pk %}">
                            {{ item.student_name }}
                        </a>
                    </td>
                    <td>{{ item.parent_name }}</td>
                    <td>{{ item.phone }}</td>
                    <td><span class="status-badge {{ item.status }}">{{ item.get_status_display }}</span></td>
                    <td>
                        <a class="btn small" href="{% url 'consultation_detail' item.pk %}">상세</a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="7" class="empty">상담 예약이 없습니다.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</section>
{% endblock %}
'''
write(TEMPLATE_DIR / "consultation_list.html", consultation_list_html)

consultation_form_html = r'''
{% extends 'academy/base.html' %}

{% block title %}{{ title }}{% endblock %}
{% block page_title %}{{ title }}{% endblock %}
{% block page_description %}학부모 방문상담 신청 정보를 입력합니다.{% endblock %}

{% block content %}
<section class="card form-card">
    <form method="post">
        {% csrf_token %}

        {% if form.non_field_errors %}
        <div class="form-error">{{ form.non_field_errors }}</div>
        {% endif %}

        <div class="form-grid">
            {% for field in form %}
            <div class="form-group {% if field.name == 'purpose' or field.name == 'result_memo' %}wide{% endif %}">
                <label>{{ field.label }}</label>
                {{ field }}
                {% for error in field.errors %}
                <p class="field-error">{{ error }}</p>
                {% endfor %}
            </div>
            {% endfor %}
        </div>

        <div class="form-actions">
            <button class="btn primary big" type="submit">{{ button_text }}</button>
            <a class="btn" href="{% url 'consultation_list' %}">목록으로</a>
        </div>
    </form>
</section>
{% endblock %}
'''
write(TEMPLATE_DIR / "consultation_form.html", consultation_form_html)

consultation_detail_html = r'''
{% extends 'academy/base.html' %}

{% block title %}방문상담 상세{% endblock %}
{% block page_title %}방문상담 상세{% endblock %}
{% block page_description %}상담 신청 내용과 처리 상태를 확인합니다.{% endblock %}

{% block content %}
<section class="card">
    <div class="section-header">
        <h2>{{ consultation.student_name }} 상담 예약</h2>
        <span class="status-badge {{ consultation.status }}">{{ consultation.get_status_display }}</span>
    </div>

    <div class="info-grid">
        <div>
            <label>학생 이름</label>
            <div class="info-box">{{ consultation.student_name }}</div>
        </div>
        <div>
            <label>학부모 이름</label>
            <div class="info-box">{{ consultation.parent_name }}</div>
        </div>
        <div>
            <label>학교</label>
            <div class="info-box">{{ consultation.school|default:"-" }}</div>
        </div>
        <div>
            <label>학년</label>
            <div class="info-box">{{ consultation.grade|default:"-" }}</div>
        </div>
        <div>
            <label>연락처</label>
            <div class="info-box">{{ consultation.phone }}</div>
        </div>
        <div>
            <label>희망 상담 일시</label>
            <div class="info-box">{{ consultation.preferred_date }} {{ consultation.preferred_time|time:"H:i" }}</div>
        </div>
        <div class="wide">
            <label>상담 목적</label>
            <div class="info-box memo">{{ consultation.purpose|linebreaksbr }}</div>
        </div>
        <div class="wide">
            <label>상담 결과 메모</label>
            <div class="info-box memo">{{ consultation.result_memo|default:"작성된 상담 결과가 없습니다."|linebreaksbr }}</div>
        </div>
    </div>

    <div class="form-actions wrap">
        <a class="btn primary" href="{% url 'consultation_update' consultation.pk %}">예약 수정</a>

        <form method="post" action="{% url 'consultation_set_status' consultation.pk 'waiting' %}" class="inline-form">
            {% csrf_token %}
            <button class="btn" type="submit">예약 접수</button>
        </form>

        <form method="post" action="{% url 'consultation_set_status' consultation.pk 'scheduled' %}" class="inline-form">
            {% csrf_token %}
            <button class="btn" type="submit">상담 예정</button>
        </form>

        <form method="post" action="{% url 'consultation_set_status' consultation.pk 'completed' %}" class="inline-form">
            {% csrf_token %}
            <button class="btn primary" type="submit">상담 완료</button>
        </form>

        <form method="post" action="{% url 'consultation_set_status' consultation.pk 'canceled' %}" class="inline-form">
            {% csrf_token %}
            <button class="btn danger" type="submit">취소</button>
        </form>

        <form method="post" action="{% url 'consultation_delete' consultation.pk %}" class="inline-form js-confirm">
            {% csrf_token %}
            <button class="btn danger" type="submit">삭제</button>
        </form>

        <a class="btn" href="{% url 'consultation_list' %}">목록으로</a>
    </div>
</section>
{% endblock %}
'''
write(TEMPLATE_DIR / "consultation_detail.html", consultation_detail_html)

# 13. 출석 현황 템플릿
attendance_report_html = r'''
{% extends 'academy/base.html' %}

{% block title %}출석 현황{% endblock %}
{% block page_title %}출석 현황{% endblock %}
{% block page_description %}날짜, 수업반, 학생명, 출석 상태별로 출석 결과와 미체크 학생을 확인합니다.{% endblock %}

{% block content %}
<section class="stat-grid consultation-stats">
    <div class="stat-card">
        <span>출석</span>
        <strong>{{ counts.present }}</strong>
        <p>정상 출석</p>
    </div>
    <div class="stat-card">
        <span>결석</span>
        <strong>{{ counts.absent }}</strong>
        <p>결석 처리</p>
    </div>
    <div class="stat-card">
        <span>지각</span>
        <strong>{{ counts.late }}</strong>
        <p>지각 처리</p>
    </div>
    <div class="stat-card warning">
        <span>미체크</span>
        <strong>{{ counts.unchecked }}</strong>
        <p>출석 확인 필요</p>
    </div>
</section>

<section class="card">
    <div class="section-header">
        <h2>{{ selected_date }} 출석 현황</h2>
        <a class="btn primary" href="{% url 'attendance_select' %}">출석 체크하기</a>
    </div>

    <form class="filter-panel" method="get">
        <div class="filter-grid">
            <div class="form-group">
                <label>날짜</label>
                <input class="form-control" type="date" name="date" value="{{ selected_date|date:'Y-m-d' }}">
            </div>

            <div class="form-group">
                <label>수업반</label>
                <select class="form-control" name="classroom">
                    <option value="">전체 수업반</option>
                    {% for classroom in classrooms %}
                    <option value="{{ classroom.id }}" {% if classroom_id == classroom.id|stringformat:"s" %}selected{% endif %}>
                        {{ classroom.name }}
                    </option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group">
                <label>학생 검색</label>
                <input class="form-control" type="text" name="q" value="{{ q }}" placeholder="학생명, 학교, 학년">
            </div>

            <div class="form-group">
                <label>상태</label>
                <select class="form-control" name="status">
                    {% for value, label in status_options %}
                    <option value="{{ value }}" {% if status_filter == value %}selected{% endif %}>{{ label }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>

        <div class="form-actions compact">
            <button class="btn primary" type="submit">조회</button>
            <a class="btn" href="{% url 'attendance_report' %}">초기화</a>
        </div>
    </form>

    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>날짜</th>
                    <th>수업반</th>
                    <th>학생명</th>
                    <th>학교</th>
                    <th>학년</th>
                    <th>상태</th>
                    <th>비고</th>
                </tr>
            </thead>
            <tbody>
                {% for row in rows %}
                <tr>
                    <td>{{ row.date }}</td>
                    <td>{{ row.classroom.name }}</td>
                    <td>
                        <a class="table-link" href="{% url 'student_detail' row.student.pk %}">
                            {{ row.student.name }}
                        </a>
                    </td>
                    <td>{{ row.student.school|default:"-" }}</td>
                    <td>{{ row.student.grade|default:"-" }}</td>
                    <td><span class="status-badge {{ row.status }}">{{ row.status_display }}</span></td>
                    <td>{{ row.note|default:"-" }}</td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="7" class="empty">조건에 맞는 출석 현황이 없습니다.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</section>
{% endblock %}
'''
write(TEMPLATE_DIR / "attendance_report.html", attendance_report_html)

# 14. CSS 추가
css_path = STATIC_DIR / "styles.css"
css_extra = r'''
/* ===== Upgrade: consultation, report, advanced filter ===== */
.wide-stats {
    grid-template-columns: repeat(6, 1fr);
}

.consultation-stats {
    grid-template-columns: repeat(4, 1fr);
}

.stat-card.highlight strong {
    color: #7c3aed;
}

.stat-card.warning strong {
    color: #f97316;
}

.filter-panel {
    background: #f8fafc;
    border: 1px solid #dbe5f3;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 20px;
}

.filter-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
}

.filter-grid.three {
    grid-template-columns: 2fr 1fr 1fr;
}

.form-actions.compact {
    margin-top: 14px;
}

.form-actions.wrap {
    flex-wrap: wrap;
}

.tag {
    display: inline-block;
    background: #e0f2fe;
    color: #0369a1;
    border-radius: 999px;
    padding: 5px 9px;
    margin: 2px;
    font-size: 12px;
    font-weight: 800;
}

.muted {
    color: #94a3b8;
    font-weight: 700;
}

.status-badge.waiting {
    background: #dbeafe;
    color: #1d4ed8;
}

.status-badge.scheduled {
    background: #ede9fe;
    color: #6d28d9;
}

.status-badge.completed {
    background: #dcfce7;
    color: #15803d;
}

.status-badge.canceled {
    background: #fee2e2;
    color: #b91c1c;
}

.status-badge.unchecked {
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #cbd5e1;
}

@media (max-width: 1280px) {
    .wide-stats {
        grid-template-columns: repeat(3, 1fr);
    }

    .filter-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 780px) {
    .wide-stats,
    .consultation-stats,
    .filter-grid,
    .filter-grid.three {
        grid-template-columns: 1fr;
    }
}
'''
if "Upgrade: consultation" not in read(css_path):
    write(css_path, read(css_path).rstrip() + "\n\n" + css_extra.strip() + "\n")

print("필수 보완 기능 패치가 완료되었습니다.")
print("추가 기능: 방문상담 예약, 상담 상태 변경, 출석 현황/미체크, 학생 필터 강화, 대시보드 개선")
