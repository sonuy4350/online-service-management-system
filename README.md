# 🛠️ Online Service Management System

A role-based web application built using **Flask** that automates the complete service request lifecycle—from request creation to engineer assignment and receipt generation.

## 🚀 Features

### 👤 Customer/User
- Register and login securely
- Create new service requests
- Track request status
- View notifications
- Access generated receipts

### 👨‍💼 Admin
- Review pending requests
- Approve or reject requests
- Assign engineers intelligently
- Generate service receipts
- Search service requests
- Monitor all activities

### 👨‍🔧 Engineer
- View assigned requests
- Manage service tasks

---

## 🏗️ System Workflow

```text
User Registration/Login
          ↓
Create Service Request
          ↓
Admin Reviews Request
          ↓
Approve / Reject
          ↓
Assign Engineer
          ↓
Engineer Performs Service
          ↓
Admin Generates Receipt
          ↓
User Receives Notification
```

---

## 🧰 Tech Stack

| Category | Technology |
|----------|------------|
| Backend | Flask, Python |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | Flask-Login |
| Forms | Flask-WTF, WTForms |
| Migration | Flask-Migrate |
| Frontend | HTML, CSS, Jinja2 |

---

## 📂 Project Structure

```bash
.
├── app.py
├── config.py
├── models.py
├── forms.py
├── extensions.py
├── requirements.txt
├── templates/
├── static/
├── migrations/
└── online_service.db
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

**macOS/Linux**
```bash
source venv/bin/activate
```

**Windows**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///online_service.db

ADMIN_EMAIL=admin@example.com
ADMIN_NAME=Admin
ADMIN_PASS=password123
```

---

## 🗄️ Database Setup

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 👨‍💼 Create Default Admin & Engineers

```bash
flask create-admin
```

### Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | password123 |
| Engineer | eng1@example.com | engpass |
| Engineer | eng2@example.com | engpass |
| Engineer | eng3@example.com | engpass |

---

## ▶️ Run Application

```bash
python app.py
```

Application runs on:

```text
http://127.0.0.1:5000
```

---

## 🔒 Security Features

- Password hashing using Werkzeug
- Role-based authorization
- Session management with Flask-Login
- CSRF protection using Flask-WTF
- Form validation with WTForms

---

## 🔮 Future Enhancements

- Email notifications
- Payment gateway integration
- File upload support
- Dashboard analytics
- AI-based engineer recommendation
- Real-time notifications

## 👨‍💻 Author

**Sonu Kumar Yadav**

---

## ⭐ Support

If you found this project useful, consider giving it a star ⭐ on GitHub.
