# Generated manually for EduManager

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClassRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='수업명')),
                ('teacher', models.CharField(max_length=50, verbose_name='담당 선생님')),
                ('day_of_week', models.CharField(max_length=50, verbose_name='수업 요일')),
                ('start_time', models.TimeField(verbose_name='시작 시간')),
                ('end_time', models.TimeField(verbose_name='종료 시간')),
                ('room', models.CharField(blank=True, max_length=50, verbose_name='강의실')),
                ('description', models.TextField(blank=True, verbose_name='수업 설명')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='학생명')),
                ('school', models.CharField(blank=True, max_length=100, verbose_name='학교')),
                ('grade', models.CharField(blank=True, max_length=20, verbose_name='학년')),
                ('phone', models.CharField(blank=True, max_length=30, verbose_name='학생 연락처')),
                ('parent_phone', models.CharField(blank=True, max_length=30, verbose_name='학부모 연락처')),
                ('address', models.CharField(blank=True, max_length=255, verbose_name='주소')),
                ('memo', models.TextField(blank=True, verbose_name='메모')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='등록일')),
            ],
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolled_at', models.DateField(auto_now_add=True, verbose_name='수강 등록일')),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='academy.classroom', verbose_name='수업반')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='academy.student', verbose_name='학생')),
            ],
            options={
                'unique_together': {('student', 'classroom')},
            },
        ),
        migrations.CreateModel(
            name='ProgressRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.localdate, verbose_name='수업 날짜')),
                ('topic', models.CharField(max_length=200, verbose_name='수업 진도')),
                ('homework', models.CharField(blank=True, max_length=200, verbose_name='숙제')),
                ('understanding', models.CharField(choices=[('good', '좋음'), ('normal', '보통'), ('need_help', '추가 지도 필요')], default='normal', max_length=20, verbose_name='이해도')),
                ('memo', models.TextField(blank=True, verbose_name='메모')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='작성일')),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress_records', to='academy.classroom', verbose_name='수업반')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress_records', to='academy.student', verbose_name='학생')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.localdate, verbose_name='출석 날짜')),
                ('status', models.CharField(choices=[('present', '출석'), ('absent', '결석'), ('late', '지각'), ('early', '조퇴'), ('makeup', '보강')], default='present', max_length=20, verbose_name='출석 상태')),
                ('note', models.CharField(blank=True, max_length=200, verbose_name='비고')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='academy.classroom', verbose_name='수업반')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='academy.student', verbose_name='학생')),
            ],
            options={
                'unique_together': {('student', 'classroom', 'date')},
            },
        ),
    ]
