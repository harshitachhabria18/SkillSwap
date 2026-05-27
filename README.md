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


