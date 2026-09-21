# 📐 Lalitha's Math Academy — Booking Platform

A full-stack tuition booking platform for **Lalitha's Math Academy**, Kolathur, Chennai.

**Tech Stack:** Flask · Google Sheets · Vanilla JS · HTML/CSS · WhatsApp API

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd Academy_Website
pip install -r requirements.txt
```

### 2. Set Up Google Sheets (One-time)

Follow the steps below to connect the app to Google Sheets.

#### Step A — Create a Google Cloud Project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g., `lalitha-math-academy`)
3. Enable **Google Sheets API** and **Google Drive API**
   - Search for "Google Sheets API" → Enable
   - Search for "Google Drive API" → Enable

#### Step B — Create a Service Account
1. Go to **IAM & Admin → Service Accounts**
2. Click **Create Service Account**
3. Name it `lalitha-sheets` → Create
4. Click on the service account → **Keys → Add Key → JSON**
5. Download the JSON file → rename it to `credentials.json`
6. Place `credentials.json` in the `Academy_Website/` folder

#### Step C — Create a Google Spreadsheet
1. Go to [sheets.google.com](https://sheets.google.com)
2. Create a new spreadsheet named `Lalitha Math Academy`
3. Copy the spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
   ```
4. Share the spreadsheet with your service account email:
   - Click Share → add the service account email (from credentials.json, field `client_email`)
   - Set permission to **Editor**

#### Step D — Configure .env
```bash
cp .env.example .env
```
Edit `.env` and fill in:
```
GOOGLE_SHEET_ID=your_sheet_id_here
FLASK_SECRET_KEY=any_random_long_string_here
```

#### Step E — Initialize Sheets with Sample Data
```bash
python setup_sheets.py
```

This creates all required sheets with sample data:
- `users` — student accounts
- `admin` — admin login (default password: `admin@lalitha2024`)
- `carousel_images` — homepage carousel
- `available_slots` — time slot availability
- `pricing` — plan descriptions
- `bookings` — all booking requests
- `confirmed_bookings` — confirmed sessions
- `contact_info` — contact details

### 3. Run the App

```bash
flask run
```

Visit: **http://localhost:5000**

---

## 📱 WhatsApp Integration

### Student Booking Confirmation
When a student submits a booking, they get a button that opens WhatsApp with a pre-filled message containing all their booking details. **No API key needed** — uses `wa.me` deep links.

### Automated Admin Notifications (Optional)
To enable automatic WhatsApp messages (without manual clicking):
1. Visit: [callmebot.com](https://www.callmebot.com/blog/free-api-whatsapp-messages/)
2. Send a WhatsApp message to CallMeBot to get your API key
3. Add it to `.env`: `CALLMEBOT_API_KEY=your_key`

---

## 🔐 Admin Access

- URL: `http://localhost:5000/admin-page`
- Default password: `admin@lalitha2024`
- To change: Update the `admin` sheet's `password_hash` column

---

## 📁 File Structure

```
Academy_Website/
├── app.py                    # Flask routes
├── sheets.py                 # Google Sheets CRUD
├── setup_sheets.py           # One-time sheet initializer
├── requirements.txt
├── credentials.json          # (you provide — GCP service account)
├── .env                      # (you create from .env.example)
├── .env.example
├── static/
│   ├── css/style.css         # Full design system
│   └── js/
│       ├── main.js           # Carousel, dark/light toggle
│       ├── booking.js        # Booking form logic
│       └── admin.js          # Admin dashboard
└── templates/
    ├── base.html             # Navbar + footer
    ├── index.html            # Public landing page
    ├── login.html
    ├── register.html
    ├── dashboard.html        # Student dashboard
    ├── confirmation.html     # Booking confirmation
    ├── admin_login.html      # /admin-page
    └── admin_dashboard.html
```

---

## 📋 Pages & Features

| Page | URL | Description |
|------|-----|-------------|
| Landing Page | `/` | Carousel, about, pricing, contact |
| Login | `/login` | Phone + password |
| Register | `/register` | Full student registration |
| Dashboard | `/dashboard` | Booking plans + glass modal |
| Confirmation | `/confirmation` | Booking summary + WhatsApp CTA |
| Admin Login | `/admin-page` | Password protected |
| Admin Dashboard | `/admin-dashboard` | Full admin panel |

---

## 🎨 Design

- **Dark Mode** (default) / **Light Mode** toggle
- Glassmorphism cards with backdrop blur
- Hero carousel with smooth transitions
- Gradient typography and buttons
- Scroll-triggered fade animations
- Fully responsive (mobile/tablet/desktop)
- Google Fonts: Outfit + Inter

---

## 📞 Academy Details

| | |
|---|---|
| **Name** | Lalitha's Math Academy |
| **Teacher** | V. Lalitha M.Sc., B.Ed. |
| **Experience** | 20 Years |
| **Subject** | Mathematics |
| **Phone** | +91 9841260450 |
| **Email** | lalithamurali1996@gmail.com |
| **Address** | 89B, 15th Cross Street, Sivanandha Nagar, Kolathur, Chennai - 600099 |

---

## 🔧 Updating Content

All content is managed via Google Sheets:

| What to Update | Sheet |
|---|---|
| Homepage carousel images | `carousel_images` |
| Time slot availability | `available_slots` |
| Contact details / social links | `contact_info` |
| Pricing descriptions | `pricing` |
| Admin password | `admin` |

---

## 📤 GitHub Push

Run the following after everything is set up:

```bash
git init
git add .
git commit -m "Initial commit: Lalitha's Math Academy booking platform"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

> **Note:** Add `credentials.json` and `.env` to `.gitignore` before pushing!

---

Made with ❤️ for Lalitha's Math Academy · Kolathur, Chennai
