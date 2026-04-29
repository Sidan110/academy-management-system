from django.shortcuts import redirect, render


PUBLIC_PREFIXES = (
    "/login/",
    "/apply/",
    "/checkin/",
    "/static/",
    "/admin/",
    "/favicon.ico",
)

OWNER_ONLY_PREFIXES = (
    "/consultations/",
    "/enrollments/",
    "/notifications/",
    "/payments/",
)

OWNER_ONLY_EXACT_PATHS = (
    "/students/new/",
    "/classes/new/",
    "/classrooms/new/",
)


def is_owner(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name="Owner").exists()


def is_teacher(user):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name="Teacher").exists()


def is_owner_only_path(path):
    if path.startswith(OWNER_ONLY_PREFIXES):
        return True

    if path in OWNER_ONLY_EXACT_PATHS:
        return True

    if path.startswith("/students/") and (
        path.endswith("/edit/") or path.endswith("/delete/")
    ):
        return True

    if path.startswith("/classes/") and (
        path.endswith("/edit/") or path.endswith("/delete/")
    ):
        return True

    if path.startswith("/classrooms/") and (
        path.endswith("/edit/") or path.endswith("/delete/")
    ):
        return True

    return False


class RoleAccessMiddleware:
    """
    원장/교사 권한을 나누기 위한 간단한 접근 제어 미들웨어.

    - 비회원: 로그인, 학부모 상담 신청, 학생 직접 출석 체크만 접근 가능
    - 교사: 학생 조회, 수업반 조회, 진도, 출석 중심 접근 가능
    - 원장: 전체 기능 접근 가능
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if path.startswith(PUBLIC_PREFIXES):
            return self.get_response(request)

        if path == "/":
            if not request.user.is_authenticated:
                return redirect("login")
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect("login")

        if is_owner_only_path(path) and not is_owner(request.user):
            return render(request, "academy/forbidden.html", status=403)

        return self.get_response(request)
