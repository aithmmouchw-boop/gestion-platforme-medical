from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrateur"
        SECRETARY = "secretary", "Secretaire"
        DOCTOR = "doctor", "Medecin"
        PATIENT = "patient", "Patient"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    specialty = models.CharField(max_length=120, default="Generaliste")
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    medical_notes = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Appointment(models.Model):
    class Priority(models.TextChoices):
        NORMAL = "normal", "Normal"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        CONFIRMED = "confirmed", "Confirme"
        DONE = "done", "Termine"
        CANCELED = "canceled", "Annule"

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="appointments")
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="appointments")
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.CharField(max_length=255)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time"]

    def clean(self):
        conflict_exists = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date=self.appointment_date,
            appointment_time=self.appointment_time,
        ).exclude(pk=self.pk).exclude(status=Appointment.Status.CANCELED).exists()
        if conflict_exists:
            raise ValidationError("Ce creneau est deja reserve pour ce medecin.")

    def __str__(self):
        return f"{self.patient} - {self.doctor} ({self.appointment_date} {self.appointment_time})"


class Consultation(models.Model):
    class Severity(models.IntegerChoices):
        LOW = 1, "Faible"
        MEDIUM = 2, "Moderee"
        HIGH = 3, "Critique"

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="consultation")
    diagnosis = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    severity = models.IntegerField(choices=Severity.choices, default=Severity.LOW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def timeline_color(self):
        if self.severity == Consultation.Severity.HIGH:
            return "red"
        if self.severity == Consultation.Severity.MEDIUM:
            return "orange"
        return "green"

    def __str__(self):
        return f"Consultation {self.appointment.patient} - {self.diagnosis}"


class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="prescriptions")
    medication_name = models.CharField(max_length=180)
    dosage = models.CharField(max_length=120)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.medication_name} ({self.dosage})"
