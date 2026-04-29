from django import forms
from .models import Student, ClassRoom, Enrollment, ProgressRecord, ConsultationReservation

class BaseStyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            old_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (old_class + ' form-control').strip()


class StudentForm(BaseStyledForm):
    class Meta:
        model = Student
        fields = [
            'name',
            'school',
            'grade',
            'phone',
            'parent_phone',
            'address',
            'memo',
        ]
        widgets = {
            'memo': forms.Textarea(attrs={'rows': 4}),
        }


class ClassRoomForm(BaseStyledForm):
    class Meta:
        model = ClassRoom
        fields = [
            'name',
            'teacher',
            'day_of_week',
            'start_time',
            'end_time',
            'room',
            'description',
        ]
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class EnrollmentForm(BaseStyledForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'classroom']

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        classroom = cleaned_data.get('classroom')

        if student and classroom:
            exists = Enrollment.objects.filter(
                student=student,
                classroom=classroom
            ).exists()

            if exists:
                raise forms.ValidationError("이미 해당 학생은 이 수업반에 등록되어 있습니다.")

        return cleaned_data


class ProgressRecordForm(BaseStyledForm):
    class Meta:
        model = ProgressRecord
        fields = [
            'student',
            'classroom',
            'date',
            'topic',
            'homework',
            'understanding',
            'memo',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'memo': forms.Textarea(attrs={'rows': 4}),
        }

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
