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
    path('adminsignup', views.admin_signup_view,name='adminsignup'),
    path('doctorsignup', views.doctor_signup_view, name='doctorsignup'),
    path('patientsignup', views.patient_signup_view,name='patientsignup'),

]
