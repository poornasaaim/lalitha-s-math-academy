# 🎓 Lalitha's Math Academy — Comprehensive System Documentation & Client Guide

---

## 📌 Executive Summary
**Lalitha's Math Academy Tuition Platform** is a full-stack, cloud-hosted web application built specifically for managing math tuition registrations, flexible class bookings, schedule availability, and automated WhatsApp notifications.

The application leverages **Google Sheets as its real-time cloud database**, eliminating the need for complex SQL setup while providing the academy administrator (Lalitha Ma'am) with full visibility directly inside standard spreadsheets.

---

## 🔑 Admin Credentials & Security
- **Admin Portal URL:** `https://<your-app-domain>/admin-page` (or `http://localhost:5003/admin-page`)
- **Admin Password:** `Lalitha@MathAcademy`
- **Security Features:**
  - Strict password validation (rejects invalid attempts).
  - Session-based session control (`@admin_required` decorator).
  - SHA-256 hashed password authentication against Google Sheets `admin` worksheet and environment variable backup.

---

## 🛠️ Technology Stack Architecture

| Layer | Technology Used | Description |
| :--- | :--- | :--- |
| **Backend Framework** | **Flask (Python 3.11)** | Lightweight WSGI web framework handling routing, session auth, API endpoints & template rendering. |
| **Database Integration** | **Google Sheets API v4 + GSpread** | Real-time, dual-mode database integration (Live GSheets with service account & local demo fallback). |
| **Frontend Styling** | **Vanilla CSS3 (Design Tokens)** | Custom glassmorphism aesthetic, dark mode support, fluid typography, responsive flex/grid. |
| **Frontend Logic** | **Vanilla JavaScript (ES6+)** | Dynamic modal forms, interactive slot pickers, schedule tab toggles, real-time AJAX submissions. |
| **Production WSGI** | **Gunicorn 22.0** | High-performance UNIX WSGI HTTP server for production deployment. |
| **Cloud Hosting** | **Render Free Plan** | Ephemeral, containerized cloud hosting auto-configured with `render.yaml` & `Procfile`. |
| **Communication** | **WhatsApp wa.me & CallMeBot API** | Pre-formatted WhatsApp messaging links and automated background status notifications. |

---

## 🧩 Detailed Module-by-Module Explanation

### 1. 🌐 Homepage & Hero Carousel (`index.html` & `app.py`)
- **Interactive Hero Carousel:** Displays dynamic background images and captions fetched directly from the `carousel_images` Google Sheet.
- **Academy Details & Credentials:** Highlights 20+ years of teaching experience, 100% board exam pass record, and course offerings.
- **Pricing & Plan Overview:** Clear card layouts showing Hourly, Weekly, Monthly, and Yearly learning options.
- **Contact & Location:** Embeds interactive Google Maps, address details, and direct WhatsApp contact buttons.

---

### 2. 🔐 Student Authentication Module (`register.html` & `login.html`)
- **Registration Form:**
  - Captures student's Full Name, Class (Grade 1 to 12), School Name, Address, Pincode, 10-digit Phone Number, and Password.
  - Automatically formats full address and creates a record in the `users` Google Sheet.
- **Login Form:**
  - Authenticates student using 10-digit Phone Number and SHA-256 password hashing.
  - Persists student session securely.

---

### 3. 📆 Student Booking Engine (`dashboard.html` & `booking.js`)
Students can choose from **4 customizable learning plans** via an intuitive glassmorphism modal:

#### A. ⏱️ Hourly Sessions (`hourly`)
1. **Enter Hours Needed:** Choose 1, 2, 3, or 4 hours per session.
2. **Select Time Slot:** Pick an available slot loaded live from Google Sheets data.
3. **Select Preferred Start Date:** Pick calendar start date (day of week is automatically formatted).
4. **Class Mode:** Choose **Offline** (at center) or **Online** (Google Meet).

#### B. 📆 Weekly Plan (`weekly`)
1. **Number of Days per Week:** Specify desired frequency (e.g., 3 days/week).
2. **Select Specific Days:** Interactive day selector including **Sunday** (Mon–Sun).
3. **Hours per Session:** Set duration per class.
4. **Select Time Slot:** Pick available recurring slot from GSheets.
5. **Duration & Start Date:** Specify total weeks and start date.

#### C. 🗓️ Monthly Plan (`monthly`)
1. **Schedule Preference:** Select **`⚡ Daily (Mon – Sun)`** button OR **`📅 Specific Days/Week`**.
2. **Number of Months:** Choose package duration (1, 2, 3, 6 months).
3. **Hours per Session:** Set hours per class.
4. **Select Days:** Auto-selects all 7 days if "Daily" is active, or allows manual day selection.
5. **Select Time Slot:** Choose time slot.
6. **Start Date & Mode:** Pick start date and Offline/Online mode.

#### D. 🎓 Yearly Program (`yearly`)
1. **Duration in Months:** Program length (e.g., 3, 6, 9, 12 months / 1 Year).
2. **Schedule Preference:** Select **`⚡ Daily (Mon – Sun)`** button OR **`📅 Specific Days/Week`**.
3. **Hours per Session:** Select duration per session.
4. **Select Days & Slot:** Choose schedule days & time slot from GSheets.
5. **Start Date & Mode:** Select start date & mode.

---

### 4. 🛠️ Admin Management Portal (`admin_dashboard.html` & `admin.js`)
Accessible via `/admin-page` using password **`Lalitha@MathAcademy`**:

1. **📊 Overview Dashboard:** Quick stats cards for Pending Requests, Confirmed Sessions, and Available Slots.
2. **⏳ Pending Booking Requests:** Review new student bookings, view student contact details, add Google Meet links for online classes, and click `✅ Confirm` or `📲 Remind`.
3. **✅ Confirmed Sessions:** View all active confirmed sessions, update Google Meet links, and open direct WhatsApp chats with students.
4. **🕐 Availability Slot Manager:** Interactive toggle switches for every day of the week (Monday through **Sunday**). Toggling a switch and clicking `💾 Save Availability` instantly updates the `available_slots` sheet in Google Sheets!
5. **⚙️ Academy Settings:** Adjust available days, max days per week, time slots list, min/max hours, online/offline availability toggles, and pricing display hints.
6. **👥 Registered Students Directory:** Complete directory of all registered students with contact info, school name, and address.
7. **🖼️ Carousel Image Manager:** Update hero carousel image URLs and captions.
8. **🔗 GSheets Connection Status:** Displays live connection mode (`Live GSheets` vs `Demo Mode`) and direct link to open the Google Spreadsheet.

---

## 📊 Google Sheets Database Architecture (9 Worksheets)

| Worksheet Name | Primary Key / Headers | Description |
| :--- | :--- | :--- |
| **`users`** | `id, full_name, class, school, address, pincode, phone, password_hash, created_at` | Student registration directory. |
| **`admin`** | `username, password_hash` | Admin authentication hash. |
| **`settings`** | `key, value, description` | Global preferences (slots, days, pricing). |
| **`bookings`** | `id, user_id, full_name, phone, class, school, mode, basis, quantity, days_of_week, time_slot, preferred_date, subject, status, meet_link, notes, created_at` | All incoming booking requests. |
| **`confirmed_bookings`** | *(Same schema as `bookings`)* | Quick index of confirmed sessions. |
| **`available_slots`** | `day, time_slot, is_available` | Live availability toggles (Mon–Sun). |
| **`carousel_images`** | `url, caption, order` | Hero carousel images & captions. |
| **`pricing`** | `basis, description, price_hint, highlight` | Pricing plan descriptions. |
| **`contact_info`** | `key, value` | Academy phone, email, address, & map link. |

---

## 🚀 Cloud Deployment Guide (Render Free Tier)

### Environment Variables required on Render:
- `PORT` = `10000` (auto-assigned by Render)
- `FLASK_SECRET_KEY` = `lalitha-math-academy-secret-2024`
- `ADMIN_PASSWORD` = `Lalitha@MathAcademy`
- `GOOGLE_SHEET_ID` = `1yy6x8Q2MAi5BUCGl72s9yMfvi6OAoKM1nYpz0aOUDDQ`
- `GOOGLE_CREDENTIALS_JSON` = *(Paste contents of credentials.json Service Account key)*

### Start Command:
```bash
gunicorn app:app
```

---
*Documentation compiled for Lalitha's Math Academy Client Delivery.*
