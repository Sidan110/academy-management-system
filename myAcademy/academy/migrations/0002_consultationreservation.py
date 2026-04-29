# Generated manually for EduManager consultation feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsultationReservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_name', models.CharField(max_length=50, verbose_name='학부모 이름')),
                ('student_name', models.CharField(max_length=50, verbose_name='학생 이름')),
                ('school', models.CharField(blank=True, max_length=100, verbose_name='학교')),
                ('grade', models.CharField(blank=True, max_length=20, verbose_name='학년')),
                ('phone', models.CharField(max_length=30, verbose_name='연락처')),
                ('preferred_date', models.DateField(verbose_name='희망 상담 날짜')),
                ('preferred_time', models.TimeField(verbose_name='희망 상담 시간')),
                ('purpose', models.TextField(verbose_name='상담 목적')),
                ('status', models.CharField(choices=[('waiting', '예약 접수'), ('scheduled', '상담 예정'), ('completed', '상담 완료'), ('canceled', '취소')], default='waiting', max_length=20, verbose_name='상담 상태')),
                ('result_memo', models.TextField(blank=True, verbose_name='상담 결과 메모')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='신청일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
            ],
            options={
                'ordering': ['preferred_date', 'preferred_time', '-created_at'],
            },
        ),
    ]
