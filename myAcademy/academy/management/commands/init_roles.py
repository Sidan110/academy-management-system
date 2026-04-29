
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = "Create default owner and teacher accounts for EduManager"

    def handle(self, *args, **options):
        owner_group, _ = Group.objects.get_or_create(name="Owner")
        teacher_group, _ = Group.objects.get_or_create(name="Teacher")

        owner, _ = User.objects.get_or_create(username="owner")
        owner.set_password("owner1234")
        owner.first_name = "원장"
        owner.is_staff = True
        owner.is_superuser = True
        owner.save()
        owner.groups.set([owner_group])

        teacher, _ = User.objects.get_or_create(username="teacher")
        teacher.set_password("teacher1234")
        teacher.first_name = "교사"
        teacher.is_staff = False
        teacher.is_superuser = False
        teacher.save()
        teacher.groups.set([teacher_group])

        self.stdout.write(self.style.SUCCESS("Default accounts created or updated."))
        self.stdout.write("Owner  : owner / owner1234")
        self.stdout.write("Teacher: teacher / teacher1234")
