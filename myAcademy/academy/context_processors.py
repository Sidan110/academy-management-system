def role_flags(request):
    user = getattr(request, "user", None)

    is_owner = False
    is_teacher = False
    role_label = "비회원"

    if user and user.is_authenticated:
        is_owner = user.is_superuser or user.groups.filter(name="Owner").exists()
        is_teacher = user.groups.filter(name="Teacher").exists()

        if is_owner:
            role_label = "원장"
        elif is_teacher:
            role_label = "교사"
        else:
            role_label = "직원"

    return {
        "is_owner": is_owner,
        "is_teacher": is_teacher,
        "role_label": role_label,
    }
