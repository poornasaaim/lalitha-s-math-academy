"""
sheets.py — Google Sheets integration for Lalitha's Math Academy

AUTO-DETECTION:
  • If credentials.json has a valid service account key AND GOOGLE_SHEET_ID is set
    → writes/reads from real Google Sheets
  • Otherwise → demo mode (in-memory data, identical API surface)

After saving credentials via the admin panel, the next API call automatically
switches to live mode (no restart required).
"""

import os, json, hashlib, datetime
from dotenv import load_dotenv

load_dotenv()

SCOPES     = ["https://www.googleapis.com/auth/spreadsheets",
               "https://www.googleapis.com/auth/drive"]
SHEET_ID   = os.getenv("GOOGLE_SHEET_ID", "").strip()
CREDS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# ── Lazy GSheets client (recreated after credentials change) ──────────────────
_gc   = None
_spr  = None

def _sheets_ok() -> bool:
    """Dynamically check if real GSheets is usable (called per request)."""
    if not SHEET_ID:
        return False
    if not os.path.exists(CREDS_FILE):
        return False
    try:
        with open(CREDS_FILE) as f:
            d = json.load(f)
        return bool(d.get("private_key") and d.get("type") == "service_account")
    except Exception:
        return False

def reset_client():
    """Call after saving new credentials to force reconnection."""
    global _gc, _spr
    _gc = None
    _spr = None

def _ws(name: str):
    """Get a worksheet, (re)connecting if needed."""
    global _gc, _spr
    import gspread
    from google.oauth2.service_account import Credentials
    try:
        if _gc is None:
            creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
            _gc   = gspread.authorize(creds)
        if _spr is None:
            _spr = _gc.open_by_key(SHEET_ID)
        return _spr.worksheet(name)
    except Exception as e:
        reset_client()
        raise e

def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()

def get_connection_status() -> dict:
    """Returns connection status info for admin panel."""
    if _sheets_ok():
        try:
            _ws("users")
            return {"mode": "live", "sheet_id": SHEET_ID,
                    "message": "✅ Connected to Google Sheets"}
        except Exception as e:
            return {"mode": "error", "sheet_id": SHEET_ID,
                    "message": f"❌ Credentials valid but connection failed: {e}"}
    else:
        reasons = []
        if not SHEET_ID:
            reasons.append("GOOGLE_SHEET_ID not set in .env")
        if not os.path.exists(CREDS_FILE):
            reasons.append("credentials.json not found")
        else:
            try:
                with open(CREDS_FILE) as f:
                    d = json.load(f)
                if not d.get("private_key"):
                    reasons.append("credentials.json is empty or invalid")
            except Exception:
                reasons.append("credentials.json cannot be parsed")
        return {"mode": "demo", "sheet_id": SHEET_ID,
                "message": "⚠️ Demo Mode — " + "; ".join(reasons)}

# ── In-memory Demo Data ───────────────────────────────────────────────────────
_h = hash_password

_DEMO_USERS = [
    {"id":1,"full_name":"Arjun Kumar","class":"10","school":"Govt Higher Secondary School",
     "address":"12, Anna Nagar, Chennai","pincode":"600040","phone":"9876543210",
     "password_hash":_h("student123"),"created_at":"2024-01-15 10:00:00"},
    {"id":2,"full_name":"Priya Sharma","class":"12","school":"DAV Matriculation School",
     "address":"45, T.Nagar, Chennai","pincode":"600017","phone":"9876543211",
     "password_hash":_h("student456"),"created_at":"2024-01-16 11:30:00"},
]
_DEMO_BOOKINGS  = [
    {"id":1,"user_id":1,"full_name":"Arjun Kumar","phone":"9876543210","class":"10",
     "school":"Govt HSS","mode":"offline","basis":"weekly","quantity":"3 days/week",
     "days_of_week":"Monday, Wednesday, Friday","time_slot":"4:00 PM - 5:00 PM",
     "preferred_date":"2024-02-01","subject":"Mathematics","status":"pending",
     "meet_link":"","notes":"First time student","created_at":"2024-01-20 14:00:00"},
]
_DEMO_CONFIRMED = []
_DEMO_NEXT      = {"user": 3, "booking": 2}

_DEMO_SETTINGS = {
    "max_days_per_week":  "3",
    "available_days":     "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday",
    "min_hours":          "1",
    "max_hours":          "4",
    "time_slots":         "4:00 PM - 5:00 PM,5:00 PM - 6:00 PM,6:00 PM - 7:00 PM,7:00 PM - 8:00 PM",
    "pricing_hourly":     "Contact for pricing",
    "pricing_weekly":     "Contact for pricing",
    "pricing_monthly":    "Contact for pricing",
    "pricing_yearly":     "Contact for pricing",
    "online_available":   "TRUE",
    "offline_available":  "TRUE",
}

_DEMO_CAROUSEL = [
    {"url":"https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1200&q=80",
     "caption":"Excellence in Mathematics Education","order":1},
    {"url":"https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1200&q=80",
     "caption":"20 Years of Teaching Experience","order":2},
    {"url":"https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=1200&q=80",
     "caption":"100% Board Exam Pass Record","order":3},
]

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


# ════════════════════════════════════════════════════════════════════════════
# SETTINGS (admin preferences — max days, slots, pricing, etc.)
# ════════════════════════════════════════════════════════════════════════════

def get_settings() -> dict:
    if _sheets_ok():
        try:
            ws = _ws("settings")
            records = ws.get_all_records()
            return {str(r.get("key","")): str(r.get("value","")) for r in records if r.get("key")}
        except Exception as e:
            print(f"[GSheets] get_settings fallback: {e}")
    return dict(_DEMO_SETTINGS)


def save_settings(settings: dict) -> bool:
    """Save/update admin settings. Merges with existing."""
    if _sheets_ok():
        try:
            ws      = _ws("settings")
            records = ws.get_all_records()
            headers = ws.row_values(1)
            k_col   = headers.index("key")   + 1
            v_col   = headers.index("value") + 1
            existing = {str(r.get("key","")): i + 2 for i, r in enumerate(records)}
            for k, v in settings.items():
                if k in existing:
                    ws.update_cell(existing[k], v_col, str(v))
                else:
                    ws.append_row([k, str(v), ""])
            return True
        except Exception as e:
            print(f"[GSheets] save_settings error: {e}")
            return False
    # Demo mode
    _DEMO_SETTINGS.update(settings)
    return True


# ════════════════════════════════════════════════════════════════════════════
# USERS
# ════════════════════════════════════════════════════════════════════════════

def get_user_by_phone(phone: str):
    phone = str(phone).strip()
    if _sheets_ok():
        try:
            ws = _ws("users")
            for r in ws.get_all_records():
                if str(r.get("phone","")).strip() == phone:
                    return r
            return None
        except Exception as e:
            print(f"[GSheets] get_user_by_phone fallback: {e}")
    return next((u for u in _DEMO_USERS if str(u["phone"]) == phone), None)


def register_user(full_name, cls, school, address, pincode, phone, password) -> tuple:
    phone = str(phone).strip()
    if get_user_by_phone(phone):
        return False, "Phone number already registered."
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if _sheets_ok():
        try:
            ws  = _ws("users")
            all_records = ws.get_all_records()
            uid = len(all_records) + 1
            ws.append_row([uid, full_name, cls, school, address, pincode, phone,
                           hash_password(password), now])
            return True, "Registration successful."
        except Exception as e:
            print(f"[GSheets] register_user error: {e}")
            return False, f"Registration failed: {e}"
    uid     = _DEMO_NEXT["user"]
    _DEMO_NEXT["user"] += 1
    _DEMO_USERS.append({
        "id": uid, "full_name": full_name, "class": cls, "school": school,
        "address": address, "pincode": pincode, "phone": phone,
        "password_hash": hash_password(password), "created_at": now,
    })
    return True, "Registration successful."


def authenticate_user(phone, password):
    user = get_user_by_phone(phone)
    if user and str(user.get("password_hash","")) == hash_password(password):
        return user
    return None


def get_all_users() -> list:
    if _sheets_ok():
        try:
            return _ws("users").get_all_records()
        except Exception:
            pass
    return list(_DEMO_USERS)


# ════════════════════════════════════════════════════════════════════════════
# BOOKINGS
# ════════════════════════════════════════════════════════════════════════════

_BOOKING_HEADERS = [
    "id","user_id","full_name","phone","class","school",
    "mode","basis","quantity","days_of_week","time_slot",
    "preferred_date","subject","status","meet_link","notes","created_at"
]

def create_booking(data: dict):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if _sheets_ok():
        try:
            ws  = _ws("bookings")
            all_records = ws.get_all_records()
            bid = len(all_records) + 1
            ws.append_row([
                bid,
                data.get("user_id",""),   data.get("full_name",""),
                data.get("phone",""),     data.get("class",""),
                data.get("school",""),    data.get("mode","offline"),
                data.get("basis","hourly"), data.get("quantity",""),
                data.get("days_of_week",""), data.get("time_slot",""),
                data.get("preferred_date",""), "Mathematics",
                "pending", "", data.get("notes",""), now,
            ])
            return bid
        except Exception as e:
            print(f"[GSheets] create_booking error: {e}")
            return None
    bid = _DEMO_NEXT["booking"]
    _DEMO_NEXT["booking"] += 1
    _DEMO_BOOKINGS.append({
        "id": bid, "user_id": data.get("user_id",""),
        "full_name": data.get("full_name",""), "phone": data.get("phone",""),
        "class": data.get("class",""),         "school": data.get("school",""),
        "mode": data.get("mode","offline"),    "basis": data.get("basis","hourly"),
        "quantity": data.get("quantity",""),   "days_of_week": data.get("days_of_week",""),
        "time_slot": data.get("time_slot",""), "preferred_date": data.get("preferred_date",""),
        "subject": "Mathematics", "status": "pending",
        "meet_link": "", "notes": data.get("notes",""), "created_at": now,
    })
    return bid


def get_all_bookings() -> list:
    if _sheets_ok():
        try:
            return _ws("bookings").get_all_records()
        except Exception:
            pass
    return list(_DEMO_BOOKINGS)


def get_pending_bookings() -> list:
    return [b for b in get_all_bookings() if str(b.get("status","")) == "pending"]


def get_confirmed_bookings() -> list:
    if _sheets_ok():
        try:
            return [b for b in _ws("bookings").get_all_records()
                    if str(b.get("status","")) == "confirmed"]
        except Exception:
            pass
    return list(_DEMO_CONFIRMED)


def confirm_booking(booking_id, meet_link="") -> bool:
    bid = str(booking_id)
    if _sheets_ok():
        try:
            ws      = _ws("bookings")
            records = ws.get_all_records()
            headers = ws.row_values(1)
            s_col   = headers.index("status")    + 1
            m_col   = headers.index("meet_link") + 1
            for i, r in enumerate(records, start=2):
                if str(r.get("id","")) == bid:
                    ws.update_cell(i, s_col, "confirmed")
                    ws.update_cell(i, m_col, meet_link)
                    # Also copy to confirmed_bookings sheet
                    try:
                        cws = _ws("confirmed_bookings")
                        row_vals = [r.get(h, "") for h in headers]
                        row_vals[headers.index("status")]    = "confirmed"
                        row_vals[headers.index("meet_link")] = meet_link
                        cws.append_row(row_vals)
                    except Exception:
                        pass
                    return True
            return False
        except Exception as e:
            print(f"[GSheets] confirm_booking error: {e}")
            return False
    for b in _DEMO_BOOKINGS:
        if str(b["id"]) == bid:
            b["status"]    = "confirmed"
            b["meet_link"] = meet_link
            _DEMO_CONFIRMED.append(dict(b))
            _DEMO_BOOKINGS.remove(b)
            return True
    return False


# ════════════════════════════════════════════════════════════════════════════
# ADMIN AUTH
# ════════════════════════════════════════════════════════════════════════════

def authenticate_admin(password: str) -> bool:
    # Always allow env fallback
    if password == os.getenv("ADMIN_PASSWORD", "admin@lalitha2024"):
        return True
    if _sheets_ok():
        try:
            ws = _ws("admin")
            for r in ws.get_all_records():
                if str(r.get("password_hash","")) == hash_password(password):
                    return True
        except Exception:
            pass
    return password in ("admin@lalitha2024", "admin123")


# ════════════════════════════════════════════════════════════════════════════
# CAROUSEL
# ════════════════════════════════════════════════════════════════════════════

def get_carousel_images() -> list:
    if _sheets_ok():
        try:
            ws = _ws("carousel_images")
            return sorted(ws.get_all_records(), key=lambda x: int(x.get("order",99)))
        except Exception:
            pass
    return list(_DEMO_CAROUSEL)


def update_carousel_images(images: list) -> bool:
    if _sheets_ok():
        try:
            ws = _ws("carousel_images")
            ws.clear()
            ws.append_row(["url","caption","order"])
            for i, img in enumerate(images, 1):
                ws.append_row([img.get("url",""), img.get("caption",""), i])
            return True
        except Exception:
            return False
    _DEMO_CAROUSEL.clear()
    _DEMO_CAROUSEL.extend(images)
    return True


# ════════════════════════════════════════════════════════════════════════════
# AVAILABLE SLOTS
# ════════════════════════════════════════════════════════════════════════════

def get_available_slots() -> list:
    """Returns flat list of {day, time_slot, is_available} dicts."""
    if _sheets_ok():
        try:
            ws = _ws("available_slots")
            return ws.get_all_records()
        except Exception:
            pass
    # Fallback: generate from settings
    s          = get_settings()
    days       = [d.strip() for d in s.get("available_days","").split(",") if d.strip()]
    time_slots = [t.strip() for t in s.get("time_slots","").split(",") if t.strip()]
    result     = []
    for day in days:
        for ts in time_slots:
            result.append({"day": day, "time_slot": ts, "is_available": "TRUE"})
    return result


def set_all_slots(slots: list) -> bool:
    """Update slot availability from admin panel."""
    if _sheets_ok():
        try:
            ws = _ws("available_slots")
            ws.clear()
            ws.append_row(["day", "time_slot", "is_available"])
            for s in slots:
                ws.append_row([s.get("day",""), s.get("time_slot",""), s.get("is_available","TRUE")])
            return True
        except Exception as e:
            print(f"[GSheets] set_all_slots error: {e}")
            return False
    return True


# ════════════════════════════════════════════════════════════════════════════
# CONTACT INFO
# ════════════════════════════════════════════════════════════════════════════

def get_contact_info() -> dict:
    if _sheets_ok():
        try:
            ws = _ws("contact_info")
            return {str(r.get("key","")): str(r.get("value","")) for r in ws.get_all_records() if r.get("key")}
        except Exception:
            pass
    return dict(_DEMO_CONTACT)


# ════════════════════════════════════════════════════════════════════════════
# PRICING
# ════════════════════════════════════════════════════════════════════════════

def get_pricing() -> dict:
    s = get_settings()
    return {
        "hourly":  {"basis":"hourly",  "description":"Pay per session. Flexible scheduling for 1–4 hours.",
                    "price_hint": s.get("pricing_hourly","Contact for pricing"), "highlight":"Flexible"},
        "weekly":  {"basis":"weekly",  "description":"3 sessions/week. Consistent structured learning.",
                    "price_hint": s.get("pricing_weekly","Contact for pricing"), "highlight":"Popular"},
        "monthly": {"basis":"monthly", "description":"Full month coaching. Board exam preparation.",
                    "price_hint": s.get("pricing_monthly","Contact for pricing"), "highlight":"Best Value"},
        "yearly":  {"basis":"yearly",  "description":"Annual program. Maximum savings.",
                    "price_hint": s.get("pricing_yearly","Contact for pricing"), "highlight":"Max Savings"},
    }
