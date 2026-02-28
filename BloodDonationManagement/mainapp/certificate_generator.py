"""
Certificate Generator Utility
Generates PDF certificates for blood donors using reportlab
"""
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import uuid


def generate_certificate_id():
    """
    Generate a unique certificate ID.
    Format: CERT-YYYY-XXXXX (e.g., CERT-2024-00001)
    """
    year = datetime.now().year
    unique_id = str(uuid.uuid4())[:5].upper()
    return f"CERT-{year}-{unique_id}"


def generate_certificate_pdf(certificate):
    """
    Generate a PDF certificate for a blood donor.
    
    Args:
        certificate: Certificate model instance
    
    Returns:
        bytes: PDF content as bytes
    """
    # Create a buffer to hold the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document (landscape A4)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=30*mm,
        leftMargin=30*mm,
        topMargin=30*mm,
        bottomMargin=30*mm
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=36,
        textColor=colors.HexColor('#dc3545'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=24,
        textColor=colors.HexColor('#333333'),
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName='Helvetica'
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        alignment=TA_CENTER,
        spaceAfter=10,
        fontName='Helvetica'
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    message_style = ParagraphStyle(
        'Message',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.HexColor('#28a745'),
        alignment=TA_CENTER,
        spaceBefore=30,
        fontName='Helvetica-Bold'
    )
    
    # Build the certificate content
    story = []
    
    # Title
    story.append(Paragraph("BLOOD DONATION CERTIFICATE", title_style))
    story.append(Spacer(1, 10))
    
    # Subtitle
    story.append(Paragraph("Certificate of Appreciation", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Certificate ID
    story.append(Paragraph(f"Certificate ID: {certificate.certificate_id}", label_style))
    story.append(Spacer(1, 30))
    
    # Main content table
    # Donor name
    story.append(Paragraph("This is to certify that", normal_style))
    story.append(Spacer(1, 10))
    
    donor_name_style = ParagraphStyle(
        'DonorName',
        parent=styles['Heading2'],
        fontSize=28,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(certificate.donor_name, donor_name_style))
    story.append(Spacer(1, 15))
    
    # Blood group
    story.append(Paragraph("has successfully donated blood", normal_style))
    story.append(Spacer(1, 10))
    
    blood_group_style = ParagraphStyle(
        'BloodGroup',
        parent=styles['Heading1'],
        fontSize=32,
        textColor=colors.HexColor('#dc3545'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(f"Blood Group: {certificate.blood_group}", blood_group_style))
    story.append(Spacer(1, 20))
    
    # Date of donation
    date_str = certificate.date_of_donation.strftime('%B %d, %Y')
    story.append(Paragraph(f"Date of Donation: {date_str}", normal_style))
    story.append(Spacer(1, 30))
    
    # Thank you message
    story.append(Paragraph(certificate.message, message_style))
    story.append(Spacer(1, 20))
    
    # Footer with system info
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
        spaceBefore=40
    )
    story.append(Paragraph("Blood Donation Management System", footer_style))
    story.append(Paragraph(f"Issued on: {datetime.now().strftime('%B %d, %Y at %H:%M')}", footer_style))
    
    # Build the PDF
    doc.build(story)
    
    # Get the PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content
