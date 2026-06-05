# UNICRACY

### One University. One Election.

A Modern Campus Election & Representation Platform built with Flask, MongoDB Atlas, HTML5, CSS3, and Vanilla JavaScript.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your MongoDB Atlas URI and secret key
```

### 3. Seed Admin Account

```bash
flask seed-admin
```

### 4. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python Flask |
| Database | MongoDB Atlas |
| Auth | Flask Sessions + Werkzeug |

---

## Features

- 🗳️ **One Vote Lock** — Each student can vote only once per election
- 🏛️ **Election Control Room** — Admin dashboard for managing elections
- 📋 **Candidate Manifestos** — Rich candidate profile cards
- 📊 **Result Analytics** — Visual result displays with animated charts
- 🔒 **Privacy-First** — Admins cannot see individual vote choices
- 📱 **Fully Responsive** — Works on desktop, tablet, and mobile

---

## License

MIT
