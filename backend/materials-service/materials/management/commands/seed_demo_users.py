from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create demo users (teacher and student) for local testing"

    def handle(self, *args, **options):
        # Create teacher
        teacher_username = 'teacher1'
        teacher_password = 'teacher123'
        student_username = 'student1'
        student_password = 'student123'

        teacher, created_t = User.objects.get_or_create(username=teacher_username)
        if created_t:
            teacher.set_password(teacher_password)
            teacher.is_staff = True  # grant admin UI access if needed
            teacher.save()
            self.stdout.write(self.style.SUCCESS(f"Created teacher user: {teacher_username}/{teacher_password}"))
        else:
            self.stdout.write(self.style.WARNING(f"Teacher user exists: {teacher_username}"))

        student, created_s = User.objects.get_or_create(username=student_username)
        if created_s:
            student.set_password(student_password)
            student.save()
            self.stdout.write(self.style.SUCCESS(f"Created student user: {student_username}/{student_password}"))
        else:
            self.stdout.write(self.style.WARNING(f"Student user exists: {student_username}"))

        # Note: Our materials service doesn't have a custom role field.
        # Permission checks fallback to is_staff/is_superuser (already handled in permissions.py and views.py).
