from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing_page, name='landing-page'),
    path('contact/', views.contact_page, name='contact-page'),
    path('blog/protection-donnees/', views.blog_article_protection, name='blog-article-protection'),
    path('page/fonctionnalites/', views.info_page, {"slug": "fonctionnalites"}, name='page-fonctionnalites'),
    path('page/benefices/', views.info_page, {"slug": "benefices"}, name='page-benefices'),
    path('page/tarifs/', views.info_page, {"slug": "tarifs"}, name='page-tarifs'),
    path('page/temoignages/', views.info_page, {"slug": "temoignages"}, name='page-temoignages'),
    path('page/blog/', views.info_page, {"slug": "blog"}, name='page-blog'),
    path('page/contact/', views.info_page, {"slug": "contact"}, name='page-contact'),
    path('page/dashboard/', views.info_page, {"slug": "dashboard"}, name='page-dashboard'),
    path('page/agenda/', views.info_page, {"slug": "agenda"}, name='page-agenda'),
    path('page/fiche-patient/', views.info_page, {"slug": "fiche-patient"}, name='page-fiche-patient'),
    path('page/brochure/', views.info_page, {"slug": "brochure"}, name='page-brochure'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_router, name='dashboard-router'),
    path('dashboard/admin/', views.admin_dashboard, name='dashboard-admin'),
    path('dashboard/secretary/', views.secretary_dashboard, name='dashboard-secretary'),
    path('dashboard/doctor/', views.doctor_dashboard, name='dashboard-doctor'),
    path('dashboard/patient/', views.patient_dashboard, name='dashboard-patient'),
    path('appointments/new/', views.appointment_create, name='appointment-create'),
    path('appointments/', views.appointments_list, name='appointments-list'),
    path('consultations/new/', views.consultation_create, name='consultation-create'),
    path('timeline/', views.patient_timeline, name='patient-timeline'),
]
