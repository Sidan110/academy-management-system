
from django.shortcuts import redirect, render


PUBLIC_PREFIXES = (
    "/login/",
    "/apply/",
    "/checkin/",
    "/static/",
    "/admin/",
)

OWNER_ONLY_PREFIXES = (
    "/consultations/",
    "/enrollments/",
    "/notifications/",
    "/payments/",
)

OWNER_ONLY_PATTERNS = (
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

    if path in OWNER_ONLY_PATTERNS:
        return True

    if path.startswith("/students/") and (path.endswith("/edit/") or path.endswith("/delete/")):
        return True

    if path.startswith("/classes/") and (path.endswith("/edit/") or path.endswith("/delete/")):
        return True

    if path.startswith("/classrooms/") and (path.endswith("/edit/") or path.endswith("/delete/")):
        return True

    return False


class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if path == "/":
            if not request.user.is_authenticated:
                return redirect("login")
            return self.get_response(request)

        if path.startswith(PUBLIC_PREFIXES):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect("login")

        if is_owner_only_path(path) and not is_owner(request.user):
            return render(request, "academy/forbidden.html", status=403)

        return self.get_response(request)
