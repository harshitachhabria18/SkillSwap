# 🔄 SkillSwap

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech/)
[![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)](https://cloudinary.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)

**Peer-to-Peer Skill Exchange Platform**

---

## 🔗 Live Demo
[https://skillswap-nfjm.onrender.com](https://skillswap-nfjm.onrender.com)

---

## 📖 About the Project
SkillSwap is a full-stack peer-to-peer skill exchange platform developed using Flask (Python). The application enables users to connect with others by offering skills they possess and requesting skills they want to learn. Users can create profiles, manage skill listings, browse potential matches, and send structured swap requests for collaborative learning along with messaging, session scheduling, notifications, Google login and an admin panel.

The platform supports user authentication, profile management, skill tagging, structured swap requests, search and filtering, and a feedback/rating system, with PostgreSQL (hosted on Neon) for data management, Cloudinary for profile photo storage, Brevo for transactional emails, and Bootstrap for a responsive user interface.

### 💡 Problem It Solves
Access to skill development often depends on financial resources, formal learning platforms, or existing professional networks. SkillSwap addresses this challenge by providing a platform where users can exchange knowledge and expertise directly, enabling collaborative learning without monetary dependency.

---

## ✨ Features
- **User Authentication** — Secure registration and login with password hashing and session management using Flask-Login
- **Google Login** — Sign in or create an account instantly using your Google account
- **Forgot Password** — Reset your password via a secure link sent to your email
- **Profile Management** — Update profile details including name, location, availability, session duration, and profile visibility
- **Profile Photo Upload** — Profile images uploaded and managed through Cloudinary
- **Skill Tagging** — Add and manage skills offered and skills requested from a shared skills database
- **Browse & Search** — Paginated user discovery with search by name or skill, along with availability-based filtering
- **Swap Requests** — Send structured swap requests with offered skills, requested skills, and personalised messages
- **Request Management** — Manage incoming and outgoing requests with status tracking (Pending / Accepted / Rejected / Completed)
- **1:1 Messaging** — Chat privately with your swap partner once a request is accepted
- **Session Scheduling** — Propose and confirm a date, time, and meeting link for your skill session
- **In-App Notifications** — Get notified for all swap activity via a bell icon in the navbar; multiple messages from the same person are grouped into one notification
- **Feedback & Ratings** — Submit star ratings and written reviews after completed skill swaps
- **Average Rating Display** — Display average user ratings and review counts on profile and browse sections
- **Profile Visibility Control** — Toggle profile visibility between Public and Private for controlled discoverability
- **Admin Panel** — A special dashboard for admins to view platform stats, manage users, moderate skills and reviews

---

## ⚙️ How SkillSwap Works
1. Users register with email and password or sign in with Google, and add their location, availability, and preferred session length during profile completion.
2. Users add the skills they can teach and the skills they want to learn.
3. Users search for others by name or skill and filter by availability.
4. Users send a swap request by selecting what they will offer, what they want to learn, and adding a personal message.
5. The recipient accepts or rejects the request. Both users are notified immediately.
6. Once a swap is accepted, both users can message each other in a private chat.
7. Either user can propose a date, time, duration, and meeting link for the session. The other person confirms or declines.
8. At session time, users click the meeting link directly from the session page.
9. Users mark the swap complete and leave a star rating and review for their partner.

---

## 🛠️ Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.1 |
| Database | PostgreSQL (hosted on Neon) |
| ORM & Migrations | SQLAlchemy 2.0, Flask-Migrate, Alembic |
| Authentication | Flask-Login, Werkzeug (password hashing), Authlib (Google OAuth) |
| Forms & Validation | Flask-WTF (CSRF protection), WTForms, email-validator |
| Transactional Email | Brevo API (via `requests`) |
| File Storage | Cloudinary |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Templating Engine | Jinja2 |
| Deployment | Render (Gunicorn web server), `Procfile` + `runtime.txt` |

---

## 📁 Project Structure
```bash
SkillSwap/
├── app/
│   ├── admin/
│   │   ├── templates/admin/
│   │   │   ├── base_admin.html
│   │   │   ├── dashboard.html
│   │   │   ├── feedback.html
│   │   │   ├── skills.html
│   │   │   ├── swaps.html
│   │   │   └── users.html
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── utils.py
│   ├── auth/
│   │   ├── templates/auth/
│   │   │   ├── forgot_password.html
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   ├── reset_email.html
│   │   │   └── reset_password.html
│   │   ├── __init__.py
│   │   ├── oauth.py
│   │   └── routes.py
│   ├── messaging/
│   │   ├── templates/messaging/
│   │   │   └── chat.html
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── scheduling/
│   │   ├── templates/scheduling/
│   │   │   └── session.html
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── swap/
│   │   ├── templates/swap/
│   │   │   ├── browse.html
│   │   │   ├── leave_feedback.html
│   │   │   ├── private_profile.html
│   │   │   ├── request_swap.html
│   │   │   ├── swap_requests.html
│   │   │   └── view_profile.html
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── user/
│   │   ├── templates/user/
│   │   │   └── profile.html
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/script.js
│   │   └── images/
│   ├── templates/
│   │   ├── base.html
│   │   └── notifications/list.html
│   ├── __init__.py
│   ├── forms.py
│   ├── models.py
│   ├── notifications.py
│   └── notif_routes.py
├── migrations/
├── .env               ← never committed
├── .gitignore
├── Procfile
├── requirements.txt
├── run.py
├── runtime.txt
└── seed.py
```

---

## 🚀 Setup and Installation
### Prerequisites
- Python 3.12+
- A [Neon](https://neon.tech/) (or any PostgreSQL) database
- A [Cloudinary](https://cloudinary.com/) account
- A [Google Cloud Console](https://console.cloud.google.com/) project with OAuth 2.0 credentials
- A [Brevo](https://www.brevo.com/) account for password-reset emails

### Clone the Repository
```bash
git clone https://github.com/harshitachhabria18/SkillSwap.git
cd SkillSwap
```

### Create and Activate Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure Environment Variables
Create a `.env` file in the root directory (never commit this file):
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-long-random-secret-key

SQLALCHEMY_DATABASE_URI=postgresql://user:password@host/dbname?sslmode=require

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

BREVO_API_KEY=your_brevo_api_key
MAIL_SENDER=your_verified_sender@example.com
```

### Set Up Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services → Credentials**.
2. Create an **OAuth 2.0 Client ID** (Web application).
3. Add the following **Authorised Redirect URIs**:
   - `http://127.0.0.1:5000/auth/google/callback`
   - `https://your-app.onrender.com/auth/google/callback`
4. Copy the Client ID and Secret into your `.env`.

### Apply Database Migrations
```bash
flask db upgrade
```

### Run the Application
```bash
flask run
```
Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Promote a User to Admin
```bash
flask make-admin your@email.com
```
This is the only way to grant admin access — there is no web route for promotion.

---

## 🗄️ Database Schema
The application uses a relational database design to manage users, skills, swap requests, notifications, messages, session scheduling, and feedback efficiently.

![ER Diagram](screenshots/er_diagram_updated.png)

---

## 📸 Screenshots
### Home Page
![Home Page](screenshots/home.png)

### User Profile
![User Profile](screenshots/user_profile.png)

### Swap Requests
![Swap Requests](screenshots/swap_requests.png)

## 🎥 Demo Video
https://github.com/user-attachments/assets/d3045fca-2739-4e2c-ad48-cddc66911e47

---

## 🔒 Security
- **CSRF Protection** — All forms are protected against cross-site request forgery using Flask-WTF
- **Password Hashing** — Passwords are never stored in plain text; Werkzeug hashes them before saving to the database
- **Password Reset Tokens** — Reset links expire after 1 hour and cannot be faked or reused; Google-only accounts cannot use this flow
- **Access Control** — Protected pages require login; chat and session pages additionally check that the user is a participant in that specific swap
- **Ban Enforcement** — Banned users are automatically logged out on their very next page load, even if they were already logged in
- **Profile Privacy** — Private profiles are excluded from search results and show a placeholder page when visited directly

---

## 🔮 Future Improvements
- **Smart Matching** — Automatically suggest compatible swap partners based on complementary skills
- **Location-Based Matching** — Filter and suggest users based on geographic proximity
- **Gamification** — Badges and achievements to reward active and highly-rated users
- **Real-Time Chat** — Replace the current polling system with instant messaging using WebSockets
- **Email Alerts** — Send email notifications for key events like new swap requests or confirmed sessions
- **Mobile App / PWA** — A Progressive Web App with push notifications for a native mobile experience

---

## 👨‍💻 Author
**Harshita Chhabria**
