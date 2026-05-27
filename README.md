# 🔄 SkillSwap

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)](https://cloudinary.com/)

**Peer-to-Peer Skill Exchange Platform**

---

## 🔗 Live Demo
[https://skillswap-nfjm.onrender.com](https://skillswap-nfjm.onrender.com)

---

## 📖 About the Project
SkillSwap is a full-stack peer-to-peer skill exchange platform developed using Flask (Python). The application enables users to connect with others by offering skills they possess and requesting skills they want to learn. Users can create profiles, manage skill listings, browse potential matches, and send structured swap requests for collaborative learning.

The platform supports user authentication, profile management, skill tagging, structured swap requests, search and filtering, and a feedback/rating system, with PostgreSQL used for database management, Cloudinary for profile photo storage, and Bootstrap for a responsive user interface.

### 💡 Problem It Solves
Access to skill development often depends on financial resources, formal learning platforms, or existing professional networks. SkillSwap addresses this challenge by providing a platform where users can exchange knowledge and expertise directly, enabling collaborative learning without monetary dependency.

---

## ✨ Features
- **User Authentication** — Secure registration and login with password hashing and session management using Flask-Login
- **Profile Management** — Update profile details including name, location, availability, session duration, and profile visibility
- **Profile Photo Upload** — Profile images uploaded and managed through Cloudinary
- **Skill Tagging** — Add and manage skills offered and skills requested from a shared skills database
- **Browse & Search** — Paginated user discovery with search by name or skill, along with availability-based filtering
- **Swap Requests** — Send structured swap requests with offered skills, requested skills, and personalized messages
- **Request Management** — Manage incoming and outgoing requests with status tracking (Pending / Accepted / Rejected)
- **Feedback & Ratings** — Submit star ratings and written reviews after completed skill swaps
- **Average Rating Display** — Display average user ratings and review counts on profile and browse sections
- **Profile Visibility Control** — Toggle profile visibility between Public and Private for controlled discoverability

---

## ⚙️ How SkillSwap Works
1. Users create profiles and add skills they offer and skills they want to learn.
2. The browse system allows users to search and filter potential matches by skill, availability, or location.
3. Users send structured swap requests containing offered skills, requested skills, and personalized messages.
4. Recipients can accept or reject requests with status tracking.
5. After completing a swap, users can leave ratings and feedback to build trust and reputation within the platform.

---

## 🛠️ Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask |
| Database | PostgreSQL |
| ORM & Migrations | SQLAlchemy, Flask-Migrate, Alembic |
| Authentication | Flask-Login, Werkzeug (Password Hashing) |
| Forms & Validation | Flask-WTF, WTForms |
| File Storage | Cloudinary |
| Frontend | HTML5, CSS3, Bootstrap, JavaScript |
| Templating Engine | Jinja2 |

---

## 📁 Project Structure
```bash
SKillSwap/
├── app/
│   ├── auth/
│   │   ├── templates/
│   │   │   └── auth/
│   │   │       ├── login.html
│   │   │       └── register.html
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── user/
│   │   ├── templates/
│   │   │   └── user/
│   │   │       └── profile.html
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── swap/
│   │   ├── templates/
│   │   │   └── swap/
│   │   │       ├── browse.html
│   │   │       ├── request_swap.html
│   │   │       ├── swap_requests.html
│   │   │       ├── view_profile.html
│   │   │       └── leave_feedback.html
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── script.js
│   │   └── images/
│   ├── templates/
│   │   └── base.html
│   ├── __init__.py
│   ├── models.py
│   └── forms.py
├── migrations/
│   └── versions/
├── instance/
│   └── config.py
├── .env
├── requirements.txt
├── run.py
└── seed.py
```

---

## 🚀 Setup and Installation
### Prerequisites
- Python 3.12+
- PostgreSQL
- Cloudinary Account

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
Create a .env file in the root directory:
```env
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost/skillswap

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Initialize the Database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Run the Application
```bash
python run.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser

---

## 🗄️ Database Schema
The application uses a relational database design to manage users, skills, swap requests, and feedback efficiently.

![ER Diagram](screenshots/er_diagram.png)

---

## 📸 Screenshots
### Home Page
![Home Page](screenshots/home.png)

### User Profile
![User Profile](screenshots/user_profile.png)

### Swap Requests
![Swap Requests](screenshots/swap_requests.png)

## 🎥 Demo Video
https://github.com/user-attachments/assets/86d6c4b2-2051-4239-b402-653be285a9b2

---

## 🔮 Future Improvements
- In-App Messaging — Real-time chat between matched users instead of relying on external communication
- Notifications — Email or in-app notifications for swap request updates and new messages
- Smart Matching — Algorithm to automatically suggest compatible swap partners based on offered and wanted skills
- OAuth Login — Sign in with Google or GitHub for faster onboarding
- Session Scheduling — Built-in calendar to schedule and manage swap sessions between users
- Location-Based Matching — Filter and suggest users based on geographic proximity
- Gamification — Badges and achievements to reward active and highly-rated users

---

## 👨‍💻 Author
**Harshita Chhabria**
