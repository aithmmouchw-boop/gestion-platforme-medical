from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import AppointmentForm, ConsultationForm, ContactForm, PrescriptionForm, RegisterForm
from .models import Appointment, Consultation, DoctorProfile, PatientProfile, UserProfile


def landing_page(request):
    return render(request, "landing.html")


def contact_page(request):
    form = ContactForm(request.POST or None)
    success = False
    if request.method == "POST" and form.is_valid():
        success = True
        form = ContactForm()
    return render(request, "contact.html", {"form": form, "success": success})


def blog_article_protection(request):
    return render(request, "blog_article_protection.html")


def info_page(request, slug):
    pages = {
        "fonctionnalites": {
            "title": "Fonctionnalites",
            "description": "Gestion patients, agenda intelligent, dossiers medicaux, IA de risque et tableaux de bord role-based.",
        },
        "benefices": {
            "title": "Benefices",
            "description": "Gain de temps, meilleure organisation clinique, suivi patient optimise et securite des donnees.",
        },
        "tarifs": {
            "title": "Tarifs",
            "description": "Plans flexibles selon la taille du cabinet avec periode d'essai et support prioritaire.",
        },
        "temoignages": {
            "title": "Temoignages",
            "description": "Retours de medecins et equipes administratives qui utilisent MediFlow au quotidien.",
        },
        "blog": {
            "title": "Blog",
            "description": "Conseils pratiques, actualites de la e-sante et bonnes pratiques de gestion medicale.",
        },
        "contact": {
            "title": "Contact",
            "description": "Parlez a notre equipe pour une demo, une integration ou un accompagnement personnalise.",
        },
        "dashboard": {
            "title": "Dashboard Medecin",
            "description": "Vue globale de l'activite quotidienne: rendez-vous, patients, revenus et priorites cliniques.",
        },
        "agenda": {
            "title": "Agenda Medical",
            "description": "Planification intelligente, disponibilites en temps reel et gestion fluide du parcours patient.",
        },
        "fiche-patient": {
            "title": "Fiche Patient",
            "description": "Acces rapide a l'historique, aux consultations, prescriptions et indicateurs de risque.",
        },
        "brochure": {
            "title": "Brochure MediFlow",
            "description": "Telechargez la brochure complete des modules, plans et avantages de la plateforme.",
        },
    }
    page = pages.get(slug)
    if not page:
        return redirect("landing-page")
    return render(request, "site_page.html", page)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard-router")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        if user.profile.role == UserProfile.Role.DOCTOR:
            DoctorProfile.objects.get_or_create(user=user)
        if user.profile.role == UserProfile.Role.PATIENT:
            PatientProfile.objects.get_or_create(user=user)
        login(request, user)
        return redirect("dashboard-router")
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard-router")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("dashboard-router")
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("landing-page")


@login_required
def dashboard_router(request):
    role = request.user.profile.role
    if role == UserProfile.Role.ADMIN:
        return redirect("dashboard-admin")
    if role == UserProfile.Role.SECRETARY:
        return redirect("dashboard-secretary")
    if role == UserProfile.Role.DOCTOR:
        return redirect("dashboard-doctor")
    return redirect("dashboard-patient")


def _require_role(request, allowed_roles):
    if request.user.profile.role not in allowed_roles:
        return HttpResponseForbidden("Acces non autorise pour ce role.")
    return None


def _calculate_risk(patient):
    consultations = Consultation.objects.filter(appointment__patient=patient)
    consultation_count = consultations.count()
    severity_total = sum(item.severity for item in consultations)
    severity_average = (severity_total / consultation_count) if consultation_count else 0
    score = min(100, int(consultation_count * 8 + severity_average * 20))
    if score >= 70:
        return {"score": score, "status": "Eleve", "color": "red", "followup_days": 7}
    if score >= 35:
        return {"score": score, "status": "Moyen", "color": "orange", "followup_days": 30}
    return {"score": score, "status": "Faible", "color": "green", "followup_days": 90}


@login_required
def admin_dashboard(request):
    denied = _require_role(request, [UserProfile.Role.ADMIN])
    if denied:
        return denied
    context = {
        "users_count": UserProfile.objects.count(),
        "appointments_count": Appointment.objects.count(),
        "doctors_count": DoctorProfile.objects.count(),
    }
    return render(request, "dashboards/admin.html", context)


@login_required
def secretary_dashboard(request):
    denied = _require_role(request, [UserProfile.Role.SECRETARY])
    if denied:
        return denied
    upcoming = Appointment.objects.exclude(status=Appointment.Status.CANCELED)
    context = {
        "today_count": upcoming.filter(appointment_date=timezone.localdate()).count(),
        "urgent_count": upcoming.filter(priority=Appointment.Priority.URGENT).count(),
        "appointments": upcoming.select_related("doctor__user", "patient__user")[:8],
    }
    return render(request, "dashboards/secretary.html", context)


@login_required
def doctor_dashboard(request):
    denied = _require_role(request, [UserProfile.Role.DOCTOR])
    if denied:
        return denied
    doctor, _ = DoctorProfile.objects.get_or_create(user=request.user)
    appointments = doctor.appointments.exclude(status=Appointment.Status.CANCELED)
    context = {
        "today_count": appointments.filter(appointment_date=timezone.localdate()).count(),
        "upcoming_count": appointments.count(),
        "consultation_count": Consultation.objects.filter(appointment__doctor=doctor).count(),
    }
    return render(request, "dashboards/doctor.html", context)


@login_required
def patient_dashboard(request):
    denied = _require_role(request, [UserProfile.Role.PATIENT])
    if denied:
        return denied
    patient, _ = PatientProfile.objects.get_or_create(user=request.user)
    appointments = patient.appointments.select_related("doctor__user")
    consultations = Consultation.objects.filter(appointment__patient=patient).select_related(
        "appointment__doctor__user"
    )[:8]
    context = {
        "appointments": appointments[:8],
        "consultations": consultations,
        "risk": _calculate_risk(patient),
    }
    return render(request, "dashboards/patient.html", context)


@login_required
def appointment_create(request):
    denied = _require_role(request, [UserProfile.Role.PATIENT, UserProfile.Role.SECRETARY])
    if denied:
        return denied

    if request.user.profile.role == UserProfile.Role.PATIENT:
        patient_profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    else:
        patient_profile = None

    form = AppointmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        appointment = form.save(commit=False)
        if patient_profile:
            appointment.patient = patient_profile
        else:
            patient_id = request.POST.get("patient_id")
            if patient_id:
                appointment.patient = PatientProfile.objects.filter(pk=patient_id).first()
        if not appointment.patient:
            form.add_error(None, "Selectionnez un patient valide.")
        else:
            try:
                appointment.full_clean()
                appointment.save()
                return redirect("appointments-list")
            except ValidationError as exc:
                form.add_error(None, exc.message)

    patients = PatientProfile.objects.select_related("user").all() if not patient_profile else None
    return render(request, "appointments/create.html", {"form": form, "patients": patients})


@login_required
def appointments_list(request):
    denied = _require_role(
        request,
        [UserProfile.Role.PATIENT, UserProfile.Role.SECRETARY, UserProfile.Role.DOCTOR, UserProfile.Role.ADMIN],
    )
    if denied:
        return denied

    role = request.user.profile.role
    appointments = Appointment.objects.select_related("doctor__user", "patient__user")
    if role == UserProfile.Role.PATIENT:
        patient, _ = PatientProfile.objects.get_or_create(user=request.user)
        appointments = appointments.filter(patient=patient)
    elif role == UserProfile.Role.DOCTOR:
        doctor, _ = DoctorProfile.objects.get_or_create(user=request.user)
        appointments = appointments.filter(doctor=doctor)

    return render(request, "appointments/list.html", {"appointments": appointments[:30]})


@login_required
def consultation_create(request):
    denied = _require_role(request, [UserProfile.Role.DOCTOR])
    if denied:
        return denied
    doctor, _ = DoctorProfile.objects.get_or_create(user=request.user)

    form = ConsultationForm(request.POST or None, doctor=doctor)
    prescription_form = PrescriptionForm(request.POST or None, prefix="rx")
    if request.method == "POST" and form.is_valid() and prescription_form.is_valid():
        consultation = form.save()
        prescription = prescription_form.save(commit=False)
        prescription.consultation = consultation
        prescription.save()
        return redirect("appointments-list")

    return render(
        request,
        "consultations/create.html",
        {"form": form, "prescription_form": prescription_form},
    )


@login_required
def patient_timeline(request):
    denied = _require_role(request, [UserProfile.Role.PATIENT])
    if denied:
        return denied
    patient, _ = PatientProfile.objects.get_or_create(user=request.user)
    consultations = Consultation.objects.filter(appointment__patient=patient).select_related(
        "appointment__doctor__user"
    )
    return render(
        request,
        "consultations/timeline.html",
        {"consultations": consultations, "risk": _calculate_risk(patient)},
    )
