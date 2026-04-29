# Generated manually for EduManager notification feature

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0002_consultationreservation'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('sms', '문자'), ('alimtalk', '알림톡')], default='sms', max_length=20, verbose_name='알림 유형')),
                ('category', models.CharField(choices=[('consultation_received', '상담 예약 접수'), ('consultation_scheduled', '상담 일정 확정'), ('consultation_completed', '상담 완료'), ('consultation_canceled', '상담 취소'), ('attendance_notice', '출석 안내')], default='consultation_received', max_length=40, verbose_name='알림 분류')),
                ('recipient_name', models.CharField(max_length=50, verbose_name='수신자')),
                ('phone', models.CharField(max_length=30, verbose_name='연락처')),
                ('message', models.TextField(verbose_name='발송 내용')),
                ('status', models.CharField(choices=[('waiting', '발송 대기'), ('sent', '발송 완료'), ('failed', '발송 실패')], default='waiting', max_length=20, verbose_name='발송 상태')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('sent_at', models.DateTimeField(blank=True, null=True, verbose_name='발송 처리일')),
                ('consultation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='academy.consultationreservation', verbose_name='관련 상담 예약')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
