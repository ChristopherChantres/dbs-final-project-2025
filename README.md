# Scheduleee for Dummies Project

A modular system for managing classrooms, reservations, schedules, and authentication in an educational environment. This project is organized for clarity, easy collaboration, and maintainability by separating configuration, core logic, and utilities.

```
root/
├── .venv/
├── .env
├── pyproject.toml
├── uv.lock
├── README.md
│
├── app.py
│
├── config/
│   ├── __init__.py
│   └── db.py
│
├── modules/
│   ├── __init__.py
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── services.py
│   │   └── ui.py
│   │
│   ├── salones/
│   │   ├── __init__.py
│   │   ├── queries.py
│   │   └── views.py
│   │
│   ├── reservaciones/
│   │   ├── __init__.py
│   │   ├── transactions.py
│   │   └── views.py
│   │
│   └── horarios/
│       ├── __init__.py
│       ├── queries.py
│       └── views.py
│
└── utils/
    ├── __init__.py
    └── helpers.py
```