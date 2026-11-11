# 🎟️ EpicEvents CRM

EpicEvents CRM is a **command-line interface (CLI)** application developed in **Python** for comprehensive management of **customers, contracts, and events**.
Built on the **Textual** library, it provides a **rich and interactive interface** directly in the terminal.

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
- [🔍 Code Quality & Linting](#code-quality--linting)
- [🔐 Authentication System](#authentication-system)
- [👥 RBAC Permission System](#rbac-permission-system)
- [📖 Resources](#resources)
- [📜 License](#license)
- [👤 Authors](#authors)
- [🙏 Acknowledgments](#acknowledgments)

---

## Overview

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

## Prerequisites

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

## Installation and Configuration

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
# Generate a new secret key with:
# poetry run python -c "import secrets; print(secrets.token_hex(32))"
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
COLLAB_PASSWORD_6=password6
```

> [!IMPORTANT]
> Make sure to run :
> ```bash
> poetry run python -c "import secrets; print(secrets.token_hex(32))"
> ```
> And then paste the 64 character hex as the SECRET_KEY

---

## Database Initialization

### 1️⃣ Create MySQL Database
```bash
# Connect to your MySQL service
mysql -u root -p
```
```sql
CREATE DATABASE IF NOT EXISTS epicevents;
CREATE USER IF NOT EXISTS 'epic_events_user'@'localhost' IDENTIFIED BY 'YourSecurePassword123!';
GRANT ALL PRIVILEGES ON epicevents.* TO 'epic_events_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```
> [!WARNING]
> Make sure that :
> - the DATABASE name is the one defined in your .env file 
> - the USER name is the one defined in your .env file 
> - the PASSWORD is the one defined in your .env file 

### 2️⃣ Generate RSA Keys
```bash
poetry run python -m keys.generate_keys
```
> [!NOTE]
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

1. **Create a Sentry account** at [sentry.io](https://sentry.io) or log in to your existing account
2. **Create a new project** for EpicEvents CRM
3. **Copy the DSN** from your project settings
4. **Add the DSN** to your `.env` file:

Add to `.env`:
```env
SENTRY_DSN=https://your-public-key@sentry.io/your-project-id
```

5. **Restart the application** for changes to take effect

### 📊 Use Cases

| Scenario | Logged Data | Benefit |
|----------|-------------|---------|
| Collaborator actions | Main data | Monitor management |
| Contract signature | Contract info | Track history |
| Unhandled exceptions | Error details | Immediate alerts |

> [!TIP]
> Once configured, all errors will be visible in your Sentry dashboard.

---

## Features

### Interface and Navigation

The application uses **Textual** to provide a rich interface with:

- **Interactive menus** with cursor selection or keyboard shortcuts
- **Formatted display** with colors and custom styles
- **Notifications** for error and success messages
- **Real-time clock** in the header
- **Nord theme** for a pleasant visual experience

### 🔐 Authentication
| Feature | Description |
|---------|-------------|
| **Login** | Email/password auth with JWT |
| **Logout** | Invalidate local tokens |
| **Auto-refresh** | Automatic token refresh |
| **Persistent Session** | Secure local token storage |

![Login Screen](reports/login_screenshot.png)  
*Login interface with email and password fields*

![Authenticated View](reports/authenticated_screenshot.png)  
*Main application view after successful login*

### 👥 Customer Management
| Feature | Description | Allowed Roles |
|---------|-------------|---------------|
| **List** | View all customers | ADMIN, SALES, SUPPORT |
| **Create** | Add new customer | ADMIN, SALES |
| **Update** | Modify customer info | ADMIN, SALES |
| **View** | Detailed customer view | ADMIN, SALES, SUPPORT |

![Customer List](reports/customers_list_screenshot.png)  
*List view of all customers with search and filter options*

![Create Customer](reports/customer_create_screenshot.png)  
*Form for creating a new customer with contact information*

![Edit Customer](reports/customer_edit_screenshot.png)  
*Interface for updating customer information*

### 📄 Contract Management
| Feature | Description | Allowed Roles |
|---------|-------------|---------------|
| **List** | View all contracts | ADMIN, SALES, SUPPORT |
| **Create** | Add new contract | ADMIN, SALES |
| **Update** | Modify contract | ADMIN, SALES |

![Contract List](reports/contracts_list_screenshot.png)  
*List view of all contracts with status indicators*

![Create Contract](reports/contract_create_screenshot.png)  
*Form for creating a new contract with amount and customer selection*

![Edit Contract](reports/contract_update_screenshot.png)  
*Interface for changing contract data and status (pending, signed, cancelled)*

### 🎉 Event Management
| Feature | Description | Allowed Roles |
|---------|-------------|---------------|
| **List** | View all events | ADMIN, SALES, SUPPORT |
| **Create** | Add new event | ADMIN, SALES |
| **Update** | Modify event | ADMIN, SUPPORT |
| **Assign Support** | Assign representative | ADMIN |

![Event List](reports/events_list_screenshot.png)  
*List view of all events with dates and status*

![Create Event](reports/event_create_screenshot.png)  
*Form for creating a new event with location and date selection*

![Update Event](reports/event_update_screenshot.png)  
*Form for modifying existing event information*

### 👥 Collaborator Management
| Feature | Description | Allowed Roles |
|---------|-------------|---------------|
| **List** | View all collaborators | ADMIN, SALES, SUPPORT |
| **Create** | Add new collaborator | ADMIN |
| **Update** | Modify collaborator | ADMIN |
| **Delete** | Delete collaborator | ADMIN |

![Collaborators List](reports/collaborators_list_screenshot.png)  
*List view of all collaborators with department and role information*

![Create Collaborator](reports/collaborator_create_screenshot.png)  
*Form for creating a new collaborator with email and department selection*

![Update Collaborator](reports/collaborator_update_screenshot.png)  
*Interface for modifying collaborator information*

![Delete Collaborator](reports/collaborator_delete_screenshot.png)  
*Confirmation interface for deleting a collaborator*

---

## Technical Architecture

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

## Testing and Coverage

### 🚀 Run Tests
```bash
# All tests
poetry run pytest -vv

# Specific test file
poetry run pytest feature/tests/test_module.py -vv
```

Here are the pytest testing results:

![Pytest Test Results](reports/tests_results_screenshot.png)

> [!NOTE]
> Test results are based on the latest test run.

### Test Coverage Summary

To run the test suite and generate a coverage report:

```bash
# Run all tests with coverage and generate html report
poetry run coverage run -m pytest && poetry run coverage html 

# Open report
open htmlcov/index.html # macOS
start htmlcov/index.html # Windows
xdg-open htmlcov/index.html # Linux
```

> [!TIP]
> The coverage report will be generated in the `htmlcov/` directory. Open `htmlcov/index.html` in your browser to view detailed coverage information.

Here are the coverage results of the pytest tests in the current state of the project:

![Coverage Test Results](./reports/coverage_test_results_screenshot_1.png)
![Coverage Test Results](./reports/coverage_test_results_screenshot_2.png)

> [!NOTE]
> Coverage results are based on the latest test run.

---

## Authentication System

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

## RBAC Permission System

### 🎯 Roles & Permissions
| Role | 🎯 Responsibilities | 🔑 Key Permissions |
|------|--------------------|-------------------|
| **ADMIN** | Team & contract management | Full CRUD on collaborators, contracts, events |
| **SALES** | Customer & contract lifecycle | CRUD customers, contracts, read-only events |
| **SUPPORT** | Event planning | CRUD events, read-only customers/contracts |

---

## Code Quality & Linting

This project uses **Flake8** to ensure code compliance with [PEP 8](https://peps.python.org/pep-0008/) style guidelines.

### Generate an HTML Report

To generate and visualize Flake8 results in a browser:

```bash
# Generate a detailed HTML report
poetry run flake8

# Open the report in your browser
open flake8-report/index.html  # macOS
start flake8-report/index.html   # Windows
xdg-open flake8-report/index.html # Linux
```

### 📊 Flake8 Report

Here are the Flake8 results of the current state of the project:

![Flake8 Compliance Results](./reports/flake8_report_screenshot.png)

---

## Resources

- [Textual Documentation](https://textual.textualize.io/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [bcrypt Documentation](https://bcrypt.readthedocs.io/)
- [Cryptography Library](https://cryptography.io/)

---

## License

This project is licensed under a **custom Educational License** specifically designed for OpenClassrooms portfolio projects.

This project is developed as part of **Project 12** of the **Python Application Developer** path at OpenClassrooms. It is intended for **educational, portfolio, and professional demonstration purposes only**.

For full license details, see the [LICENSE](LICENSE) file.

### Quick Summary

**You are free to:**
- Use this code for personal learning and study
- Reference it in your portfolio or resume
- Demonstrate the application during job interviews
- Study, modify, and understand the codebase for educational purposes

**You may NOT:**
- Sell this code or use it in commercial products without explicit permission
- Remove or alter copyright notices
- Claim authorship or ownership of this software
- Distribute modified versions without maintaining the original license

**Copyright (c) 2026 Quentin Tellier** - All rights reserved.

---

## Authors

- **Quentin Tellier** - Developer
  - Email: [quentin.tellier@outlook.com](mailto:quentin.tellier@outlook.com)

---

## Acknowledgments

- [Textual](https://textual.textualize.io/) - CLI Framework
- The Python community
- All future contributors