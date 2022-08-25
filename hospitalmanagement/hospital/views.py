from multiprocessing import context
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
from . import forms, models
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta, date
from django.conf import settings
# Create your views here.

# View for home page


def home_view(request):
    # if request.user.is_authenticated:
    #     return HttpResponseRedirect('afterlogin')
    return render(request, 'hospital/index.html')

# for checking user is doctor , patient or admin(by submit button)


def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()


def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()


def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


# for showing signup/login button for admin(by submit)
def adminclick_view(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin-dashboard')
    context = {'error': 'Account Not Found, Please Register'}
    return render(request, 'hospital/adminclick.html', context = context)


# for showing signup/login button for doctor(by submit)
def doctorclick_view(request):
    if is_doctor(request.user):
        accountapproval = models.Doctor.objects.all().filter(
            user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request, 'hospital/doctor_wait_for_approval.html')
    context = {'error': 'Account Not Found, Please Register'}
    return render(request, 'hospital/doctorclick.html', context=context)


# for showing signup/login button for patient(by submit)
def patientclick_view(request):
    if is_patient(request.user):
            accountapproval = models.Patient.objects.all().filter(
                user_id=request.user.id, status=True)
            if accountapproval:
                return redirect('patient-dashboard')
            else:
                return render(request, 'hospital/patient_wait_for_approval.html')
    return render(request, 'hospital/patientclick.html')

# Now work for signup views


def admin_signup_view(request):  # sourcery skip: extract-method
    form = forms.AdminSigupForm()
    if request.method == 'POST':
        form = forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(user.password)
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            return HttpResponseRedirect('adminlogin')
    return render(request, 'hospital/adminsignup.html', {'form': form})


def doctor_signup_view(request):  # sourcery skip: extract-method
    userForm = forms.DoctorUserForm()
    doctorForm = forms.DoctorForm()
    mydict = {'userForm': userForm, 'doctorForm': doctorForm}
    if request.method == 'POST':
        userForm = forms.DoctorUserForm(request.POST)
        doctorForm = forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            doctor = doctorForm.save(commit=False)
            doctor.user = user
            doctor = doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
        return HttpResponseRedirect('doctorlogin')
    return render(request, 'hospital/doctorsignup.html', context=mydict)


def patient_signup_view(request):  # sourcery skip: extract-method
    userForm = forms.PatientUserForm()
    patientForm = forms.PatientForm()
    mydict = {'userForm': userForm, 'patientForm': patientForm}
    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            patient = patientForm.save(commit=False)
            patient.user = user
            patient.assignedDoctorId = request.POST.get('assignedDoctorId')
            patient = patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request, 'hospital/patientsignup.html', context=mydict)


# ---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,DOCTOR OR PATIENT
def afterlogin_view(request):  # sourcery skip: use-named-expression
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        accountapproval = models.Doctor.objects.all().filter(
            user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request, 'hospital/doctor_wait_for_approval.html')
    elif is_patient(request.user):
        accountapproval = models.Patient.objects.all().filter(
            user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('patient-dashboard')
        else:
            return render(request, 'hospital/patient_wait_for_approval.html')


# ---------------------------------------------------------------------------------
# ------------------------ ADMIN RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    # for both table in admin dashboard
    doctors = models.Doctor.objects.all().order_by('-id')
    patients = models.Patient.objects.all().order_by('-id')
    # for three cards
    doctorcount = models.Doctor.objects.all().filter(status=True).count()
    pendingdoctorcount = models.Doctor.objects.all().filter(status=False).count()

    patientcount = models.Patient.objects.all().filter(status=True).count()
    pendingpatientcount = models.Patient.objects.all().filter(status=False).count()

    appointmentcount = models.Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount = models.Appointment.objects.all().filter(status=False).count()
    mydict = {
        'doctors': doctors,
        'patients': patients,
        'doctorcount': doctorcount,
        'pendingdoctorcount': pendingdoctorcount,
        'patientcount': patientcount,
        'pendingpatientcount': pendingpatientcount,
        'appointmentcount': appointmentcount,
        'pendingappointmentcount': pendingappointmentcount,
    }
    return render(request, 'hospital/admin_dashboard.html', context=mydict)


#--------------------------------------------------------------#


# ---------------------------------------------------------------------------------
# ------------------------ DOCTOR RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    # for three cards
    patientcount = models.Patient.objects.all().filter(
        status=True, assignedDoctorId=request.user.id).count()
    appointmentcount = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id).count()
    patientdischarged = models.PatientDischargeDetails.objects.all(
    ).distinct().filter(assignedDoctorName=request.user.first_name).count()

    # for  table in doctor dashboard
    appointments = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id).order_by('-id')
    patientid = []
    for a in appointments:
        patientid.append(a.patientId)
    patients = models.Patient.objects.all().filter(
        status=True, user_id__in=patientid).order_by('-id')
    appointments = zip(appointments, patients)
    mydict = {
        'patientcount': patientcount,
        'appointmentcount': appointmentcount,
        'patientdischarged': patientdischarged,
        'appointments': appointments,
        # for profile picture of doctor in sidebar
        'doctor': models.Doctor.objects.get(user_id=request.user.id),
    }
    return render(request, 'hospital/doctor_dashboard.html', context=mydict)


# -----------------------------------------------------------------------


# ---------------------------------------------------------------------------------
# ------------------------ PATIENT RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    doctor = models.Doctor.objects.get(user_id=patient.assignedDoctorId)
    mydict = {
        'patient': patient,
        'doctorName': doctor.get_name,
        'doctorMobile': doctor.mobile,
        'doctorAddress': doctor.address,
        'symptoms': patient.symptoms,
        'doctorDepartment': doctor.department,
        'admitDate': patient.admitDate,
    }
    return render(request, 'hospital/patient_dashboard.html', context=mydict)
