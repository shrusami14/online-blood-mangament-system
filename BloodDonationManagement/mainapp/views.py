from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from .models import Donor, BloodRequest
from datetime import date


def home(request):
    """Home page view"""
    return render(request, 'home.html')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Blood Donation System.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    """Admin/User dashboard view"""
    total_donors = Donor.objects.count()
    total_requests = BloodRequest.objects.count()
    pending_requests = BloodRequest.objects.filter(status='Pending').count()
    approved_requests = BloodRequest.objects.filter(status='Approved').count()
    
    # Get distinct blood groups from donors (available blood groups)
    available_blood_groups = Donor.objects.values_list('blood_group', flat=True).distinct().count()
    
    # Get recent donors and requests
    recent_donors = Donor.objects.order_by('-created_at')[:5]
    recent_requests = BloodRequest.objects.order_by('-created_at')[:5]
    
    context = {
        'total_donors': total_donors,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'available_blood_groups': available_blood_groups,
        'recent_donors': recent_donors,
        'recent_requests': recent_requests,
    }
    return render(request, 'dashboard.html', context)


@login_required
def add_donor(request):
    """Add new donor view"""
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        blood_group = request.POST.get('blood_group')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        last_donation = request.POST.get('last_donation')
        
        if name and age and gender and blood_group and phone and city:
            donor = Donor.objects.create(
                user=request.user,
                name=name,
                age=age,
                gender=gender,
                blood_group=blood_group,
                phone=phone,
                city=city,
                last_donation=last_donation if last_donation else None
            )
            messages.success(request, f'Donor {name} added successfully!')
            return redirect('donor_list')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'add_donor.html')


@login_required
def donor_list(request):
    """List all donors view"""
    donors = Donor.objects.all().order_by('-created_at')
    return render(request, 'donor_list.html', {'donors': donors})


@login_required
def edit_donor(request, id):
    """Edit donor view"""
    try:
        donor = Donor.objects.get(id=id)
    except Donor.DoesNotExist:
        messages.error(request, 'Donor not found.')
        return redirect('donor_list')
    
    if request.method == 'POST':
        donor.name = request.POST.get('name')
        donor.age = request.POST.get('age')
        donor.gender = request.POST.get('gender')
        donor.blood_group = request.POST.get('blood_group')
        donor.phone = request.POST.get('phone')
        donor.city = request.POST.get('city')
        last_donation = request.POST.get('last_donation')
        donor.last_donation = last_donation if last_donation else None
        donor.save()
        messages.success(request, 'Donor updated successfully!')
        return redirect('donor_list')
    
    return render(request, 'edit_donor.html', {'donor': donor})


@login_required
def delete_donor(request, id):
    """Delete donor view"""
    try:
        donor = Donor.objects.get(id=id)
        donor.delete()
        messages.success(request, 'Donor deleted successfully!')
    except Donor.DoesNotExist:
        messages.error(request, 'Donor not found.')
    return redirect('donor_list')


@login_required
def request_blood(request):
    """Blood request view"""
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name')
        blood_group = request.POST.get('blood_group')
        units = request.POST.get('units')
        hospital = request.POST.get('hospital')
        city = request.POST.get('city')
        urgency = request.POST.get('urgency')
        
        if patient_name and blood_group and units and hospital and city:
            blood_request = BloodRequest.objects.create(
                user=request.user,
                patient_name=patient_name,
                blood_group=blood_group,
                units=units,
                hospital=hospital,
                city=city,
                urgency=urgency
            )
            messages.success(request, 'Blood request submitted successfully!')
            return redirect('request_list')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'request_blood.html')


@login_required
def request_list(request):
    """List all blood requests view"""
    requests = BloodRequest.objects.all().order_by('-created_at')
    return render(request, 'request_list.html', {'requests': requests})


@login_required
def approve_request(request, id):
    """Approve blood request view"""
    try:
        blood_request = BloodRequest.objects.get(id=id)
        blood_request.status = 'Approved'
        blood_request.save()
        messages.success(request, 'Blood request approved successfully!')
    except BloodRequest.DoesNotExist:
        messages.error(request, 'Blood request not found.')
    return redirect('request_list')


@login_required
def delete_request(request, id):
    """Delete blood request view"""
    try:
        blood_request = BloodRequest.objects.get(id=id)
        blood_request.delete()
        messages.success(request, 'Blood request deleted successfully!')
    except BloodRequest.DoesNotExist:
        messages.error(request, 'Blood request not found.')
    return redirect('request_list')


@login_required
def search(request):
    """Search donors by blood group and city"""
    blood_group = request.GET.get('blood_group', '')
    city = request.GET.get('city', '')
    
    donors = Donor.objects.all()
    
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if city:
        donors = donors.filter(city__icontains=city)
    
    donors = donors.order_by('-created_at')
    
    context = {
        'donors': donors,
        'blood_group': blood_group,
        'city': city,
    }
    return render(request, 'search.html', context)


@login_required
def profile(request):
    """User profile view"""
    donors = Donor.objects.filter(user=request.user)
    requests = BloodRequest.objects.filter(user=request.user)
    
    context = {
        'donors': donors,
        'requests': requests,
    }
    return render(request, 'profile.html')
