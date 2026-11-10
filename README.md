# 🎟️ EpicEvents CRM

## 📜 Event Management CRM - OpenClassrooms Project 12

EpicEvents CRM is a **command-line interface (CLI)** application developed in **Python** for comprehensive management of **customers, contracts, and events**.
Built on the **⚡ Textual** library, it provides a **rich and interactive interface** directly in the terminal.

This project implements an **MVC (Model-View-Controller)** architecture with a **🔒 secure authentication system** using **JWT (JSON Web Tokens)** and **🔑 RSA keys**, along with a **🛡️ RBAC (Role-Based Access Control)** permission system.

---

## 📚 Table of Contents

- [🏔️ Overview](#overview)
- [📋 Prerequisites](#prerequisites)
- [⚙️ Installation and Configuration](#installation-and-configuration)
- [🗃️ Database Initialization](#database-initialization)
- [🛠️ Error Tracking with Sentry](#error-tracking-with-sentry)
- [▶️ Running the Application](#running-the-application)
- [✨ Features](#features)
- [🏗️ Technical Architecture](#technical-architecture)
- [🧪 Testing and Coverage](#testing-and-coverage)
- [🔐 Authentication System](#authentication-system)
- [👥 RBAC Permission System](#rbac-permission-system)
- [📖 Resources](#resources)
- [📜 License](#license)
- [👤 Authors](#authors)
- [🙏 Acknowledgments](#acknowledgments)

---

## 🏔️ Overview

EpicEvents CRM enables **EpicEvents** company collaborators to efficiently manage:

| Feature          | Description                                      |
|------------------|--------------------------------------------------|
| **👥 Customers**  | Create, view, and update customer information     |
| **📄 Contracts** | Track contracts, status, and amounts               |
| **🎉 Events**    | Plan and manage events with support assignment    |
| **👥 Collaborators** | Manage the internal team (ADMIN only)        |

The application is designed for **three departments**:
- **ADMIN**: Collaborator & contract management
- **SALES**: Customer & contract management
- **SUPPORT**: Event management

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

| Requirement       | Version       | Check Command               |
|-------------------|---------------|-----------------------------|
| **Python**     | 3.13+         | `python --version`         |
| **MySQL**      | 8.0+          | `mysql --version`          |
| **Git**        | Latest        | `git --version`            |
| **Poetry**     | Latest        | `poetry --version`        |

### ⚡ Quick Verification
```bash
# Check all prerequisites at once
python --version && mysql --version && git --version && poetry --version
```

---

## ⚙️ Installation and Configuration

### 1️⃣ Clone the Repository
```bash
cd /path/to/your/projects
git clone https://github.com/Q1009/P12-EpicEvents.git
```

### 2️⃣ Setup Virtual Environment
```bash
cd P12-EpicEvents
poetry install
```

### 3️⃣ Configure Environment Variables
```bash
cd P12-EpicEvents
touch .env
```
Open the `.env` file and edit it as follows :
```env
# ===== Database =====
DB_HOST=localhost
DB_PORT=3306
DB_USER=epic_events_user
DB_PASSWORD=YourSecurePassword123!
DB_NAME=epicevents

# ===== Sentry =====
# SENTRY_DSN=https://xxx@sentry.io/xxx

# ===== Safety =====
# Generate a new secret key with: poetry run python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_64_character_hex_secret_key

# ===== Environment =====
ENVIRONMENT=development  # development|staging|production

# ===== JWT Configuration =====
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_PRIVATE_KEY_PATH=keys/keys/jwt_private_key.pem
JWT_PUBLIC_KEY_PATH=keys/keys/jwt_public_key.pem

# ===== Passwords (for initial database seeding) =====
COLLAB_PASSWORD_1=password1
COLLAB_PASSWORD_2=password2
COLLAB_PASSWORD_3=password3
COLLAB_PASSWORD_4=password4
COLLAB_PASSWORD_5=password5
```

> [!IMPORTANT]
> Make sure to run poetry run :
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
> And then paste the 64 character hex as the SECRET_KEY

---

## 🗃️ Database Initialization

### 1️⃣ Create MySQL Database
```bash
mysql -u root -p
```
```sql
CREATE DATABASE IF NOT EXISTS epicevents;
CREATE USER IF NOT EXISTS 'epic_events_user'@'localhost' IDENTIFIED BY 'MyPassword123!';
GRANT ALL PRIVILEGES ON epicevents.* TO 'epic_events_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2️⃣ Generate RSA Keys
```bash
poetry run python -m keys.generate_keys
```
> 📁 Files generated: `keys/keys/jwt_private_key.pem`, `keys/keys/jwt_public_key.pem`

### 3️⃣ Apply Migrations
```bash
poetry run alembic upgrade head
```

### 4️⃣ Seed the Database
```bash
poetry run python -m database.seed
```
> 🌱 **Seeded data includes**:
> - 3 departments (ADMIN, SALES, SUPPORT)
> - 6 collaborators
> - 10 customers with contacts
> - 10 locations
> - 8 contracts
> - 5 events

---

## 🛠️ Error Tracking with Sentry

**🎯 Purpose**: Real-time error tracking and monitoring

### 📝 Configuration
Add to `.env`:
```env
SENTRY_DSN=https://your-public-key@sentry.io/your-project-id
```

### 📊 Use Cases
| Scenario | Logged Data | Benefit |
|----------|-------------|---------|
| Collaborator actions | Main data | Monitor management |
| Contract signature | Contract info | Track history |
| Unhandled exceptions | Error details | Immediate alerts |

---
---
## ▶️ Running the Application

```bash
poetry run python main.py
```

---

## ✨ Features

### 🔐 Authentication
| Feature | Description | Icon |
|---------|-------------|------|
| **Login** | Email/password auth with JWT | |
| **Logout** | Invalidate local tokens | |
| **Auto-refresh** | Automatic token refresh | |
| **Persistent Session** | Secure local token storage | |

---

### 👥 Customer Management
| Feature | Description | Allowed Roles |
|---------|-------------|---------------|
| **List** | View all customers | ADMIN, SALES, SUPPORT |
| **Create** | Add new customer | ADMIN, SALES |
| **Update** | Modify customer info | ADMIN, SALES |
| **View** | Detailed customer view | ADMIN, SALES, SUPPORT |

---

### 📄 Contract Management
| Feature | Description | Allowed Roles |
|---------|-------------|---------------|
| **List** | View all contracts | ADMIN, SALES, SUPPORT |
| **Create** | Add new contract | ADMIN, SALES |
| **Update** | Modify contract | ADMIN, SALES |
| **Change Status** | Update status | ADMIN, SALES |

---

### 🎉 Event Management
| Feature | Description | Allowed Roles |
|---------|-------------|---------------|
| **List** | View all events | ADMIN, SALES, SUPPORT |
| **Create** | Add new event | ADMIN, SALES |
| **Update** | Modify event | ADMIN, SUPPORT |
| **Assign Support** | Assign representative | ADMIN |

---
---
## 🏗️ Technical Architecture

| Component | Technology | Version |
|-----------|------------|---------|
| **Language** | Python | 3.13+ |
| **CLI Framework** | Textual | 8.2.8+ |
| **ORM** | SQLAlchemy | 2.0.51+ |
| **Database** | MySQL | 8.0+ |
| **Migrations** | Alembic | 1.18.5+ |
| **Authentication** | PyJWT + Cryptography | 2.8.0+ |
| **Hashing** | bcrypt | 5.0.0+ |
| **Environment** | python-dotenv | 1.2.2+ |
| **Logging** | Sentry | 2.66.0+ |
| **Testing** | pytest | 9.1.1+ |
| **Formatting** | Ruff | 0.16.10 |

---

## 🧪 Testing and Coverage

### 🚀 Run Tests
```bash
# All tests
poetry run pytest -vv

# Specific test file
poetry run pytest feature/tests/test_module.py -vv

# With coverage
poetry run coverage run -m pytest && poetry run coverage html
```

> 📊 **View coverage report**:
> ```bash
> open htmlcov/index.html  # macOS
> start htmlcov/index.html   # Windows
> xdg-open htmlcov/index.html # Linux
> ```

---
---
## 🔐 Authentication System

**🔑 JWT (JSON Web Tokens)** with **RS256** algorithm

### 🏗️ Components
| Component | File | Role |
|-----------|------|------|
| **AuthController** | `authentication/authentication_controller.py` | Login/logout flow |
| **AuthView** | `authentication/authentication_view.py` | Credential UI |
| **AuthService** | `services/authentication_services.py` | Business logic |
| **TokenService** | `services/authentication_services.py` | Token management |
| **TokenManagement** | `tokens/token_management.py` | Secure storage |
| **RSA Key Management** | `keys/rsa_key_management.py` | Key storage |

### Token Payload
```json
{
  "sub": "1",           // User ID
  "jti": "uuid",        // Token ID
  "type": "access",     // Token type
  "exp": 1234567890,    // Expiration
  "iat": 1234567800     // Issued at
}
```

---
---
## 👥 RBAC Permission System

### 🎯 Roles & Permissions
| Role | 🎯 Responsibilities | 🔑 Key Permissions |
|------|--------------------|-------------------|
| **ADMIN** | Team & contract management | Full CRUD on collaborators, contracts, events |
| **SALES** | Customer & contract lifecycle | CRUD customers, contracts, read-only events |
| **SUPPORT** | Event planning | CRUD events, read-only customers/contracts |

---
---
## 📖 Resources

- [Textual Documentation](https://textual.textualize.io/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [bcrypt Documentation](https://bcrypt.readthedocs.io/)
- [Cryptography Library](https://cryptography.io/)

---
---
## 📜 License

This project is **educational** and licensed under a **custom OpenClassrooms license**.

### ✅ Allowed
- 📚 Personal learning
- 🎨 Portfolio demonstration
- 💼 Job interviews
- 🔍 Code study

### ❌ Not Allowed
- 💰 Commercial use without permission
- ❌ Remove copyright notices
- 👑 Claim ownership

**© 2026 Quentin Tellier**

---
---
## 👤 Authors

- **Quentin Tellier** - Developer
  - Email: [quentin.tellier@outlook.com](mailto:quentin.tellier@outlook.com)

---
---
## 🙏 Acknowledgments

- ⚡ [Textual](https://textual.textualize.io/) - CLI Framework
- 🐍 The Python community
- 🌟 All open-source contributors