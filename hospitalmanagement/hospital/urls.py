from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('', views.home_view, name='home'),

    # add about us and contact us page paths
    # path('aboutus', views.aboutus_view),
    # path('contactus', views.contactus_view),

    # add doctor, patient, admin click pages url path

    path('adminclick', views.adminclick_view, name='adminclick'),
    path('doctorclick', views.doctorclick_view, name='doctorclick'),
    path('patientclick', views.patientclick_view, name='patientclick'),

    # add admin, patient, doctor registration url
    path('adminsignup', views.admin_signup_view, name='adminsignup'),
    path('doctorsignup', views.doctor_signup_view, name='doctorsignup'),
    path('patientsignup', views.patient_signup_view, name='patientsignup'),

    # admin doctor and patient login
    path('adminlogin', LoginView.as_view(
        template_name='hospital/adminlogin.html')),
    path('doctorlogin', LoginView.as_view(
        template_name='hospital/doctorlogin.html')),
    path('patientlogin', LoginView.as_view(
        template_name='hospital/patientlogin.html')),

    # after login and logout
    path('afterlogin', views.afterlogin_view, name='afterlogin'),
    path('logout', LogoutView.as_view(
        template_name='hospital/index.html'), name='logout'),

    # admin dashboard
    path('admin-dashboard', views.admin_dashboard_view, name='admin-dashboard'),

    # # Doctor related admin work
    path('admin-doctor', views.admin_doctor_view, name='admin-doctor'),
    path('admin-view-doctor', views.admin_view_doctor_view,
         name='admin-view-doctor'),
    path('delete-doctor-from-hospital/<int:pk>',
         views.delete_doctor_from_hospital_view, name='delete-doctor-from-hospital'),
    path('update-doctor/<int:pk>', views.update_doctor_view, name='update-doctor'),
    path('admin-add-doctor', views.admin_add_doctor_view, name='admin-add-doctor'),
    path('admin-approve-doctor', views.admin_approve_doctor_view,
         name='admin-approve-doctor'),
    path('approve-doctor/<int:pk>',
         views.approve_doctor_view, name='approve-doctor'),
    path('reject-doctor/<int:pk>', views.reject_doctor_view, name='reject-doctor'),
    path('admin-view-doctor-specialisation', views.admin_view_doctor_specialisation_view,
         name='admin-view-doctor-specialisation'),

    path('admin-patient', views.admin_patient_view, name='admin-patient'),
    path('admin-view-patient', views.admin_view_patient_view,
         name='admin-view-patient'),
    path('delete-patient-from-hospital/<int:pk>',
         views.delete_patient_from_hospital_view, name='delete-patient-from-hospital'),
    path('update-patient/<int:pk>',
         views.update_patient_view, name='update-patient'),
    path('admin-add-patient', views.admin_add_patient_view,
         name='admin-add-patient'),
    path('admin-approve-patient', views.admin_approve_patient_view,
         name='admin-approve-patient'),
    path('approve-patient/<int:pk>',
         views.approve_patient_view, name='approve-patient'),
    path('reject-patient/<int:pk>',
         views.reject_patient_view, name='reject-patient'),
    path('admin-discharge-patient', views.admin_discharge_patient_view,
         name='admin-discharge-patient'),
    path('discharge-patient/<int:pk>',
         views.discharge_patient_view, name='discharge-patient'),
    path('download-pdf/<int:pk>', views.download_pdf_view, name='download-pdf'),
    path('admin-appointment', views.admin_appointment_view,
         name='admin-appointment'),
    path('admin-view-appointment', views.admin_view_appointment_view,
         name='admin-view-appointment'),
    path('admin-add-appointment', views.admin_add_appointment_view,
         name='admin-add-appointment'),
    path('admin-approve-appointment', views.admin_approve_appointment_view,
         name='admin-approve-appointment'),
    path('approve-appointment/<int:pk>',
         views.approve_appointment_view, name='approve-appointment'),
    path('reject-appointment/<int:pk>',
         views.reject_appointment_view, name='reject-appointment'),


]

# ---------FOR DOCTOR RELATED URLS-------------------------------------
urlpatterns += [
    path('doctor-dashboard', views.doctor_dashboard_view, name='doctor-dashboard'),

]


# ---------FOR PATIENT RELATED URLS-------------------------------------
urlpatterns += [

    path('patient-dashboard', views.patient_dashboard_view,
         name='patient-dashboard'),


]
