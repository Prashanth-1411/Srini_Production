# Srinivasa Technology — Production Tracking & Heat Traceability System

A production-ready, LAN-only **MES / Production Tracking / Traceability System** for
**Srinivasa Technology** (CNC machining, hard-facing/grinding, supplying customers such as TVS).

The core requirement: answer **"For this finished part, which Heat Number did the steel come from?"**
and **"For this Heat Number, where did all the material go?"**

---

## 1. Technology Stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| Backend    | Python 3.12+, Django 5.x, Django ORM    |
| Database   | MySQL 8.x (InnoDB, utf8mb4) ONLY        |
| Frontend   | Django Templates, Bootstrap 5.3, Bootstrap Icons, Vanilla JS, Chart.js |
| PDF        | ReportLab                               |
| Excel      | openpyxl                                |
| Barcode/QR | python-barcode, qrcode, Pillow          |
| Deployment | Waitress (Windows LAN)                  |

> No SQLite, no PostgreSQL, no JSON/CSV storage for production data.

---

## 2. Project Structure

```
Inventory-Django/
├── manage.py
├── config/           # project settings, urls, wsgi/asgi
├── accounts/         # auth, groups, permissions
├── masters/          # supplier/customer/product/machine/furnace/shift masters
├── materials/        # inward, heat number, lots, bars, transactions, balance
├── production/       # CNC jobs, production lots, pieces
├── processes/        # grinding / hard-facing
├── heat_treatment/   # furnace batches
├── quality/          # QC inspection, rework, scrap
├── dispatch/         # dispatch & invoicing
├── traceability/     # traceability center, forward/backward tracing, certificates
├── reports/          # production/QC/dispatch reports, dashboards
├── audit/            # audit log
├── documents/        # MTC, drawings, QC certs, etc.
├── templates/        # Bootstrap templates
├── static/           # css/js/vendor (Bootstrap, icons, Chart.js)
├── media/            # uploaded documents
├── backups/          # automated MySQL + media backups
└── logs/             # application logs
```

---

## 3. Installation (Windows)

### 3.1 Prerequisites
- Python 3.12+ installed and on PATH
- MySQL 8.x installed and running on port 3306

### 3.2 One-time setup

```bat
:: create virtual environment
python -m venv .venv

:: activate and install requirements
.venv\Scripts\pip install -r requirements.txt
```

### 3.3 Create the MySQL database

```sql
CREATE DATABASE srinivasa_traceability CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'srinivasa_app'@'localhost' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON srinivasa_traceability.* TO 'srinivasa_app'@'localhost';
CREATE USER 'srinivasa_app'@'%' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON srinivasa_traceability.* TO 'srinivasa_app'@'%';
FLUSH PRIVILEGES;
```

Also grant the app user access to the test database used by Django tests:

```sql
GRANT ALL PRIVILEGES ON test_srinivasa_traceability.* TO 'srinivasa_app'@'localhost';
GRANT ALL PRIVILEGES ON test_srinivasa_traceability.* TO 'srinivasa_app'@'%';
FLUSH PRIVILEGES;
```

### 3.4 Configure environment

```bat
copy .env.example .env
```

Edit `.env` — set `SECRET_KEY`, `DB_PASSWORD`, `DEBUG`, `ALLOWED_HOSTS`, `SERVER-IP`.
**Never commit the real `.env`.**

### 3.5 Migrate, create admin, set up groups

```bat
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py createsuperuser
.venv\Scripts\python manage.py setup_groups
```

`setup_groups` creates the role groups `ADMIN, STORES, PRODUCTION, GRINDING,
HEAT_TREATMENT, QC, DISPATCH, MANAGEMENT` and assigns permissions.
**Operational groups have no DELETE permission** — records use status/correction instead.

---

## 4. Running

### Development
```bat
start.bat                       :: runs migrate + collectstatic + runserver 0.0.0.0:8000
```

### LAN production (Waitress)
```bat
.venv\Scripts\python -m waitress --listen=0.0.0.0:8000 config.wsgi:application
```

Other factory PCs access: `http://192.168.1.100:8000`

### Windows Firewall (allow only your private/LAN subnet)
```
New-NetFirewallRule -DisplayName "Django LAN 8000" -Direction Inbound -Protocol TCP `
  -LocalPort 8000 -Action Allow -Profile Private
```

---

## 5. Backups

```bat
backup.bat
```

Creates timestamped `mysqldump` SQL files + a media zip under:
- `backups/daily/`   (every day)
- `backups/weekly/`  (Sundays)
- `backups/monthly/` (1st of month)

Never overwrites existing backups. To restore:

```bat
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u srinivasa_app -p srinivasa_traceability < backups\daily\srinivasa_backup_YYYY-MM-DD_HHMMSS.sql
```

---

## 6. Testing

```bat
.venv\Scripts\python manage.py test
```

Covers: login, groups, permissions, material inward, heat-number preservation, bars,
transactions, material balance, CNC consumption, grinding, hard-facing, furnace batches,
QC, rework, scrap, HOLD/rejected-material prevention, dispatch prevention,
forward/backward traceability, Excel validation, audit logs, MySQL operations.

---

## 7. Development Phases

| Phase | Content                                   | Status |
|-------|-------------------------------------------|--------|
| 1     | Django foundation, MySQL config, auth, groups, base UI, dashboard, logging | ✅ built |
| 2     | Master data (suppliers, customers, products, machines, furnaces, shifts) | ✅ built |
| 3     | Raw material — heat numbers, lots, bars, transactions, balance | ✅ built |
| 4     | CNC jobs & production lots (material consumption, traceability) | ✅ built |
| 5     | Grinding / hard-facing process records    | ✅ built |
| 6     | Heat treatment furnace batches            | ✅ built |
| 7     | Quality control — inspection, rework, scrap | ✅ built |
| 8     | Dispatch & invoicing                      | ✅ built |
| 9     | Traceability center — forward/backward tracing | ✅ built |
| 10    | Reports (stock, production, quality, dispatch) | ✅ built |
| 11    | Deployment, backup, firewall              | pending |

---

## 8. Security Notes

- Django auth, password hashing, sessions, CSRF in use.
- MySQL password comes from `.env` only — never hardcoded.
- LAN-only; do not expose to the public internet.
- Important production records cannot be physically deleted by operators.
