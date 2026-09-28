import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdf_filename = "Lalithas_Math_Academy_Documentation.pdf"
doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=letter,
    rightMargin=36, leftMargin=36,
    topMargin=36, bottomMargin=36
)

styles = getSampleStyleSheet()

# Custom color palette
primary_color = colors.HexColor("#7c3aed")
secondary_col = colors.HexColor("#0284c7")
text_dark     = colors.HexColor("#1e293b")

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=20,
    leading=24,
    textColor=primary_color,
    alignment=1,
    spaceAfter=4
)

subtitle_style = ParagraphStyle(
    'DocSubtitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=13,
    textColor=colors.HexColor("#64748b"),
    alignment=1,
    spaceAfter=12
)

h1_style = ParagraphStyle(
    'SectionH1',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=16,
    textColor=primary_color,
    spaceBefore=12,
    spaceAfter=6
)

h2_style = ParagraphStyle(
    'SectionH2',
    parent=styles['Heading3'],
    fontName='Helvetica-Bold',
    fontSize=10.5,
    leading=14,
    textColor=secondary_col,
    spaceBefore=8,
    spaceAfter=4
)

body_style = ParagraphStyle(
    'BodyTextCustom',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=13,
    textColor=text_dark,
    spaceAfter=4
)

bullet_style = ParagraphStyle(
    'BulletCustom',
    parent=body_style,
    leftIndent=12,
    spaceAfter=3
)

code_style = ParagraphStyle(
    'CodeCustom',
    parent=styles['Normal'],
    fontName='Courier',
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor("#d97706"),
    backColor=colors.HexColor("#fef3c7"),
    borderColor=colors.HexColor("#fcd34d"),
    borderWidth=0.5,
    borderPadding=5,
    spaceBefore=4,
    spaceAfter=6
)

story = []

# Title & Subtitle
story.append(Paragraph("🎓 Lalitha's Math Academy", title_style))
story.append(Paragraph("Comprehensive System Documentation & Technical Delivery Guide", subtitle_style))
story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=12))

# 1. Executive Summary
story.append(Paragraph("1. 📌 Executive Summary", h1_style))
story.append(Paragraph(
    "<b>Lalitha's Math Academy Tuition Platform</b> is a full-stack web application designed for managing student registrations, class scheduling, custom booking packages, and automated admin management. "
    "The platform uses <b>Google Sheets</b> as its real-time database, enabling direct spreadsheet access for the academy administrator (V. Lalitha Ma'am) without complex database overhead.",
    body_style
))

# 2. Admin Credentials
story.append(Paragraph("2. 🔑 Admin Authentication & Credentials", h1_style))
admin_data = [
    [Paragraph("<b>Admin Portal URL</b>", body_style), Paragraph("<code>/admin-page</code> (e.g., https://your-domain.com/admin-page)", body_style)],
    [Paragraph("<b>Admin Password</b>", body_style), Paragraph("<b>Lalitha@MathAcademy</b>", body_style)],
    [Paragraph("<b>Security Enforcement</b>", body_style), Paragraph("Strict single-password check with SHA-256 hash backup in Google Sheets <code>admin</code> worksheet.", body_style)]
]
t_admin = Table(admin_data, colWidths=[140, 380])
t_admin.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ('PADDING', (0,0), (-1,-1), 5),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t_admin)
story.append(Spacer(1, 8))

# 3. Technical Architecture
story.append(Paragraph("3. 🛠️ Technology Stack Architecture", h1_style))
tech_data = [
    [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Description</b>", body_style)],
    [Paragraph("Backend Framework", body_style), Paragraph("Flask (Python 3.11)", body_style), Paragraph("Python web framework managing session auth, API endpoints, and dynamic HTML rendering.", body_style)],
    [Paragraph("Database Integration", body_style), Paragraph("GSpread / GSheets API v4", body_style), Paragraph("Real-time spreadsheet read/write with automatic service account authentication.", body_style)],
    [Paragraph("Frontend UI / UX", body_style), Paragraph("HTML5 / Vanilla CSS3 / JS", body_style), Paragraph("Modern glassmorphism UI, responsive layouts, interactive day/time pickers.", body_style)],
    [Paragraph("WSGI Server", body_style), Paragraph("Gunicorn 22.0", body_style), Paragraph("Production-grade WSGI HTTP server for Render cloud deployment.", body_style)],
    [Paragraph("Cloud Hosting", body_style), Paragraph("Render Free Plan", body_style), Paragraph("Auto-deploy container with Procfile & render.yaml configurations.", body_style)],
    [Paragraph("Notifications", body_style), Paragraph("WhatsApp wa.me & CallMeBot", body_style), Paragraph("Direct pre-filled WhatsApp links & automatic status notifications.", body_style)],
]
t_tech = Table(tech_data, colWidths=[110, 130, 280])
t_tech.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#ede9fe")),
    ('TEXTCOLOR', (0,0), (-1,0), primary_color),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ('PADDING', (0,0), (-1,-1), 4),
]))
story.append(t_tech)
story.append(Spacer(1, 8))

# 4. Detailed Module Explanation
story.append(Paragraph("4. 🧩 Detailed Module-by-Module Working", h1_style))

story.append(Paragraph("A. Student Registration & Authentication", h2_style))
story.append(Paragraph("• <b>Registration Form:</b> Collects student's Full Name, Class (Grade 1 to 12), School Name, Address, Pincode, 10-digit Phone Number, and Password. Creates a new record in GSheets <code>users</code> sheet.", bullet_style))
story.append(Paragraph("• <b>Login Form:</b> Validates 10-digit phone number and SHA-256 hashed password. Creates secure session for student dashboard access.", bullet_style))

story.append(Paragraph("B. Student Booking Engine (4 Flexible Plans)", h2_style))
story.append(Paragraph("• <b>1. Hourly Plan (hourly):</b> Student specifies <b>Hours Needed</b> (1–4 hrs), selects an available time slot from live GSheets data, picks a preferred start date, and chooses class mode (Offline/Online). Day picker is hidden for hourly.", bullet_style))
story.append(Paragraph("• <b>2. Weekly Plan (weekly):</b> Student enters number of days per week, selects specific days (including Sunday), selects hours per session, chooses an available time slot, and sets total duration in weeks.", bullet_style))
story.append(Paragraph("• <b>3. Monthly Package (monthly):</b> Offers a <b>⚡ Daily (Mon–Sun)</b> toggle button or <b>Specific Days/Week</b> option. Student sets number of months, hours per session, time slot from GSheets, and preferred start date.", bullet_style))
story.append(Paragraph("• <b>4. Yearly Program (yearly):</b> Designed for long-term board exam prep (3, 6, 9, 12 months). Supports <b>Daily</b> or <b>Specific Days</b> schedule, hours per class, and GSheets time slots.", bullet_style))

story.append(Paragraph("C. Admin Management Portal (Password: Lalitha@MathAcademy)", h2_style))
story.append(Paragraph("• <b>Overview Dashboard:</b> Real-time counters for Pending Requests, Confirmed Sessions, and Slot Availability.", bullet_style))
story.append(Paragraph("• <b>Pending Requests Tab:</b> Lists all pending bookings with student phone, plan, days, time slot, and mode. Admin can enter Google Meet links for online classes and click <code>✅ Confirm</code> or <code>📲 Remind</code>.", bullet_style))
story.append(Paragraph("• <b>Confirmed Sessions Tab:</b> Displays active confirmed sessions with student contact info, meet links, and direct WhatsApp buttons.", bullet_style))
story.append(Paragraph("• <b>Availability Slot Manager:</b> Interactive toggle switches for every day of the week (Monday through <b>Sunday</b>). Clicking <code>💾 Save Availability</code> updates GSheets in real-time.", bullet_style))
story.append(Paragraph("• <b>Academy Settings:</b> Allows admin to customize available days, max days per week, default time slots list, min/max hours, and pricing display hints.", bullet_style))
story.append(Paragraph("• <b>Registered Students Directory:</b> View complete student database with school name, address, pincode, and registration timestamp.", bullet_style))

# 5. Database Schema
story.append(Paragraph("5. 📊 Google Sheets Database Structure (9 Worksheets)", h1_style))
sheets_data = [
    [Paragraph("<b>Worksheet Name</b>", body_style), Paragraph("<b>Key Columns / Schema</b>", body_style), Paragraph("<b>Purpose</b>", body_style)],
    [Paragraph("<code>users</code>", body_style), Paragraph("id, full_name, class, school, address, pincode, phone, password_hash, created_at", body_style), Paragraph("Student accounts & login credentials.", body_style)],
    [Paragraph("<code>admin</code>", body_style), Paragraph("username, password_hash", body_style), Paragraph("Admin account hash.", body_style)],
    [Paragraph("<code>settings</code>", body_style), Paragraph("key, value, description", body_style), Paragraph("Academy preferences & default slots.", body_style)],
    [Paragraph("<code>bookings</code>", body_style), Paragraph("id, user_id, full_name, phone, class, school, mode, basis, quantity, days_of_week, time_slot, preferred_date, status, meet_link", body_style), Paragraph("All booking requests.", body_style)],
    [Paragraph("<code>confirmed_bookings</code>", body_style), Paragraph("(Same schema as bookings)", body_style), Paragraph("Confirmed sessions index.", body_style)],
    [Paragraph("<code>available_slots</code>", body_style), Paragraph("day, time_slot, is_available", body_style), Paragraph("Live availability toggles (Mon–Sun).", body_style)],
    [Paragraph("<code>carousel_images</code>", body_style), Paragraph("url, caption, order", body_style), Paragraph("Homepage hero carousel images.", body_style)],
    [Paragraph("<code>pricing</code>", body_style), Paragraph("basis, description, price_hint, highlight", body_style), Paragraph("Plan features & pricing hints.", body_style)],
    [Paragraph("<code>contact_info</code>", body_style), Paragraph("key, value", body_style), Paragraph("Phone, email, address & map embed.", body_style)],
]
t_sheets = Table(sheets_data, colWidths=[100, 240, 180])
t_sheets.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e0f2fe")),
    ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0284c7")),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ('PADDING', (0,0), (-1,-1), 4),
]))
story.append(t_sheets)
story.append(Spacer(1, 8))

# 6. Render Cloud Deployment
story.append(Paragraph("6. 🚀 Render Free Plan Deployment Guide", h1_style))
story.append(Paragraph("To deploy this platform on Render Free Web Service:", body_style))
story.append(Paragraph("1. Push repository to GitHub.", bullet_style))
story.append(Paragraph("2. Create a new <b>Web Service</b> on Render connected to your repository.", bullet_style))
story.append(Paragraph("3. Render automatically detects <code>Procfile</code> and <code>render.yaml</code>.", bullet_style))
story.append(Paragraph("4. In Render Dashboard Environment Variables, set:", bullet_style))
story.append(Paragraph("<code>PORT</code> = <code>10000</code><br/><code>ADMIN_PASSWORD</code> = <code>Lalitha@MathAcademy</code><br/><code>GOOGLE_SHEET_ID</code> = <i>your_spreadsheet_id</i><br/><code>GOOGLE_CREDENTIALS_JSON</code> = <i>paste JSON key contents</i>", code_style))

doc.build(story)
print(f"✅ Generated PDF document: {pdf_filename}")
