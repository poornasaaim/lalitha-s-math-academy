"""
sheets.py — Google Sheets helper for Lalitha's Math Academy
All database operations go through this module.
"""

import os
import json
import hashlib
import datetime
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
CREDS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# ─── Sheet name constants ────────────────────────────────────────────────────
SHEET_USERS          = "users"
SHEET_BOOKINGS       = "bookings"
SHEET_ADMIN          = "admin"
SHEET_CAROUSEL       = "carousel_images"
SHEET_SLOTS          = "available_slots"
SHEET_PRICING        = "pricing"
SHEET_CONTACT        = "contact_info"
SHEET_CONFIRMED      = "confirmed_bookings"

_client = None
_spreadsheet = None


def _get_client():
    global _client
    if _client is None:
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
        _client = gspread.authorize(creds)
    return _client


def _get_sheet(sheet_name: str):
    global _spreadsheet
    client = _get_client()
    if _spreadsheet is None:
        _spreadsheet = client.open_by_key(SHEET_ID)
    return _spreadsheet.worksheet(sheet_name)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ─── Users ───────────────────────────────────────────────────────────────────

def get_user_by_phone(phone: str):
    """Return user row dict or None."""
    try:
        ws = _get_sheet(SHEET_USERS)
        records = ws.get_all_records()
        for r in records:
            if str(r.get("phone", "")).strip() == str(phone).strip():
                return r
    except Exception:
        pass
    return None


def register_user(full_name, cls, school, address, pincode, phone, password):
    """Add new user. Returns (True, msg) or (False, error)."""
    try:
        if get_user_by_phone(phone):
            return False, "Phone number already registered."
        ws = _get_sheet(SHEET_USERS)
        records = ws.get_all_records()
        user_id = len(records) + 1
        ws.append_row([
            user_id, full_name, cls, school, address, pincode, phone,
            hash_password(password),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        return True, "Registration successful."
    except Exception as e:
        return False, str(e)


def authenticate_user(phone, password):
    """Return user dict if credentials match, else None."""
    user = get_user_by_phone(phone)
    if user and user.get("password_hash") == hash_password(password):
        return user
    return None


# ─── Bookings ────────────────────────────────────────────────────────────────

def create_booking(data: dict):
    """Insert a new booking row. Returns booking_id or None."""
    try:
        ws = _get_sheet(SHEET_BOOKINGS)
        records = ws.get_all_records()
        booking_id = len(records) + 1
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws.append_row([
            booking_id,
            data.get("user_id", ""),
            data.get("full_name", ""),
            data.get("phone", ""),
            data.get("class", ""),
            data.get("school", ""),
            data.get("mode", "offline"),        # offline / online
            data.get("basis", "hourly"),         # hourly/weekly/monthly/yearly
            data.get("quantity", ""),            # hours / days / weeks / months
            data.get("days_of_week", ""),        # Mon,Wed,Fri etc.
            data.get("time_slot", ""),
            data.get("preferred_date", ""),
            data.get("subject", "Mathematics"),
            "pending",                           # status
            "",                                  # meet_link (filled by admin)
            now
        ])
        return booking_id
    except Exception as e:
        print(f"[Booking Error] {e}")
        return None


def get_all_bookings():
    """Return all bookings from the bookings sheet."""
    try:
        ws = _get_sheet(SHEET_BOOKINGS)
        return ws.get_all_records()
    except Exception:
        return []


def get_booking_by_id(booking_id):
    try:
        ws = _get_sheet(SHEET_BOOKINGS)
        records = ws.get_all_records()
        for i, r in enumerate(records, start=2):
            if str(r.get("id", "")) == str(booking_id):
                return r, i   # row_index is 1-based, header is row 1
        return None, None
    except Exception:
        return None, None


def confirm_booking(booking_id, meet_link=""):
    """Mark booking as confirmed and optionally add meet link."""
    try:
        ws = _get_sheet(SHEET_BOOKINGS)
        records = ws.get_all_records()
        headers = ws.row_values(1)
        status_col = headers.index("status") + 1
        meet_col   = headers.index("meet_link") + 1

        for i, r in enumerate(records, start=2):
            if str(r.get("id", "")) == str(booking_id):
                ws.update_cell(i, status_col, "confirmed")
                if meet_link:
                    ws.update_cell(i, meet_col, meet_link)
                # Also copy to confirmed_bookings sheet
                confirmed_ws = _get_sheet(SHEET_CONFIRMED)
                row_data = list(r.values())
                row_data[headers.index("status")]    = "confirmed"
                row_data[headers.index("meet_link")] = meet_link
                confirmed_ws.append_row(row_data)
                return True
    except Exception as e:
        print(f"[Confirm Booking Error] {e}")
    return False


def get_pending_bookings():
    try:
        ws = _get_sheet(SHEET_BOOKINGS)
        records = ws.get_all_records()
        return [r for r in records if r.get("status", "") == "pending"]
    except Exception:
        return []


def get_confirmed_bookings():
    try:
        ws = _get_sheet(SHEET_BOOKINGS)
        records = ws.get_all_records()
        return [r for r in records if r.get("status", "") == "confirmed"]
    except Exception:
        return []


# ─── Admin ───────────────────────────────────────────────────────────────────

def authenticate_admin(password: str) -> bool:
    try:
        ws = _get_sheet(SHEET_ADMIN)
        records = ws.get_all_records()
        if records:
            stored = records[0].get("password_hash", "")
            return stored == hash_password(password)
    except Exception:
        pass
    # Fallback to env variable
    fallback = os.getenv("ADMIN_PASSWORD", "admin123")
    return password == fallback


# ─── Carousel Images ─────────────────────────────────────────────────────────

def get_carousel_images():
    try:
        ws = _get_sheet(SHEET_CAROUSEL)
        records = ws.get_all_records()
        return sorted(records, key=lambda x: int(x.get("order", 99)))
    except Exception:
        return [
            {"url": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1200", "caption": "Expert Mathematics Tuition"},
            {"url": "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1200", "caption": "Learn with Passion"},
            {"url": "https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=1200", "caption": "20 Years of Excellence"},
        ]


def update_carousel_images(images: list):
    """Replace all carousel images."""
    try:
        ws = _get_sheet(SHEET_CAROUSEL)
        ws.clear()
        ws.append_row(["url", "caption", "order"])
        for i, img in enumerate(images, start=1):
            ws.append_row([img.get("url", ""), img.get("caption", ""), i])
        return True
    except Exception:
        return False


# ─── Available Slots ─────────────────────────────────────────────────────────

def get_available_slots():
    try:
        ws = _get_sheet(SHEET_SLOTS)
        records = ws.get_all_records()
        return records
    except Exception:
        return []


def update_slot_availability(day: str, time_slot: str, is_available: bool):
    try:
        ws = _get_sheet(SHEET_SLOTS)
        records = ws.get_all_records()
        headers = ws.row_values(1)
        avail_col = headers.index("is_available") + 1
        for i, r in enumerate(records, start=2):
            if r.get("day") == day and r.get("time_slot") == time_slot:
                ws.update_cell(i, avail_col, "TRUE" if is_available else "FALSE")
                return True
        # If slot not found, add it
        ws.append_row([day, time_slot, "TRUE" if is_available else "FALSE"])
        return True
    except Exception as e:
        print(f"[Slot Error] {e}")
        return False


def set_all_slots(slots: list):
    """Replace all slot rows. slots = [{'day': 'Monday', 'time_slot': '4:00 PM - 5:00 PM', 'is_available': 'TRUE'}]"""
    try:
        ws = _get_sheet(SHEET_SLOTS)
        ws.clear()
        ws.append_row(["day", "time_slot", "is_available"])
        for s in slots:
            ws.append_row([s["day"], s["time_slot"], s["is_available"]])
        return True
    except Exception:
        return False


# ─── Pricing ─────────────────────────────────────────────────────────────────

def get_pricing():
    try:
        ws = _get_sheet(SHEET_PRICING)
        records = ws.get_all_records()
        return {r["basis"]: r for r in records}
    except Exception:
        return {
            "hourly":  {"basis": "hourly",   "description": "1-hour session, flexible scheduling", "price_hint": "Ask for pricing"},
            "weekly":  {"basis": "weekly",   "description": "3 sessions per week, consistent learning", "price_hint": "Ask for pricing"},
            "monthly": {"basis": "monthly",  "description": "Full month package, best value", "price_hint": "Ask for pricing"},
            "yearly":  {"basis": "yearly",   "description": "Annual package, maximum savings", "price_hint": "Ask for pricing"},
        }


# ─── Contact Info ────────────────────────────────────────────────────────────

def get_contact_info():
    try:
        ws = _get_sheet(SHEET_CONTACT)
        records = ws.get_all_records()
        return {r["key"]: r["value"] for r in records}
    except Exception:
        return {
            "phone":      "+91 9841260450",
            "email":      "lalithamurali1996@gmail.com",
            "address":    "89B, 15th Cross Street, Sivanandha Nagar (Senthil Nagar), Kolathur, Chennai - 600099",
            "whatsapp":   "919841260450",
            "instagram":  "#",
            "youtube":    "#",
            "maps_embed": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3886.4!2d80.2!3d13.1!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMTPCsDA2JzAwLjAiTiA4MMKwMTInMDAuMCJF!5e0!3m2!1sen!2sin!4v1234567890",
        }
