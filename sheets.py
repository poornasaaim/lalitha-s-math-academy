"""
sheets.py — Google Sheets helper for Lalitha's Math Academy

DEMO MODE: When credentials.json is missing or empty, the app automatically
runs in demo mode with in-memory data. All features work for testing.
When you set up real Google Sheets credentials, it switches seamlessly.
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

SHEET_ID   = os.getenv("GOOGLE_SHEET_ID", "")
CREDS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# ─── Demo Mode Detection ─────────────────────────────────────────────────────
def _is_demo_mode() -> bool:
    """Returns True if credentials.json is missing or empty."""
    if not os.path.exists(CREDS_FILE):
        return True
    try:
        with open(CREDS_FILE) as f:
            data = json.load(f)
        return not data.get("type")           # real creds always have "type"
    except Exception:
        return True

DEMO_MODE = _is_demo_mode()
if DEMO_MODE:
    print("[INFO] sheets.py running in DEMO MODE — using in-memory sample data.")
    print("[INFO] To use real Google Sheets, add valid credentials.json and set GOOGLE_SHEET_ID in .env")

# ─── In-Memory Sample Data (Demo Mode) ───────────────────────────────────────
import hashlib as _hs
def _h(p): return _hs.sha256(p.encode()).hexdigest()

_DEMO_USERS = [
    {"id": 1, "full_name": "Arjun Kumar",  "class": "10", "school": "Govt Higher Secondary School",
     "address": "12, Anna Nagar, Chennai, 600040", "pincode": "600040",
     "phone": "9876543210", "password_hash": _h("student123"), "created_at": "2024-01-15 10:00:00"},
    {"id": 2, "full_name": "Priya Sharma", "class": "12", "school": "DAV Matriculation School",
     "address": "45, T.Nagar, Chennai, 600017",    "pincode": "600017",
     "phone": "9876543211", "password_hash": _h("student456"), "created_at": "2024-01-16 11:30:00"},
]

_DEMO_BOOKINGS = [
    {"id": 1, "user_id": 1, "full_name": "Arjun Kumar", "phone": "9876543210",
     "class": "10", "school": "Govt HSS", "mode": "offline", "basis": "weekly",
     "quantity": "3 days/week", "days_of_week": "Monday, Wednesday, Friday",
     "time_slot": "4:00 PM - 5:00 PM", "preferred_date": "2024-02-01",
     "subject": "Mathematics", "status": "pending", "meet_link": "", "created_at": "2024-01-20 14:00:00"},
]

_DEMO_CONFIRMED = []

_DEMO_NEXT_USER_ID    = [3]
_DEMO_NEXT_BOOKING_ID = [2]

_DEMO_SLOTS = [
    {"day": d, "time_slot": t, "is_available": "TRUE"}
    for d in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    for t in ["4:00 PM - 5:00 PM","5:00 PM - 6:00 PM","6:00 PM - 7:00 PM","7:00 PM - 8:00 PM"]
] + [
    {"day": "Sunday", "time_slot": t, "is_available": "TRUE"}
    for t in ["9:00 AM - 10:00 AM","10:00 AM - 11:00 AM","11:00 AM - 12:00 PM"]
]

_DEMO_CAROUSEL = [
    {"url": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1200&q=80",
     "caption": "Excellence in Mathematics Education", "order": 1},
    {"url": "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1200&q=80",
     "caption": "20 Years of Teaching Experience", "order": 2},
    {"url": "https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=1200&q=80",
     "caption": "100% Board Exam Pass Record", "order": 3},
]

_DEMO_PRICING = {
    "hourly":  {"basis":"hourly",   "description":"Pay per session. Maximum flexibility. 1-hour sessions tailored to your pace.",         "price_hint":"Contact for pricing","highlight":"Flexible"},
    "weekly":  {"basis":"weekly",   "description":"3 sessions per week (Mon/Wed/Fri or Tue/Thu/Sat). Build consistent study habits.",      "price_hint":"Contact for pricing","highlight":"Popular"},
    "monthly": {"basis":"monthly",  "description":"Full month package with 3 sessions/week. Best for board exam preparation.",             "price_hint":"Contact for pricing","highlight":"Best Value"},
    "yearly":  {"basis":"yearly",   "description":"Annual commitment with maximum savings. Ideal for Class 10 & 12 students.",             "price_hint":"Contact for pricing","highlight":"Max Savings"},
}

_DEMO_CONTACT = {
    "phone":        "+91 8122231658",
    "email":        "lalithamurali1996@gmail.com",
    "address":      "89B, 15th Cross Street, Sivanandha Nagar (Senthil Nagar), Kolathur, Chennai - 600099",
    "whatsapp":     "918122231658",
    "instagram":    "https://instagram.com/",
    "youtube":      "https://youtube.com/",
    "maps_embed":   "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3885.7234567890!2d80.2090123!3d13.1189456!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3a5265ea0ed4a10b%3A0x5b3d6f17d9a9ef1f!2sKolathur%2C%20Chennai%2C%20Tamil%20Nadu%20600099!5e0!3m2!1sen!2sin!4v1234567890123!5m2!1sen!2sin",
    "teacher_name": "V. Lalitha M.Sc., B.Ed.",
    "experience":   "20 Years",
    "subject":      "Mathematics",
    "school_name":  "Lalitha's Math Academy",
}

# ─── GSheets Client ──────────────────────────────────────────────────────────
_client      = None
_spreadsheet = None

def _get_client():
    global _client
    if _client is None:
        creds   = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
        _client = gspread.authorize(creds)
    return _client

def _get_sheet(sheet_name: str):
    global _spreadsheet
    client = _get_client()
    if _spreadsheet is None:
        _spreadsheet = client.open_by_key(SHEET_ID)
    return _spreadsheet.worksheet(sheet_name)

# ─── Password Hashing ─────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ════════════════════════════════════════════════════════════════════════════
# USERS
# ════════════════════════════════════════════════════════════════════════════

def get_user_by_phone(phone: str):
    if DEMO_MODE:
        return next((u for u in _DEMO_USERS if str(u["phone"]) == str(phone).strip()), None)
    try:
        ws = _get_sheet("users")
        for r in ws.get_all_records():
            if str(r.get("phone","")).strip() == str(phone).strip():
                return r
    except Exception as e:
        print(f"[GSheets Error] get_user_by_phone: {e}")
    return None


def register_user(full_name, cls, school, address, pincode, phone, password):
    """Add new user. Returns (True, msg) or (False, error)."""
    phone = str(phone).strip()
    if get_user_by_phone(phone):
        return False, "Phone number already registered."

    if DEMO_MODE:
        uid = _DEMO_NEXT_USER_ID[0]
        _DEMO_NEXT_USER_ID[0] += 1
        _DEMO_USERS.append({
            "id": uid, "full_name": full_name, "class": cls, "school": school,
            "address": address, "pincode": pincode, "phone": phone,
            "password_hash": hash_password(password),
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        return True, "Registration successful."

    try:
        ws  = _get_sheet("users")
        uid = len(ws.get_all_records()) + 1
        ws.append_row([
            uid, full_name, cls, school, address, pincode, phone,
            hash_password(password),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ])
        return True, "Registration successful."
    except Exception as e:
        return False, str(e)


def authenticate_user(phone, password):
    user = get_user_by_phone(phone)
    if user and user.get("password_hash") == hash_password(password):
        return user
    return None


# ════════════════════════════════════════════════════════════════════════════
# BOOKINGS
# ════════════════════════════════════════════════════════════════════════════

def create_booking(data: dict):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if DEMO_MODE:
        bid = _DEMO_NEXT_BOOKING_ID[0]
        _DEMO_NEXT_BOOKING_ID[0] += 1
        _DEMO_BOOKINGS.append({
            "id": bid,
            "user_id":        data.get("user_id",""),
            "full_name":      data.get("full_name",""),
            "phone":          data.get("phone",""),
            "class":          data.get("class",""),
            "school":         data.get("school",""),
            "mode":           data.get("mode","offline"),
            "basis":          data.get("basis","hourly"),
            "quantity":       data.get("quantity",""),
            "days_of_week":   data.get("days_of_week",""),
            "time_slot":      data.get("time_slot",""),
            "preferred_date": data.get("preferred_date",""),
            "subject":        "Mathematics",
            "status":         "pending",
            "meet_link":      "",
            "created_at":     now,
        })
        return bid

    try:
        ws  = _get_sheet("bookings")
        bid = len(ws.get_all_records()) + 1
        ws.append_row([
            bid,
            data.get("user_id",""),   data.get("full_name",""),
            data.get("phone",""),     data.get("class",""),
            data.get("school",""),    data.get("mode","offline"),
            data.get("basis","hourly"), data.get("quantity",""),
            data.get("days_of_week",""), data.get("time_slot",""),
            data.get("preferred_date",""), "Mathematics",
            "pending", "", now,
        ])
        return bid
    except Exception as e:
        print(f"[Booking Error] {e}")
        return None


def get_all_bookings():
    if DEMO_MODE:
        return list(_DEMO_BOOKINGS)
    try:
        return _get_sheet("bookings").get_all_records()
    except Exception:
        return []


def get_pending_bookings():
    return [b for b in get_all_bookings() if b.get("status","") == "pending"]


def get_confirmed_bookings():
    if DEMO_MODE:
        return list(_DEMO_CONFIRMED)
    try:
        return [b for b in _get_sheet("bookings").get_all_records() if b.get("status") == "confirmed"]
    except Exception:
        return []


def confirm_booking(booking_id, meet_link=""):
    booking_id = str(booking_id)

    if DEMO_MODE:
        for b in _DEMO_BOOKINGS:
            if str(b["id"]) == booking_id:
                b["status"]    = "confirmed"
                b["meet_link"] = meet_link
                _DEMO_CONFIRMED.append(dict(b))
                _DEMO_BOOKINGS.remove(b)
                return True
        return False

    try:
        ws      = _get_sheet("bookings")
        records = ws.get_all_records()
        headers = ws.row_values(1)
        s_col   = headers.index("status")    + 1
        m_col   = headers.index("meet_link") + 1
        for i, r in enumerate(records, start=2):
            if str(r.get("id","")) == booking_id:
                ws.update_cell(i, s_col, "confirmed")
                if meet_link:
                    ws.update_cell(i, m_col, meet_link)
                # copy to confirmed_bookings
                try:
                    cws = _get_sheet("confirmed_bookings")
                    row = list(r.values())
                    row[headers.index("status")]    = "confirmed"
                    row[headers.index("meet_link")] = meet_link
                    cws.append_row(row)
                except Exception:
                    pass
                return True
    except Exception as e:
        print(f"[Confirm Error] {e}")
    return False


# ════════════════════════════════════════════════════════════════════════════
# ADMIN
# ════════════════════════════════════════════════════════════════════════════

def authenticate_admin(password: str) -> bool:
    # Always try env fallback first for reliability
    fallback = os.getenv("ADMIN_PASSWORD", "admin@lalitha2024")
    if password == fallback:
        return True

    if DEMO_MODE:
        return password in ("admin@lalitha2024", "admin123")

    try:
        ws      = _get_sheet("admin")
        records = ws.get_all_records()
        if records:
            stored = records[0].get("password_hash","")
            return stored == hash_password(password)
    except Exception:
        pass
    return False


# ════════════════════════════════════════════════════════════════════════════
# CAROUSEL
# ════════════════════════════════════════════════════════════════════════════

def get_carousel_images():
    if DEMO_MODE:
        return sorted(_DEMO_CAROUSEL, key=lambda x: int(x.get("order",99)))
    try:
        ws = _get_sheet("carousel_images")
        return sorted(ws.get_all_records(), key=lambda x: int(x.get("order",99)))
    except Exception:
        return _DEMO_CAROUSEL


def update_carousel_images(images: list):
    if DEMO_MODE:
        _DEMO_CAROUSEL.clear()
        _DEMO_CAROUSEL.extend(images)
        return True
    try:
        ws = _get_sheet("carousel_images")
        ws.clear()
        ws.append_row(["url","caption","order"])
        for i, img in enumerate(images, 1):
            ws.append_row([img.get("url",""), img.get("caption",""), i])
        return True
    except Exception:
        return False


# ════════════════════════════════════════════════════════════════════════════
# AVAILABLE SLOTS
# ════════════════════════════════════════════════════════════════════════════

def get_available_slots():
    if DEMO_MODE:
        return list(_DEMO_SLOTS)
    try:
        return _get_sheet("available_slots").get_all_records()
    except Exception:
        return list(_DEMO_SLOTS)


def set_all_slots(slots: list):
    if DEMO_MODE:
        _DEMO_SLOTS.clear()
        _DEMO_SLOTS.extend(slots)
        return True
    try:
        ws = _get_sheet("available_slots")
        ws.clear()
        ws.append_row(["day","time_slot","is_available"])
        for s in slots:
            ws.append_row([s["day"], s["time_slot"], s["is_available"]])
        return True
    except Exception:
        return False


def update_slot_availability(day: str, time_slot: str, is_available: bool):
    val = "TRUE" if is_available else "FALSE"
    if DEMO_MODE:
        for s in _DEMO_SLOTS:
            if s["day"] == day and s["time_slot"] == time_slot:
                s["is_available"] = val
                return True
        _DEMO_SLOTS.append({"day": day, "time_slot": time_slot, "is_available": val})
        return True
    try:
        ws      = _get_sheet("available_slots")
        records = ws.get_all_records()
        headers = ws.row_values(1)
        a_col   = headers.index("is_available") + 1
        for i, r in enumerate(records, start=2):
            if r.get("day") == day and r.get("time_slot") == time_slot:
                ws.update_cell(i, a_col, val)
                return True
        ws.append_row([day, time_slot, val])
        return True
    except Exception as e:
        print(f"[Slot Error] {e}")
        return False


# ════════════════════════════════════════════════════════════════════════════
# PRICING
# ════════════════════════════════════════════════════════════════════════════

def get_pricing():
    if DEMO_MODE:
        return _DEMO_PRICING
    try:
        ws = _get_sheet("pricing")
        return {r["basis"]: r for r in ws.get_all_records()}
    except Exception:
        return _DEMO_PRICING


# ════════════════════════════════════════════════════════════════════════════
# CONTACT INFO
# ════════════════════════════════════════════════════════════════════════════

def get_contact_info():
    if DEMO_MODE:
        return _DEMO_CONTACT
    try:
        ws = _get_sheet("contact_info")
        return {r["key"]: r["value"] for r in ws.get_all_records()}
    except Exception:
        return _DEMO_CONTACT
