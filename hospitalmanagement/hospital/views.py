from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from multiprocessing import context
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
from . import forms, models
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta, date
from django.conf import settings
from django.db.models import Q
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


def is_technician(user):
    return user.groups.filter(name='TECHNICIAN').exists()


# for showing signup/login button for admin(by submit)
def adminclick_view(request):
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin-dashboard')
    context = {'error': 'Account Not Found, Please Register'}
    return render(request, 'hospital/adminclick.html', context=context)


# for showing signup/login button for doctor(by submit)
def doctorclick_view(request):
    if is_doctor(request.user):
        if accountapproval := models.Doctor.objects.all().filter(user_id=request.user.id, status=True):
            return redirect('doctor-dashboard')
        else:
            return render(request, 'hospital/doctor_wait_for_approval.html')
    context = {'error': 'Account Not Found, Please Register'}
    return render(request, 'hospital/doctorclick.html', context=context)


# for showing signup/login button for patient(by submit)
def patientclick_view(request):
    if is_patient(request.user):
        if accountapproval := models.Patient.objects.all().filter(user_id=request.user.id, status=True):
            return redirect('patient-dashboard')
        else:
            return render(request, 'hospital/patient_wait_for_approval.html')
    return render(request, 'hospital/patientclick.html')

# for showing signup/login button for technician(by submit)


def technicianclick_view(request):
    if is_technician(request.user):
        if accountapproval := models.Technician.objects.all().filter(user_id=request.user.id, status=True):
            return redirect('technician-dashboard')
        else:
            return render(request, 'hospital/technician_wait_for_approval.html')
    return render(request, 'hospital/technicianclick.html')

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


def technician_signup_view(request):  # sourcery skip: extract-method
    userForm = forms.TechnicianUserForm()
    technicianForm = forms.TechnicianForm()
    mydict = {'userForm': userForm, 'technicianForm': technicianForm}
    if request.method == 'POST':
        userForm = forms.TechnicianUserForm(request.POST)
        technicianForm = forms.TechnicianForm(request.POST, request.FILES)
        if userForm.is_valid() and technicianForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            technician = technicianForm.save(commit=False)
            technician.user = user
            technician.assignedDoctorId = request.POST.get('assignedDoctorId')
            technician = technician.save()
            my_technician_group = Group.objects.get_or_create(
                name='TECHNICIAN')
            my_technician_group[0].user_set.add(user)
        return HttpResponseRedirect('technicianlogin')
    return render(request, 'hospital/techniciansignup.html', context=mydict)


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

    elif is_technician(request.user):
        accountapproval = models.Technician.objects.all().filter(
            user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('technician-dashboard')
        else:
            return render(request, 'hospital/technician_wait_for_approval.html')


# ---------------------------------------------------------------------------------
# ------------------------ ADMIN RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    # for both table in admin dashboard
    doctors = models.Doctor.objects.all().order_by('-id')

    patients = models.Patient.objects.all().order_by('-id')
    technicians = models.Technician.objects.all().order_by('-id')
    # for three cards
    doctorcount = models.Doctor.objects.all().filter(status=True).count()
    pendingdoctorcount = models.Doctor.objects.all().filter(status=False).count()

    patientcount = models.Patient.objects.all().filter(status=True).count()
    pendingpatientcount = models.Patient.objects.all().filter(status=False).count()

    techniciancount = models.Technician.objects.all().filter(status=True).count()
    pendingtechniciancount = models.Technician.objects.all().filter(status=False).count()

    appointmentcount = models.Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount = models.Appointment.objects.all().filter(status=False).count()
    mydict = {
        'doctors': doctors,
        'patients': patients,
        'technicians': technicians,
        'doctorcount': doctorcount,
        'pendingdoctorcount': pendingdoctorcount,
        'patientcount': patientcount,
        'pendingpatientcount': pendingpatientcount,
        'techniciancount': techniciancount,
        'pendingtechniciancount': pendingtechniciancount,
        'appointmentcount': appointmentcount,
        'pendingappointmentcount': pendingappointmentcount,
        'techs_and_docs': zip(doctors,technicians),
    }
    return render(request, 'hospital/admin_dashboard.html', context=mydict)

# the view for sidebar click on technician page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_technician_view(request):
    return render(request, 'hospital/admin_technician.html')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_technician_view(request):
    technicians = models.Technician.objects.all().filter(status=True)
    return render(request, 'hospital/admin_view_technician.html', {'technicians': technicians})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_technician_from_hospital_view(request, pk):
    technician = models.Technician.objects.get(id=pk)
    user = models.User.objects.get(id=technician.user_id)
    user.delete()
    technician.delete()
    return redirect('admin-view-technician')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_technician_view(request, pk):
    technician = models.Technician.objects.get(id=pk)
    user = models.User.objects.get(id=technician.user_id)

    userForm = forms.TechnicianUserForm(instance=user)
    technicianForm = forms.TechnicianForm(request.FILES, instance=technician)
    mydict = {'userForm': userForm, 'technicianForm': technicianForm}
    if request.method == 'POST':
        userForm = forms.TechnicianUserForm(request.POST, instance=user)
        technicianForm = forms.TechnicianForm(
            request.POST, request.FILES, instance=technician)
        if userForm.is_valid() and technicianForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            technician = technicianForm.save(commit=False)
            technician.status = True
            technician.save()
            return redirect('admin-view-technician')
    return render(request, 'hospital/admin_update_technician.html', context=mydict)

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_technician_view(request):
    userForm = forms.TechnicianUserForm()
    technicianForm = forms.TechnicianForm()
    mydict = {'userForm': userForm, 'technicianForm': technicianForm}
    if request.method == 'POST':
        userForm = forms.TechnicianUserForm(request.POST)
        technicianForm = forms.TechnicianForm(request.POST, request.FILES)
        if userForm.is_valid() and technicianForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()

            technician = technicianForm.save(commit=False)
            technician.user = user
            technician.status = True
            technician.save()

            my_technician_group = Group.objects.get_or_create(name='TECHNICIAN')
            my_technician_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-technician')
    return render(request, 'hospital/admin_add_technician.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_technician_view(request):
    # those whose approval are needed
    technicians = models.Technician.objects.all().filter(status=False)
    return render(request, 'hospital/admin_approve_technician.html', {'technicians': technicians})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_technician_view(request, pk):
    technician = models.Technician.objects.get(id=pk)
    technician.status = True
    technician.save()
    return redirect(reverse('admin-approve-technician'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_technician_view(request, pk):
    technician = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=technician.user_id)
    user.delete()
    technician.delete()
    return redirect('admin-approve-technician')



# this view for doctor sidebar click on admin page


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request, 'hospital/admin_doctor.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors = models.Doctor.objects.all().filter(status=True)
    return render(request, 'hospital/admin_view_doctor.html', {'doctors': doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)

    userForm = forms.DoctorUserForm(instance=user)
    doctorForm = forms.DoctorForm(request.FILES, instance=doctor)
    mydict = {'userForm': userForm, 'doctorForm': doctorForm}
    if request.method == 'POST':
        userForm = forms.DoctorUserForm(request.POST, instance=user)
        doctorForm = forms.DoctorForm(
            request.POST, request.FILES, instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            doctor = doctorForm.save(commit=False)
            doctor.status = True
            doctor.save()
            return redirect('admin-view-doctor')
    return render(request, 'hospital/admin_update_doctor.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
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
            doctor.status = True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-doctor')
    return render(request, 'hospital/admin_add_doctor.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    # those whose approval are needed
    doctors = models.Doctor.objects.all().filter(status=False)
    return render(request, 'hospital/admin_approve_doctor.html', {'doctors': doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    doctor.status = True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors = models.Doctor.objects.all().filter(status=True)
    return render(request, 'hospital/admin_view_doctor_specialisation.html', {'doctors': doctors})


# ------Admin for patient--------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request, 'hospital/admin_patient.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients = models.Patient.objects.all().filter(status=True)
    return render(request, 'hospital/admin_view_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    user = models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    user = models.User.objects.get(id=patient.user_id)

    userForm = forms.PatientUserForm(instance=user)
    patientForm = forms.PatientForm(request.FILES, instance=patient)
    mydict = {'userForm': userForm, 'patientForm': patientForm}
    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST, instance=user)
        patientForm = forms.PatientForm(
            request.POST, request.FILES, instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            patient = patientForm.save(commit=False)
            patient.status = True
            patient.assignedDoctorId = request.POST.get('assignedDoctorId')
            patient.save()
            return redirect('admin-view-patient')
    return render(request, 'hospital/admin_update_patient.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
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
            patient.status = True
            patient.assignedDoctorId = request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-patient')
    return render(request, 'hospital/admin_add_patient.html', context=mydict)

# ------------------FOR APPROVING PATIENT BY ADMIN----------------------


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    # those whose approval are needed
    patients = models.Patient.objects.all().filter(status=False)
    return render(request, 'hospital/admin_approve_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    patient.status = True
    patient.save()
    return redirect(reverse('admin-approve-patient'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    user = models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')

# --------------------- FOR DISCHARGING PATIENT BY ADMIN START-------------------------


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    patients = models.Patient.objects.all().filter(status=True)
    return render(request, 'hospital/admin_discharge_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    days = date.today() - patient.admitDate
    assignedDoctor = models.User.objects.all().filter(id=patient.assignedDoctorId)
    d = days.days
    patientDict = {'patientId': pk, 'name': patient.get_name, 'mobile': patient.mobile, 'address': patient.address, 'symptoms': patient.symptoms,
                   'admitDate': patient.admitDate, 'todayDate': date.today(), 'day': d, 'assignedDoctorName': assignedDoctor[0].first_name}

    patientDict = {'patientId': pk, 'name': patient.get_name, 'mobile': patient.mobile, 'address': patient.address, 'symptoms': patient.symptoms,
                   'admitDate': patient.admitDate, 'todayDate': date.today(), 'day': d, 'assignedDoctorName': assignedDoctor[0].first_name}

    if request.method == 'POST':
        feeDict = {'roomCharge': int(request.POST['roomCharge']) * int(d), 'doctorFee': request.POST['doctorFee'], 'medicineCost': request.POST['medicineCost'], 'OtherCharge': request.POST['OtherCharge'],
                   'total': int(request.POST['roomCharge']) * int(d) + int(request.POST['doctorFee']) + int(request.POST['medicineCost']) + int(request.POST['OtherCharge'])}

        patientDict |= feeDict
        pDD = models.PatientDischargeDetails()
        pDD.patientId = pk
        pDD.patientName = patient.get_name
        pDD.assignedDoctorName = assignedDoctor[0].first_name
        pDD.address = patient.address
        pDD.mobile = patient.mobile
        pDD.symptoms = patient.symptoms
        pDD.admitDate = patient.admitDate
        pDD.releaseDate = date.today()
        pDD.daySpent = int(d)
        pDD.medicineCost = int(request.POST['medicineCost'])
        pDD.roomCharge = int(request.POST['roomCharge']) * int(d)
        pDD.doctorFee = int(request.POST['doctorFee'])
        pDD.OtherCharge = int(request.POST['OtherCharge'])
        pDD.total = (int(request.POST['roomCharge']) * int(d) + int(request.POST['doctorFee']) + int(
            request.POST['medicineCost'])) + int(request.POST['OtherCharge'])

        pDD.save()
        return render(request, 'hospital/patient_final_bill.html', context=patientDict)
    return render(request, 'hospital/patient_generate_bill.html', context=patientDict)


# --------------for discharge patient bill (pdf) download and printing


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return


def download_pdf_view(request, pk):  # sourcery skip: avoid-builtin-shadow
    dischargeDetails = models.PatientDischargeDetails.objects.all().filter(
        patientId=pk).order_by('-id')[:1]
    dict = {
        'patientName': dischargeDetails[0].patientName,
        'assignedDoctorName': dischargeDetails[0].assignedDoctorName,
        'address': dischargeDetails[0].address,
        'mobile': dischargeDetails[0].mobile,
        'symptoms': dischargeDetails[0].symptoms,
        'admitDate': dischargeDetails[0].admitDate,
        'releaseDate': dischargeDetails[0].releaseDate,
        'daySpent': dischargeDetails[0].daySpent,
        'medicineCost': dischargeDetails[0].medicineCost,
        'roomCharge': dischargeDetails[0].roomCharge,
        'doctorFee': dischargeDetails[0].doctorFee,
        'OtherCharge': dischargeDetails[0].OtherCharge,
        'total': dischargeDetails[0].total,
    }
    return render_to_pdf('hospital/download_bill.html', dict)

# -----------------APPOINTMENT START-------------------------------------------------------------------


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request, 'hospital/admin_appointment.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments = models.Appointment.objects.all().filter(status=True)
    return render(request, 'hospital/admin_view_appointment.html', {'appointments': appointments})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    appointmentForm = forms.AppointmentForm()
    mydict = {'appointmentForm': appointmentForm, }
    if request.method == 'POST':
        appointmentForm = forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment = appointmentForm.save(commit=False)
            appointment.doctorId = request.POST.get('doctorId')
            appointment.patientId = request.POST.get('patientId')
            appointment.doctorName = models.User.objects.get(
                id=request.POST.get('doctorId')).first_name
            appointment.patientName = models.User.objects.get(
                id=request.POST.get('patientId')).first_name
            appointment.status = True
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request, 'hospital/admin_add_appointment.html', context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    # those whose approval are needed
    appointments = models.Appointment.objects.all().filter(status=False)
    return render(request, 'hospital/admin_approve_appointment.html', {'appointments': appointments})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request, pk):
    appointment = models.Appointment.objects.get(id=pk)
    appointment.status = True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request, pk):
    appointment = models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')
# ---------------------------------------------------------------------------------
# ------------------------ ADMIN RELATED VIEWS END ------------------------------
# ---------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------
# ------------------------ TECHNICIAN RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------
@login_required(login_url='technicianlogin')
@user_passes_test(is_technician)
def technician_dashboard_view(request):
    technician = models.Technician.objects.get(user_id = request.user.id)
    doctor = models.Doctor.objects.get(user_id=technician.assignedDoctorId)
    test = models.Test.objects.all().order_by('-id')
    testcount = models.Test.objects.all().filter(status=True).count()
    pendingtestcount = models.Test.objects.all().filter(status=False).count()
    mydict = {
        'technician':technician,
        'doctorName': doctor.get_name,
        'doctorMobile': doctor.mobile,
        'doctorAddress': doctor.address,
        'doctorDepartment': doctor.department,
        'test': test,
        'testcount':testcount,
        'pendingtestcount':pendingtestcount,
    }
    return render(request, 'hospital/technician_dashboard.html', context=mydict)


# technician update pending tests
@login_required(login_url='technicianlogin')
@user_passes_test(is_technician)
def technician_test_view(request):
    return render(request, 'hospital/technician_test.html')


@login_required(login_url='technicianlogin')
@user_passes_test(is_technician)
def technician_view_test_view(request):
    tests = models.Test.objects.all().filter(technicianId=request.user.id).order_by('-id')
    return render(request, 'hospital/technician_view_test.html', {'tests': tests})

@login_required(login_url='technicianlogin')
@user_passes_test(is_technician)
def technician_update_test_result(request, pk):
    test = models.Test.objects.get(id=pk)
    patientId = test.patientId
    technicianId = request.user.id
    desc = test.description

    testForm = forms.TestForm(instance=test)
    mydict = {'testForm': testForm , 'patientId': patientId, 'technicianId': technicianId}

    if request.method == 'POST':
        testForm = forms.TestForm(request.POST)

        if testForm.is_valid():
            test = testForm.save(commit=False)
            test.result = request.POST.get('result')
            test.status = True
            test.save()
            return redirect('technician_test_view')
    return render(request, 'hospital/technician_update_test.html', context=mydict)



# ---------------------------------------------------------------------------------
# ------------------------ DOCTOR RELATED VIEWS START -----------------------------
# ---------------------------------------------------------------------------------


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    patientcount = models.Patient.objects.all().filter(
        status=True, assignedDoctorId=request.user.id).count()

    appointmentcount = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id).count()

    patientdischarged = models.PatientDischargeDetails.objects.all(
    ).distinct().filter(assignedDoctorName=request.user.first_name).count()

    appointments = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id).order_by('-id')

    patientid = [a.patientId for a in appointments]
    patients = models.Patient.objects.all().filter(
        status=True, user_id__in=patientid).order_by('-id')

    appointments = zip(appointments, patients)
    mydict = {'patientcount': patientcount, 'appointmentcount': appointmentcount, 'patientdischarged': patientdischarged,
              'appointments': appointments, 'doctor': models.Doctor.objects.get(user_id=request.user.id)}

    return render(request, 'hospital/doctor_dashboard.html', context=mydict)


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict = {
        # for profile picture of doctor in sidebar
        'doctor': models.Doctor.objects.get(user_id=request.user.id),
    }
    return render(request, 'hospital/doctor_patient.html', context=mydict)


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    patients = models.Patient.objects.all().filter(
        status=True, assignedDoctorId=request.user.id)
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor_view_patient.html', {'patients': patients, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def search_view(request):
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients = models.Patient.objects.all().filter(status=True, assignedDoctorId=request.user.id).filter(
        Q(symptoms__icontains=query) | Q(user__first_name__icontains=query))
    return render(request, 'hospital/doctor_view_patient.html', {'patients': patients, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    dischargedpatients = models.PatientDischargeDetails.objects.all(
    ).distinct().filter(assignedDoctorName=request.user.first_name)
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor_view_discharge_patient.html', {'dischargedpatients': dischargedpatients, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor_appointment.html', {'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id)
    patientid = [a.patientId for a in appointments]
    patients = models.Patient.objects.all().filter(
        status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor_view_appointment.html', {'appointments': appointments, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id)
    patientid = [a.patientId for a in appointments]
    patients = models.Patient.objects.all().filter(
        status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor_delete_appointment.html', {'appointments': appointments, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request, pk):
    appointment = models.Appointment.objects.get(id=pk)
    appointment.delete()
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id)
    patientid = [a.patientId for a in appointments]
    patients = models.Patient.objects.all().filter(
        status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor_delete_appointment.html', {'appointments': appointments, 'doctor': doctor})



# Doctor prescribe tests of patient to technician

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_test(request):
    # for profile picture of patient in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor_test.html', {'doctor': doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_test_view(request):
    # for profile picture of patient in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    tests = models.Test.objects.all().filter(doctorId=request.user.id)
    return render(request, 'hospital/doctor_view_test.html', {'doctor': doctor, 'tests': tests})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_add_test(request):
    testForm = forms.TestForm()
    # for profile picture of patient in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    message = None
    mydict = {'testForm': testForm,
              'doctor': doctor, 'message': message}
    if request.method == 'POST':
        testForm = forms.TestForm(request.POST)
        if testForm.is_valid():
            desc = request.POST.get('description')

            patient = models.Patient.objects.get(
                user_id=request.POST.get('patientId'))

            test = testForm.save(commit=False)
            test.technicianId = request.POST.get('technicianId')
            # ----user can choose any patient but only their info will be stored
            test.patientId = request.POST.get('patientId')
            test.doctorId = request.user.id
            test.doctorName = request.user.first_name

            test.technicianName = models.User.objects.get(
                id=request.POST.get('technicianId')).first_name
            # ----user can choose any patient but only their info will be stored
            test.patientName = models.User.objects.get(
                id=request.POST.get('patientId')).first_name
            test.status = False
            test.save()
        return HttpResponseRedirect('doctor-view-test')
    return render(request, 'hospital/doctor_add_test.html', context=mydict)

# ---------------------------------------------------------------------------------
# ------------------------ DOCTOR RELATED VIEWS END ------------------------------
# ---------------------------------------------------------------------------------


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


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    # for profile picture of patient in sidebar
    patient = models.Patient.objects.get(user_id=request.user.id)
    return render(request, 'hospital/patient_appointment.html', {'patient': patient})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    appointmentForm = forms.PatientAppointmentForm()
    # for profile picture of patient in sidebar
    patient = models.Patient.objects.get(user_id=request.user.id)
    message = None
    mydict = {'appointmentForm': appointmentForm,
              'patient': patient, 'message': message}
    if request.method == 'POST':
        appointmentForm = forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            desc = request.POST.get('description')

            doctor = models.Doctor.objects.get(
                user_id=request.POST.get('doctorId'))

            appointment = appointmentForm.save(commit=False)
            appointment.doctorId = request.POST.get('doctorId')
            # ----user can choose any patient but only their info will be stored
            appointment.patientId = request.user.id
            appointment.doctorName = models.User.objects.get(
                id=request.POST.get('doctorId')).first_name
            # ----user can choose any patient but only their info will be stored
            appointment.patientName = request.user.first_name
            appointment.status = False
            appointment.save()
        return HttpResponseRedirect('patient-view-appointment')
    return render(request, 'hospital/patient_book_appointment.html', context=mydict)


def patient_view_doctor_view(request):
    doctors = models.Doctor.objects.all().filter(status=True)
    # for profile picture of patient in sidebar
    patient = models.Patient.objects.get(user_id=request.user.id)
    return render(request, 'hospital/patient_view_doctor.html', {'patient': patient, 'doctors': doctors})


def search_doctor_view(request):
    # for profile picture of patient in sidebar
    patient = models.Patient.objects.get(user_id=request.user.id)

    # whatever user write in search box we get in query
    query = request.GET['query']
    doctors = models.Doctor.objects.all().filter(status=True).filter(
        Q(department__icontains=query) | Q(user__first_name__icontains=query))
    return render(request, 'hospital/patient_view_doctor.html', {'patient': patient, 'doctors': doctors})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    # for profile picture of patient in sidebar
    patient = models.Patient.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request, 'hospital/patient_view_appointment.html', {'appointments': appointments, 'patient': patient})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    # for profile picture of patient in sidebar
    patient = models.Patient.objects.get(user_id=request.user.id)
    dischargeDetails = models.PatientDischargeDetails.objects.all().filter(
        patientId=patient.id).order_by('-id')[:1]
    patientDict = None
    if dischargeDetails:
        patientDict = {
            'is_discharged': True,
            'patient': patient,
            'patientId': patient.id,
            'patientName': patient.get_name,
            'assignedDoctorName': dischargeDetails[0].assignedDoctorName,
            'address': patient.address,
            'mobile': patient.mobile,
            'symptoms': patient.symptoms,
            'admitDate': patient.admitDate,
            'releaseDate': dischargeDetails[0].releaseDate,
            'daySpent': dischargeDetails[0].daySpent,
            'medicineCost': dischargeDetails[0].medicineCost,
            'roomCharge': dischargeDetails[0].roomCharge,
            'doctorFee': dischargeDetails[0].doctorFee,
            'OtherCharge': dischargeDetails[0].OtherCharge,
            'total': dischargeDetails[0].total,
        }
        print(patientDict)
    else:
        patientDict = {
            'is_discharged': False,
            'patient': patient,
            'patientId': request.user.id,
        }
    return render(request, 'hospital/patient_discharge.html', context=patientDict)


# ------------------------ PATIENT RELATED VIEWS END ------------------------------
# ---------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------
# ------------------------ ABOUT US AND CONTACT US VIEWS START ------------------------------
# ---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request, 'hospital/aboutus.html')


def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name = sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(f'{str(name)} || {str(email)}', message, settings.EMAIL_HOST_USER,
                      settings.EMAIL_RECEIVING_USER, fail_silently=False)

            return render(request, 'hospital/contactussuccess.html')
    return render(request, 'hospital/contactus.html', {'form': sub})
