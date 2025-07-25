# Coderr - Freelancer Marketplace API

A Django REST API for a freelancer platform that allows business users to create offers and customer users to book and review them.

---

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [Authentication](#authentication)
- [Data Model](#data-model)
- [Testing](#testing)
- [Deployment](#deployment)

---

## 🚀 Features

- **User Management**: Registration and authentication for business and customer users
- **Offer Management**: CRUD operations for offers with details (Basic, Standard, Premium)
- **Order System**: Customers can book offers and track their status
- **Review System**: Customers can rate business users
- **Filter & Search**: Advanced filtering capabilities for all resources
- **RESTful API**: Complete REST API with Django REST Framework

---

## 🛠 Technology Stack

- **API**: Django REST Framework
- **Database**: SQLite
- **Authentication**: Token-based Authentication

---

### Setup

1. **Clone repository**
```bash
git clone <repository-url>
cd coderr
```

2. **Create virtual environment**
```bash
python -m venv env

# Windows
env\Scripts\activate

# macOS/Linux
source env/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Migrate database**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Start development server**
```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/`.