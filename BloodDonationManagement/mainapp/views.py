from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from .models import Donor, BloodRequest, BloodStock, Certificate, Payment
from datetime import date, datetime
from .certificate_generator import generate_certificate_id, generate_certificate_pdf
import random
import string


def admin_required(view_func):
    """Decorator to check if user is admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'Only administrators can perform this action.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


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
    
    # Get certificates for logged-in user (if not admin, show only their certificates)
    if request.user.is_superuser:
        recent_certificates = Certificate.objects.order_by('-issued_at')[:5]
    else:
        recent_certificates = Certificate.objects.filter(donor__user=request.user).order_by('-issued_at')[:5]
    
    context = {
        'total_donors': total_donors,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'available_blood_groups': available_blood_groups,
        'recent_donors': recent_donors,
        'recent_requests': recent_requests,
        'recent_certificates': recent_certificates,
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
                last_donation=last_donation if last_donation else None,
                status='Pending'  # New donors are pending by default
            )
            messages.success(request, f'Donor {name} added successfully! Your registration is pending approval.')
            return redirect('donor_list')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'add_donor.html')


@login_required
def donor_list(request):
    """List all donors view"""
    donors = Donor.objects.all().order_by('-created_at')
    
    # Get certificates for each donor - store certificate object by donor id
    donor_certificates = {}
    for donor in donors:
        cert = Certificate.objects.filter(donor=donor).first()
        if cert:
            donor_certificates[donor.id] = cert
    
    context = {
        'donors': donors,
        'donor_certificates': donor_certificates,
    }
    return render(request, 'donor_list.html', context)


@login_required
@admin_required
def edit_donor(request, id):
    """Edit donor view - Admin only"""
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
@admin_required
def delete_donor(request, id):
    """Delete donor view - Admin only"""
    try:
        donor = Donor.objects.get(id=id)
        donor.delete()
        messages.success(request, 'Donor deleted successfully!')
    except Donor.DoesNotExist:
        messages.error(request, 'Donor not found.')
    return redirect('donor_list')


@login_required
@admin_required
def approve_donor(request, id):
    """Approve donor view - Admin only
    Also generates a certificate for the donor upon approval
    """
    try:
        donor = Donor.objects.get(id=id)
        donor.status = 'Approved'
        
        # Set donation date to today (or use last_donation if provided)
        donation_date = donor.last_donation if donor.last_donation else date.today()
        
        donor.save()
        
        # Generate certificate for the donor
        certificate_id = generate_certificate_id()
        
        # Check if certificate already exists for this donor
        existing_cert = Certificate.objects.filter(donor=donor).first()
        if not existing_cert:
            certificate = Certificate.objects.create(
                certificate_id=certificate_id,
                donor=donor,
                donor_name=donor.name,
                blood_group=donor.blood_group,
                date_of_donation=donation_date,
                message="Thank you for saving lives"
            )
            messages.success(request, f'Donor {donor.name} approved successfully! Certificate {certificate_id} generated.')
        else:
            messages.success(request, f'Donor {donor.name} approved successfully! Certificate already exists.')
            
    except Donor.DoesNotExist:
        messages.error(request, 'Donor not found.')
    return redirect('donor_list')


@login_required
@admin_required
def reject_donor(request, id):
    """Reject donor view - Admin only"""
    try:
        donor = Donor.objects.get(id=id)
        donor.status = 'Rejected'
        donor.save()
        messages.success(request, f'Donor {donor.name} rejected!')
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
@admin_required
def approve_request(request, id):
    """Approve blood request view and deduct stock - Admin only"""
    try:
        blood_request = BloodRequest.objects.get(id=id)
        # Try to deduct from stock
        try:
            stock = BloodStock.objects.get(blood_group=blood_request.blood_group)
            if stock.units_available >= blood_request.units:
                stock.units_available -= blood_request.units
                stock.save()
                blood_request.status = 'Approved'
                blood_request.save()
                messages.success(request, f'Blood request approved! {blood_request.units} units deducted from stock.')
            else:
                messages.error(request, f'Insufficient stock! Available: {stock.units_available}, Required: {blood_request.units}')
        except BloodStock.DoesNotExist:
            blood_request.status = 'Approved'
            blood_request.save()
            messages.success(request, 'Blood request approved successfully!')
    except BloodRequest.DoesNotExist:
        messages.error(request, 'Blood request not found.')
    return redirect('request_list')


@login_required
@admin_required
def reject_request(request, id):
    """Reject blood request view - Admin only"""
    try:
        blood_request = BloodRequest.objects.get(id=id)
        blood_request.status = 'Rejected'
        blood_request.save()
        messages.success(request, 'Blood request rejected.')
    except BloodRequest.DoesNotExist:
        messages.error(request, 'Blood request not found.')
    return redirect('request_list')


@login_required
def cancel_request(request, id):
    """
    Cancel blood request view - Owner only
    Users can only cancel their own requests when status is 'Pending'
    """
    try:
        blood_request = BloodRequest.objects.get(id=id)
        
        # Check if the logged-in user is the owner of the request
        if blood_request.user != request.user:
            messages.error(request, 'You are not authorized to cancel this request.')
            return redirect('request_list')
        
        # Check if request status is Pending
        if blood_request.status != 'Pending':
            messages.error(request, 'You can only cancel pending requests.')
            return redirect('request_list')
        
        # Update status to Cancelled (do NOT delete from database)
        blood_request.status = 'Cancelled'
        blood_request.save()
        messages.success(request, 'Blood request cancelled successfully.')
        
    except BloodRequest.DoesNotExist:
        messages.error(request, 'Blood request not found.')
    
    return redirect('request_list')


@login_required
@admin_required
def delete_request(request, id):
    """Delete blood request view - Admin only"""
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
    """User profile view with certificates"""
    donors = Donor.objects.filter(user=request.user)
    requests = BloodRequest.objects.filter(user=request.user)
    
    # Get certificates for this user
    certificates = Certificate.objects.filter(donor__user=request.user).order_by('-issued_at')
    
    context = {
        'donors': donors,
        'requests': requests,
        'certificates': certificates,
    }
    return render(request, 'profile.html', context)


@login_required
@admin_required
def blood_stock(request):
    """Blood stock management view - Admin only"""
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        units = request.POST.get('units')
        action = request.POST.get('action')
        
        try:
            stock = BloodStock.objects.get(blood_group=blood_group)
            if action == 'add':
                stock.units_available += int(units)
            elif action == 'remove':
                stock.units_available = max(0, stock.units_available - int(units))
            stock.save()
            messages.success(request, f'Blood stock updated for {blood_group}!')
        except BloodStock.DoesNotExist:
            messages.error(request, 'Blood group not found.')
        return redirect('blood_stock')
    
    stocks = BloodStock.objects.all().order_by('blood_group')
    return render(request, 'blood_stock.html', {'stocks': stocks})


# ============================================
# Certificate Views
# ============================================

@login_required
def certificate_list(request):
    """
    List all certificates for the logged-in user.
    Admins can see all certificates.
    """
    if request.user.is_superuser:
        # Admin sees all certificates
        certificates = Certificate.objects.all().order_by('-issued_at')
    else:
        # Regular user sees only their certificates
        certificates = Certificate.objects.filter(donor__user=request.user).order_by('-issued_at')
    
    context = {
        'certificates': certificates,
    }
    return render(request, 'certificate_list.html', context)


@login_required
def download_certificate(request, certificate_id):
    """
    Download certificate as PDF.
    Only the donor or admin can download the certificate.
    """
    try:
        certificate = Certificate.objects.get(certificate_id=certificate_id)
        
        # Check if user is authorized (donor or admin)
        if not request.user.is_superuser and certificate.donor.user != request.user:
            messages.error(request, 'You are not authorized to download this certificate.')
            return redirect('dashboard')
        
        # Generate PDF
        pdf_content = generate_certificate_pdf(certificate)
        
        # Create response with PDF content
        response = HttpResponse(pdf_content, content_type='application/pdf')
        filename = f"Certificate_{certificate.certificate_id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Certificate.DoesNotExist:
        messages.error(request, 'Certificate not found.')
        return redirect('dashboard')


@login_required
@admin_required
def generate_certificate_for_donor(request, donor_id):
    """
    Manually generate a certificate for a donor (Admin only).
    """
    try:
        donor = Donor.objects.get(id=donor_id)
        
        # Check if donor is approved
        if donor.status != 'Approved':
            messages.error(request, 'Only approved donors can receive certificates.')
            return redirect('donor_list')
        
        # Check if certificate already exists
        existing_cert = Certificate.objects.filter(donor=donor).first()
        if existing_cert:
            messages.warning(request, f'Certificate already exists for this donor: {existing_cert.certificate_id}')
            return redirect('donor_list')
        
        # Generate new certificate
        certificate_id = generate_certificate_id()
        donation_date = donor.last_donation if donor.last_donation else date.today()
        
        certificate = Certificate.objects.create(
            certificate_id=certificate_id,
            donor=donor,
            donor_name=donor.name,
            blood_group=donor.blood_group,
            date_of_donation=donation_date,
            message="Thank you for saving lives"
        )
        
        messages.success(request, f'Certificate {certificate_id} generated for {donor.name}.')
        
    except Donor.DoesNotExist:
        messages.error(request, 'Donor not found.')
    
    return redirect('donor_list')


# ============================================
# Payment Views (Demo Paytm Integration)
# ============================================

def generate_payment_id():
    """
    Generate a unique payment ID.
    Format: PAY-YYYYMMDD-XXXXXX
    """
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"PAY-{date_str}-{random_str}"


def generate_transaction_id():
    """
    Generate a unique Paytm transaction ID.
    Format: TXN-XXXXXXXXXXXX
    """
    return f"TXN-{''.join(random.choices(string.ascii_uppercase + string.digits, k=12))}"


@login_required
def initiate_payment(request, request_id):
    """
    View to initiate payment for a blood request.
    Shows payment options including Paytm.
    """
    try:
        blood_request = BloodRequest.objects.get(id=request_id)
        
        # Check if user owns this request
        if blood_request.user != request.user and not request.user.is_superuser:
            messages.error(request, 'You are not authorized to make payment for this request.')
            return redirect('request_list')
        
        # Check if already paid
        if blood_request.status == 'Paid':
            messages.warning(request, 'This request has already been paid.')
            return redirect('request_list')
        
        # Calculate amount (demo: ₹500 per unit)
        amount = blood_request.units * 500
        
        context = {
            'blood_request': blood_request,
            'amount': amount,
        }
        return render(request, 'initiate_payment.html', context)
        
    except BloodRequest.DoesNotExist:
        messages.error(request, 'Blood request not found.')
        return redirect('request_list')


@login_required
def process_payment(request, request_id):
    """
    View to process payment via Paytm (simulated).
    """
    if request.method != 'POST':
        return redirect('request_list')
    
    try:
        blood_request = BloodRequest.objects.get(id=request_id)
        
        # Check if user owns this request
        if blood_request.user != request.user and not request.user.is_superuser:
            messages.error(request, 'You are not authorized to make payment for this request.')
            return redirect('request_list')
        
        # Check if already paid
        if blood_request.status == 'Paid':
            messages.warning(request, 'This request has already been paid.')
            return redirect('request_list')
        
        # Get payment method
        payment_method = request.POST.get('payment_method', 'Paytm')
        
        # Calculate amount
        amount = blood_request.units * 500
        
        # Generate payment ID and transaction ID
        payment_id = generate_payment_id()
        transaction_id = generate_transaction_id()
        
        # Create payment record
        payment = Payment.objects.create(
            blood_request=blood_request,
            payment_id=payment_id,
            amount=amount,
            payment_method=payment_method,
            status='Success',
            transaction_id=transaction_id,
            notes=f'Demo payment via {payment_method}'
        )
        
        # Update blood request status to Paid
        blood_request.status = 'Paid'
        blood_request.save()
        
        # Get payment details for success page
        context = {
            'payment': payment,
            'blood_request': blood_request,
        }
        return render(request, 'payment_success.html', context)
        
    except BloodRequest.DoesNotExist:
        messages.error(request, 'Blood request not found.')
        return redirect('request_list')


@login_required
def payment_history(request):
    """
    View to display payment history for the current user.
    Admins can see all payments.
    """
    if request.user.is_superuser:
        # Admin sees all payments
        payments = Payment.objects.all().order_by('-payment_date')
    else:
        # Regular user sees only their payments
        payments = Payment.objects.filter(blood_request__user=request.user).order_by('-payment_date')
    
    context = {
        'payments': payments,
    }
    return render(request, 'payment_history.html', context)
