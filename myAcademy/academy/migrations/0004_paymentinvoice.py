# Payment invoice migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0003_notificationlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationlog',
            name='category',
            field=models.CharField(
                choices=[
                    ('consultation_received', '상담 예약 접수'),
                    ('consultation_scheduled', '상담 일정 확정'),
                    ('consultation_completed', '상담 완료'),
                    ('consultation_canceled', '상담 취소'),
                    ('attendance_notice', '출석 안내'),
                    ('payment_invoice', '수강료 청구 안내'),
                    ('payment_overdue', '미납 안내'),
                ],
                default='consultation_received',
                max_length=40,
                verbose_name='알림 분류'
            ),
        ),
        migrations.CreateModel(
            name='PaymentInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_month', models.CharField(help_text='예: 2026-04', max_length=7, verbose_name='청구월')),
                ('tuition_fee', models.DecimalField(decimal_places=0, default=0, max_digits=10, verbose_name='수업료')),
                ('book_fee', models.DecimalField(decimal_places=0, default=0, max_digits=10, verbose_name='교재비')),
                ('shuttle_fee', models.DecimalField(decimal_places=0, default=0, max_digits=10, verbose_name='차량비')),
                ('discount_amount', models.DecimalField(decimal_places=0, default=0, max_digits=10, verbose_name='할인 금액')),
                ('paid_amount', models.DecimalField(decimal_places=0, default=0, max_digits=10, verbose_name='납부 금액')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='납부 예정일')),
                ('paid_date', models.DateField(blank=True, null=True, verbose_name='납부일')),
                ('status', models.CharField(choices=[('unpaid', '미납'), ('partial', '부분납'), ('paid', '완납'), ('overdue', '연체')], default='unpaid', max_length=20, verbose_name='납부 상태')),
                ('memo', models.TextField(blank=True, verbose_name='메모')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_invoices', to='academy.student', verbose_name='학생')),
            ],
            options={
                'ordering': ['-billing_month', 'student__name'],
            },
        ),
    ]
