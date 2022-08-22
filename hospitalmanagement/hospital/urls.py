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

    #admin dashboard
    path('admin-dashboard', views.admin_dashboard_view, name='admin-dashboard'),


]
