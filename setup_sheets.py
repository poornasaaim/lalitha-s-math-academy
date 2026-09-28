"""
setup_sheets.py — One-time initializer for Google Sheets
Run this once to create all required worksheets with headers and sample data.

Usage:
    python3 setup_sheets.py

Sheets created:
    1. users           — Student registrations (login/register)
    2. admin           — Admin login credentials
    3. settings        — Admin preferences (slots, pricing, days, etc.)
    4. bookings        — All booking requests (pending + confirmed)
    5. confirmed_bookings — Copy of confirmed bookings for quick access
    6. carousel_images — Homepage hero carousel
    7. contact_info    — Academy contact details
    8. available_slots — Day-wise time slot availability
    9. pricing         — Plan descriptions
"""

import os
import sys
import hashlib
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_ID   = os.getenv("GOOGLE_SHEET_ID", "").strip()
CREDS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_or_create_worksheet(spreadsheet, title: str, rows=100, cols=20):
    try:
        ws = spreadsheet.worksheet(title)
        print(f"  ✓ Sheet '{title}' already exists — skipping creation.")
        return ws
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)
        print(f"  + Created sheet '{title}'")
        return ws


def setup():
    # ── Validate environment ──────────────────────────────────────────────────
    if not SHEET_ID:
        print("❌ ERROR: GOOGLE_SHEET_ID is not set in your .env file.")
        print("   Please edit .env and set: GOOGLE_SHEET_ID=your_spreadsheet_id_here\n")
        sys.exit(1)

    if not os.path.exists(CREDS_FILE):
        print(f"❌ ERROR: Credentials file '{CREDS_FILE}' not found.")
        print("   Please place your Google Service Account key file named 'credentials.json' in the project root directory.\n")
        sys.exit(1)

    if os.path.getsize(CREDS_FILE) == 0:
        print(f"⚠️  ERROR: '{CREDS_FILE}' is empty (0 bytes).")
        print("   To use real Google Sheets:")
        print("   1. Go to Google Cloud Console → APIs & Services → Credentials")
        print("   2. Create a Service Account and download its JSON key")
        print("   3. Share your Google Sheet with the service account email")
        print("   4. Save the JSON key contents into 'credentials.json'\n")
        print("💡 NOTE: The web app already works in DEMO MODE without credentials!")
        sys.exit(1)

    try:
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEET_ID)
    except Exception as e:
        print(f"❌ ERROR connecting to Google Sheets: {e}")
        print(f"   Ensure '{CREDS_FILE}' contains valid Service Account JSON")
        print(f"   and the sheet ID '{SHEET_ID}' is shared with the service account email.\n")
        sys.exit(1)

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║   Lalitha's Math Academy — Google Sheets Setup         ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    # ── 1. users ──────────────────────────────────────────────────────────────
    ws = get_or_create_worksheet(spreadsheet, "users")
    if ws.row_count == 0 or ws.cell(1, 1).value != "id":
        ws.clear()
        ws.append_row(["id", "full_name", "class", "school", "address", "pincode", "phone", "password_hash", "created_at"])
        ws.append_row([1, "Arjun Kumar", "10", "Govt Higher Secondary School",
                       "12, Anna Nagar, Chennai", "600040", "9876543210",
                       hash_password("student123"), "2024-01-15 10:00:00"])
        ws.append_row([2, "Priya Sharma", "12", "DAV Matriculation School",
                       "45, T.Nagar, Chennai", "600017", "9876543211",
                       hash_password("student456"), "2024-01-16 11:30:00"])
        print("    → Added sample users")
        print("      Demo Login 1: phone=9876543210, password=student123")
        print("      Demo Login 2: phone=9876543211, password=student456")

    # ── 2. admin ──────────────────────────────────────────────────────────────
    ws = get_or_create_worksheet(spreadsheet, "admin")
    if ws.cell(1, 1).value != "username":
        ws.clear()
        ws.append_row(["username", "password_hash"])
        ws.append_row(["admin", hash_password("admin@lalitha2024")])
        print("    → Admin login: password=admin@lalitha2024")

    # ── 3. settings ───────────────────────────────────────────────────────────
    ws = get_or_create_worksheet(spreadsheet, "settings")
    if ws.cell(1, 1).value != "key":
        ws.clear()
        ws.append_row(["key", "value", "description"])
        settings_data = [
            ["max_days_per_week",  "3",        "Maximum days per week a student can book"],
            ["available_days",     "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday", "Comma-separated available days"],
            ["min_hours",          "1",        "Minimum hours per session"],
            ["max_hours",          "4",        "Maximum hours per session"],
            ["time_slots",         "4:00 PM - 5:00 PM,5:00 PM - 6:00 PM,6:00 PM - 7:00 PM,7:00 PM - 8:00 PM", "Comma-separated time slots"],
            ["pricing_hourly",     "Contact for pricing", "Hourly plan price hint"],
            ["pricing_weekly",     "Contact for pricing", "Weekly plan price hint"],
            ["pricing_monthly",    "Contact for pricing", "Monthly plan price hint"],
            ["pricing_yearly",     "Contact for pricing", "Yearly plan price hint"],
            ["online_available",   "TRUE",     "Whether online mode is available"],
            ["offline_available",  "TRUE",     "Whether offline mode is available"],
            ["admin_password",     hash_password("admin@lalitha2024"), "Hashed admin password"],
        ]
        for row in settings_data:
            ws.append_row(row)
        print("    → Added admin settings (days, slots, pricing preferences)")

    # ── 4. bookings ───────────────────────────────────────────────────────────
    ws = get_or_create_worksheet(spreadsheet, "bookings")
    if ws.cell(1, 1).value != "id":
        ws.clear()
        ws.append_row(["id", "user_id", "full_name", "phone", "class", "school",
                        "mode", "basis", "quantity", "days_of_week", "time_slot",
                        "preferred_date", "subject", "status", "meet_link", "notes", "created_at"])
        # Sample pending booking
        ws.append_row([1, 1, "Arjun Kumar", "9876543210", "10", "Govt HSS",
                        "offline", "weekly", "3 days/week", "Monday,Wednesday,Friday",
                        "4:00 PM - 5:00 PM", "2024-02-01", "Mathematics", "pending",
                        "", "First time student", "2024-01-20 14:00:00"])
        print("    → Added bookings sheet with sample data")

    # ── 5. confirmed_bookings ─────────────────────────────────────────────────
    ws = get_or_create_worksheet(spreadsheet, "confirmed_bookings")
    if ws.cell(1, 1).value != "id":
        ws.clear()
        ws.append_row(["id", "user_id", "full_name", "phone", "class", "school",
                        "mode", "basis", "quantity", "days_of_week", "time_slot",
                        "preferred_date", "subject", "status", "meet_link", "notes", "created_at"])
        print("    → Created confirmed_bookings sheet")

    # ── 6. carousel_images ────────────────────────────────────────────────────
    ws = get_or_create_worksheet(spreadsheet, "carousel_images")
    if ws.cell(1, 1).value != "url":
        ws.clear()
        ws.append_row(["url", "caption", "order"])
        ws.append_row(["https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1200&q=80",
                        "Excellence in Mathematics Education", 1])
        ws.append_row(["https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1200&q=80",
                        "20 Years of Teaching Experience", 2])
        ws.append_row(["https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=1200&q=80",
                        "100% Board Exam Pass Record", 3])
        print("    → Added 3 carousel images")

    # ── 7. available_slots ────────────────────────────────────────────────────
    ws = get_or_create_worksheet(spreadsheet, "available_slots")
    if ws.cell(1, 1).value != "day":
        ws.clear()
        ws.append_row(["day", "time_slot", "is_available"])
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        slots = ["4:00 PM - 5:00 PM", "5:00 PM - 6:00 PM", "6:00 PM - 7:00 PM", "7:00 PM - 8:00 PM"]
        for day in days:
            for slot in slots:
                ws.append_row([day, slot, "TRUE"])
        # Sunday - only morning
        ws.append_row(["Sunday", "9:00 AM - 10:00 AM", "TRUE"])
        ws.append_row(["Sunday", "10:00 AM - 11:00 AM", "TRUE"])
        ws.append_row(["Sunday", "11:00 AM - 12:00 PM", "TRUE"])
        print("    → Added available slots (Mon-Sat: 4PM-8PM, Sun: 9AM-12PM)")

    # ── 8. pricing ────────────────────────────────────────────────────────────
    ws = get_or_create_worksheet(spreadsheet, "pricing")
    if ws.cell(1, 1).value != "basis":
        ws.clear()
        ws.append_row(["basis", "description", "price_hint", "highlight"])
        ws.append_row(["hourly",  "Pay per session. Flexible 1–4 hour sessions tailored to your pace.",
                        "Contact for pricing", "Flexible"])
        ws.append_row(["weekly",  "3 sessions per week. Build consistent study habits.",
                        "Contact for pricing", "Popular"])
        ws.append_row(["monthly", "Full month package with regular sessions. Best for board exam preparation.",
                        "Contact for pricing", "Best Value"])
        ws.append_row(["yearly",  "Annual commitment with maximum savings. Ideal for Class 10 & 12 students.",
                        "Contact for pricing", "Max Savings"])
        print("    → Added pricing plans")

    # ── 9. contact_info ───────────────────────────────────────────────────────
    ws = get_or_create_worksheet(spreadsheet, "contact_info")
    if ws.cell(1, 1).value != "key":
        ws.clear()
        ws.append_row(["key", "value"])
        contact_data = [
            ["phone",        "+91 8122231658"],
            ["email",        "lalithamurali1996@gmail.com"],
            ["address",      "89B, 15th Cross Street, Sivanandha Nagar (Senthil Nagar), Kolathur, Chennai - 600099"],
            ["whatsapp",     "918122231658"],
            ["instagram",    "https://instagram.com/"],
            ["youtube",      "https://youtube.com/"],
            ["maps_embed",   "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3885.7234567890!2d80.2090123!3d13.1189456!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3a5265ea0ed4a10b%3A0x5b3d6f17d9a9ef1f!2sKolathur%2C%20Chennai%2C%20Tamil%20Nadu%20600099!5e0!3m2!1sen!2sin!4v1234567890123!5m2!1sen!2sin"],
            ["teacher_name", "V. Lalitha M.Sc., B.Ed."],
            ["experience",   "20 Years"],
            ["subject",      "Mathematics"],
            ["school_name",  "Lalitha's Math Academy"],
        ]
        for row in contact_data:
            ws.append_row(row)
        print("    → Added contact info")

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║   ✅ All 9 sheets set up successfully!                  ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print("\nSheets created in your Google Spreadsheet:")
    print("  • users              — Student login/register data")
    print("  • admin              — Admin credentials")
    print("  • settings           — Admin preferences (slots, days, pricing)")
    print("  • bookings           — All booking requests")
    print("  • confirmed_bookings — Confirmed sessions")
    print("  • carousel_images    — Homepage carousel")
    print("  • available_slots    — Day/time slot availability")
    print("  • pricing            — Plan descriptions")
    print("  • contact_info       — Academy contact details")
    print("\nDemo Logins:")
    print("  Student: phone=9876543210, password=student123")
    print("  Admin:   password=admin@lalitha2024")
    print("\nNext steps:")
    print("  1. Review sheets at: https://docs.google.com/spreadsheets/d/" + SHEET_ID)
    print("  2. Run: python3 app.py")
    print("  3. Visit: http://localhost:5001\n")


if __name__ == "__main__":
    setup()
