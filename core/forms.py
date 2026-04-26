from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Appointment, Consultation, DoctorProfile, Prescription, UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=UserProfile.Role.choices, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "role", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            user.profile.role = self.cleaned_data["role"]
            user.profile.save()
        return user


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ("doctor", "appointment_date", "appointment_time", "reason", "priority")
        widgets = {
            "appointment_date": forms.DateInput(attrs={"type": "date"}),
            "appointment_time": forms.TimeInput(attrs={"type": "time"}),
        }

    doctor = forms.ModelChoiceField(queryset=DoctorProfile.objects.all(), empty_label="Choisir un medecin")


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ("appointment", "diagnosis", "severity", "notes")
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    appointment = forms.ModelChoiceField(queryset=Appointment.objects.none())

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop("doctor", None)
        super().__init__(*args, **kwargs)
        if doctor:
            self.fields["appointment"].queryset = (
                Appointment.objects.filter(doctor=doctor)
                .exclude(consultation__isnull=False)
                .exclude(status=Appointment.Status.CANCELED)
            )


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ("medication_name", "dosage", "instructions")
        widgets = {
            "instructions": forms.Textarea(attrs={"rows": 3}),
        }


class ContactForm(forms.Form):
    full_name = forms.CharField(label="Nom complet", max_length=120)
    email = forms.EmailField(label="Email")
    phone = forms.CharField(label="Telephone", max_length=30, required=False)
    message = forms.CharField(label="Message", widget=forms.Textarea(attrs={"rows": 5}))
