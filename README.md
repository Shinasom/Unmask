# Unmask - Privacy-First Social Media

**Reveal on Your Terms**

A consent-driven social media platform that puts users in control of their digital identity. Using facial recognition technology, Unmask automatically masks faces in photos and requires explicit approval before revealing them.

![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Django](https://img.shields.io/badge/django-4.2+-green.svg)
![Next.js](https://img.shields.io/badge/next.js-15.4+-black.svg)

---

## 🎯 Core Concept

Traditional social media platforms share photos of you without your permission. **Unmask flips this model:**

1. 📸 Someone uploads a photo with you in it
2. 🔍 Facial recognition automatically detects your face
3. 🚫 Your face is **masked by default**
4. 📬 You receive a consent request notification
5. ✅ You approve or deny - **you're in control**
6. 👤 Your face is unmasked only after you approve

**Your face, your choice, your consent.**

---

## ✨ Key Features

### 🛡️ Privacy First

- **Automatic face masking** - All detected faces are masked until consent is given
- **Granular consent control** - Review each photo individually before approval
- **Privacy modes** - Choose between "Require Consent" (default) or "Public" sharing

### 🎨 Modern Social Experience

- Photo sharing with filters and editing
- Like and comment on posts
- Real-time consent request notifications
- User profiles and activity feeds
- Stories/moments feature

### 🔐 Security & Performance

- JWT-based authentication
- Pre-computed face encodings for fast recognition
- Role-based access control
- Comprehensive audit logging

---

## 🏗️ Architecture

### Backend (Django REST Framework)

```
backend/
├── core/           # Project configuration
├── users/          # User authentication & face encoding
├── photos/         # Photo upload, processing & consent workflow
└── interactions/   # Likes, comments, social features
```

**Key Technologies:**

- Python 3.11+
- Django 4.2 & Django REST Framework
- PostgreSQL database
- face_recognition library (dlib)
- JWT authentication

### Frontend (Next.js)

```
frontend/
├── src/
│   ├── app/              # Next.js pages (App Router)
│   ├── components/       # React components
│   ├── context/          # Auth & state management
│   └── lib/              # API client & utilities
```

**Key Technologies:**

- React 19 & Next.js 15.4
- Tailwind CSS v4
- Axios for API communication
- Client-side routing

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/downloads)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/unmask.git
cd unmask
```

### 2️⃣ Backend Setup

#### Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=unmask_db
DB_USER=unmask_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

#### Set Up PostgreSQL Database

```bash
# Open PostgreSQL prompt
psql -U postgres

# Create database and user
CREATE DATABASE unmask_db;
CREATE USER unmask_user WITH PASSWORD 'your-secure-password';
ALTER ROLE unmask_user SET client_encoding TO 'utf8';
ALTER ROLE unmask_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE unmask_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE unmask_db TO unmask_user;
\q
```

#### Run Migrations

```bash
python manage.py migrate
```

#### Create Superuser

```bash
python manage.py createsuperuser
```

#### Start Backend Server

```bash
python manage.py runserver
```

Backend API will be available at **http://127.0.0.1:8000/**

---

### 3️⃣ Frontend Setup

Open a **new terminal window**:

```bash
cd frontend
```

#### Install Dependencies

```bash
npm install
```

#### Configure Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

#### Start Development Server

```bash
npm run dev
```

Frontend will be available at **http://localhost:3000/**

---

## 🎮 Using the Application

### First Time Setup

1. **Navigate to** http://localhost:3000
2. **Register** a new account with:
   - Username
   - Email
   - Password
   - **Profile picture** (required for face recognition)
3. **Upload** your first photo
4. **Experience** the consent workflow

### Key Workflows

#### Uploading Photos

1. Click the **Upload** button (+ icon)
2. Select an image from your device
3. Add caption, location, tags (optional)
4. Apply filters if desired
5. Click **Share Post**

#### Managing Consent Requests

1. Navigate to **Consent** tab
2. Review pending requests
3. **Approve** or **Deny** each request
4. View history of approved/denied requests

#### Privacy Settings

1. Go to **Settings**
2. Choose your face sharing mode:
   - **Require Consent** (recommended) - Review each photo
   - **Public** - Automatically unmask in all photos

---

## 🔧 Development

### Useful Commands

#### Backend

```bash
# Run migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Create superuser for admin access
python manage.py createsuperuser

# Access Django admin
# Visit: http://127.0.0.1:8000/admin/

# Compute face encodings for all users
python manage.py compute_face_encodings --all

# Clean test data (development only!)
python cleanup_script.py

# run with daphne
daphne -b 127.0.0.1 -p 8000 core.asgi:application

```

#### Frontend

```bash
# Start development server
npm run dev

# Build for production
npm run build


# Start production server
npm start

# Lint code
npm run lint
```

### API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/

### Key API Endpoints

```
POST   /api/token/              # Obtain JWT token
POST   /api/token/refresh/      # Refresh JWT token
GET    /api/users/              # List users (needs security fix)
POST   /api/users/              # Register new user
GET    /api/photos/             # List photos (feed)
POST   /api/photos/             # Upload new photo
GET    /api/consent-requests/   # List consent requests
PATCH  /api/consent-requests/{id}/ # Update consent status
POST   /api/likes/              # Like a photo
POST   /api/comments/           # Comment on a photo
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Style

- **Backend**: Follow PEP 8 guidelines
- **Frontend**: Use ESLint configuration provided
- **Commits**: Use conventional commits format

---


## 👥 Authors

- **Shinas Om** [GitHub](https://github.com/Shinasom) [Linkedin](https://www.linkedin.com/in/shinasom/)

---

## 🙏 Acknowledgments

- **face_recognition** library by Adam Geitgey
- **Next.js** team for the amazing framework
- **Django REST Framework** for the powerful API toolkit
- **Tailwind CSS** for the utility-first CSS framework
- All contributors and testers

---

## 📊 Project Status

- **Development Status**: Alpha
- **Current Version**: 0.1.0
- **Last Updated**: November 2025
- **Stability**: Experimental - Not ready for production

---

<p align="center">
  <strong>Built with ❤️ for a more private internet</strong>
</p>

<p align="center">
  <a href="#-core-concept">Core Concept</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-using-the-application">Usage</a> •
  <a href="#-contributing">Contributing</a>
</p>
