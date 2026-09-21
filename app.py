"""
app.py — Flask application for Lalitha's Math Academy Booking Platform
"""

import os
import json
import urllib.parse
import requests
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, flash
)
from dotenv import load_dotenv
import sheets

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "lalitha-math-academy-secret-2024")
app.config["SESSION_PERMANENT"] = False

ACADEMY_WA = os.getenv("ACADEMY_WHATSAPP", "919841260450")
CALLMEBOT_KEY = os.getenv("CALLMEBOT_API_KEY", "")


# ─── Decorators ──────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


# ─── Helpers ─────────────────────────────────────────────────────────────────

def build_whatsapp_message(booking: dict) -> str:
    """Build pre-filled WhatsApp message for booking confirmation."""
    lines = [
        "🎓 *Lalitha's Math Academy — New Booking Request*",
        "",
        f"👤 *Student:* {booking.get('full_name', '')}",
        f"📱 *Phone:* {booking.get('phone', '')}",
        f"🏫 *Class:* {booking.get('class', '')} | *School:* {booking.get('school', '')}",
        "",
        f"📚 *Subject:* Mathematics",
        f"📋 *Plan:* {str(booking.get('basis', '')).capitalize()} Basis",
        f"⏱ *Duration:* {booking.get('quantity', '')}",
        f"📅 *Days:* {booking.get('days_of_week', '')}",
        f"🕐 *Time Slot:* {booking.get('time_slot', '')}",
        f"📆 *Preferred Start:* {booking.get('preferred_date', '')}",
        f"🖥 *Mode:* {str(booking.get('mode', 'offline')).capitalize()}",
        "",
        "Please confirm this booking and share the fee details. Thank you! 🙏"
    ]
    return "\n".join(lines)


def send_callmebot_message(phone: str, message: str) -> bool:
    """Send WhatsApp message via CallMeBot API (free)."""
    if not CALLMEBOT_KEY:
        return False
    try:
        encoded = urllib.parse.quote(message)
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded}&apikey={CALLMEBOT_KEY}"
        r = requests.get(url, timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def whatsapp_link(message: str, phone: str = ACADEMY_WA) -> str:
    """Generate wa.me link with pre-filled message."""
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{phone}?text={encoded}"


# ─── Public Routes ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    carousel   = sheets.get_carousel_images()
    pricing    = sheets.get_pricing()
    contact    = sheets.get_contact_info()
    is_logged  = "user" in session
    return render_template("index.html",
                           carousel=carousel,
                           pricing=pricing,
                           contact=contact,
                           is_logged_in=is_logged)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        phone    = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()
        user = sheets.authenticate_user(phone, password)
        if user:
            session["user"] = dict(user)
            flash(f"Welcome back, {user.get('full_name', '')}! 🎉", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid phone number or password. Please try again.", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        cls       = request.form.get("class_", "").strip()
        school    = request.form.get("school", "").strip()
        address   = request.form.get("address", "").strip()
        pincode   = request.form.get("pincode", "").strip()
        phone     = request.form.get("phone", "").strip()
        password  = request.form.get("password", "").strip()
        confirm   = request.form.get("confirm_password", "").strip()

        if not all([full_name, cls, school, address, pincode, phone, password]):
            flash("All fields are required.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif len(phone) != 10 or not phone.isdigit():
            flash("Enter a valid 10-digit phone number.", "error")
        else:
            ok, msg = sheets.register_user(full_name, cls, school, address, pincode, phone, password)
            if ok:
                flash("Registration successful! Please login.", "success")
                return redirect(url_for("login"))
            else:
                flash(msg, "error")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ─── Student Dashboard ────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    carousel = sheets.get_carousel_images()
    pricing  = sheets.get_pricing()
    contact  = sheets.get_contact_info()
    slots    = sheets.get_available_slots()
    user     = session["user"]
    return render_template("dashboard.html",
                           carousel=carousel,
                           pricing=pricing,
                           contact=contact,
                           slots=slots,
                           user=user)


# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.route("/api/slots")
def api_slots():
    """Return available slots as JSON."""
    slots = sheets.get_available_slots()
    available = [s for s in slots if str(s.get("is_available", "")).upper() == "TRUE"]
    return jsonify(available)


@app.route("/api/book", methods=["POST"])
@login_required
def api_book():
    """Process booking form submission."""
    user = session["user"]
    data = request.get_json() or request.form.to_dict()

    booking_data = {
        "user_id":        user.get("id", ""),
        "full_name":      user.get("full_name", ""),
        "phone":          user.get("phone", ""),
        "class":          user.get("class", ""),
        "school":         user.get("school", ""),
        "mode":           data.get("mode", "offline"),
        "basis":          data.get("basis", "hourly"),
        "quantity":       data.get("quantity", ""),
        "days_of_week":   data.get("days_of_week", ""),
        "time_slot":      data.get("time_slot", ""),
        "preferred_date": data.get("preferred_date", ""),
        "subject":        "Mathematics",
    }

    booking_id = sheets.create_booking(booking_data)
    if not booking_id:
        return jsonify({"success": False, "error": "Failed to save booking."}), 500

    # Build WhatsApp message
    msg = build_whatsapp_message(booking_data)
    wa_link = whatsapp_link(msg)

    # Store in session for confirmation page
    session["last_booking"] = {**booking_data, "id": booking_id, "wa_link": wa_link}

    return jsonify({"success": True, "booking_id": booking_id, "wa_link": wa_link})


@app.route("/confirmation")
@login_required
def confirmation():
    booking = session.get("last_booking")
    if not booking:
        return redirect(url_for("dashboard"))
    contact = sheets.get_contact_info()
    return render_template("confirmation.html", booking=booking, contact=contact)


# ─── Admin Routes ─────────────────────────────────────────────────────────────

@app.route("/admin-page", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        if sheets.authenticate_admin(password):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Incorrect admin password.", "error")

    return render_template("admin_login.html")


@app.route("/admin-logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/admin-dashboard")
@admin_required
def admin_dashboard():
    pending   = sheets.get_pending_bookings()
    confirmed = sheets.get_confirmed_bookings()
    slots     = sheets.get_available_slots()
    pricing   = sheets.get_pricing()
    contact   = sheets.get_contact_info()
    carousel  = sheets.get_carousel_images()
    return render_template("admin_dashboard.html",
                           pending=pending,
                           confirmed=confirmed,
                           slots=slots,
                           pricing=pricing,
                           contact=contact,
                           carousel=carousel)


@app.route("/api/admin/confirm", methods=["POST"])
@admin_required
def admin_confirm_booking():
    data       = request.get_json() or {}
    booking_id = data.get("booking_id")
    meet_link  = data.get("meet_link", "")

    ok = sheets.confirm_booking(booking_id, meet_link)
    if not ok:
        return jsonify({"success": False, "error": "Could not confirm booking."}), 500

    # Build confirmation message for student
    all_bookings = sheets.get_all_bookings()
    booking = next((b for b in all_bookings if str(b.get("id")) == str(booking_id)), None)

    if booking:
        student_phone = "91" + str(booking.get("phone", "")).replace("+91", "").strip()
        lines = [
            "✅ *Lalitha's Math Academy — Booking Confirmed!*",
            "",
            f"Dear {booking.get('full_name', 'Student')},",
            f"Your {booking.get('basis', '')} Mathematics session has been confirmed!",
            "",
            f"📅 *Days:* {booking.get('days_of_week', '')}",
            f"🕐 *Time:* {booking.get('time_slot', '')}",
            f"🖥 *Mode:* {str(booking.get('mode', '')).capitalize()}",
        ]
        if meet_link:
            lines.append(f"🔗 *Meet Link:* {meet_link}")
        lines += ["", "See you in class! 📐✏️", "— V. Lalitha Ma'am"]
        confirm_msg = "\n".join(lines)

        wa_link = whatsapp_link(confirm_msg, student_phone)

        # Try CallMeBot auto-send (if configured)
        sent = send_callmebot_message(student_phone, confirm_msg)

        return jsonify({
            "success": True,
            "wa_link": wa_link,
            "auto_sent": sent,
            "message": confirm_msg
        })

    return jsonify({"success": True})


@app.route("/api/admin/slots", methods=["POST"])
@admin_required
def admin_update_slots():
    data = request.get_json() or {}
    slots = data.get("slots", [])
    ok = sheets.set_all_slots(slots)
    return jsonify({"success": ok})


@app.route("/api/admin/carousel", methods=["POST"])
@admin_required
def admin_update_carousel():
    data = request.get_json() or {}
    images = data.get("images", [])
    ok = sheets.update_carousel_images(images)
    return jsonify({"success": ok})


@app.route("/api/admin/remind", methods=["POST"])
@admin_required
def admin_send_reminder():
    data       = request.get_json() or {}
    booking_id = data.get("booking_id")
    all_bookings = sheets.get_all_bookings() + sheets.get_confirmed_bookings()

    booking = next((b for b in all_bookings if str(b.get("id")) == str(booking_id)), None)
    if not booking:
        return jsonify({"success": False, "error": "Booking not found"})

    student_phone = "91" + str(booking.get("phone", "")).replace("+91", "").strip()
    lines = [
        "⏰ *Reminder — Lalitha's Math Academy*",
        "",
        f"Dear {booking.get('full_name', 'Student')},",
        "This is a reminder for your upcoming Mathematics session.",
        "",
        f"📅 *Days:* {booking.get('days_of_week', '')}",
        f"🕐 *Time:* {booking.get('time_slot', '')}",
        f"🖥 *Mode:* {str(booking.get('mode', '')).capitalize()}",
    ]
    if booking.get("meet_link"):
        lines.append(f"🔗 *Meet Link:* {booking['meet_link']}")
    lines += ["", "Please be prepared. Best of luck! 📐", "— V. Lalitha Ma'am"]
    msg = "\n".join(lines)

    sent = send_callmebot_message(student_phone, msg)
    wa_link = whatsapp_link(msg, student_phone)

    return jsonify({"success": True, "wa_link": wa_link, "auto_sent": sent})


@app.route("/api/admin/meet-link", methods=["POST"])
@admin_required
def admin_set_meet_link():
    data       = request.get_json() or {}
    booking_id = data.get("booking_id")
    meet_link  = data.get("meet_link", "")
    ok = sheets.confirm_booking(booking_id, meet_link)
    return jsonify({"success": ok})


# ─── Error Handlers ───────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("index.html",
                           carousel=sheets.get_carousel_images(),
                           pricing=sheets.get_pricing(),
                           contact=sheets.get_contact_info(),
                           is_logged_in="user" in session), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
