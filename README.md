# Scheduleee for Dummies

A modular classroom management system built with **Python (Streamlit)** and **MariaDB**, containerized with **Docker**.

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.

### How to Run
1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd dbs-final-project-2025
   ```

2. **Start the application**:
   ```bash
   docker compose up --build
   ```
   - The app will be available at: `http://localhost:8501`
   - The database runs on port `3307` (mapped from 3306).

3. **Stop the application**:
   ```bash
   docker compose down
   ```

## 📂 Project Structure

```text
root/
├── config/          # Database connection & global settings
├── modules/         # Business logic & UI components
│   ├── auth/        # Authentication (Login/Users)
│   ├── salones/     # Classroom management
│   ├── reservaciones/ # Reservation logic (Transactions)
│   └── horarios/    # Schedule viewing & management
├── utils/           # Helper functions
├── app.py           # Application entry point
├── Dockerfile       # Backend container configuration
└── docker-compose.yml # Service orchestration
```

## ⚙️ Configuration

Environment variables are managed via `docker-compose.yml`.
- **DB_USER**: `root`
- **DB_PASS**: `example_root_password`
- **DB_NAME**: `scheduleee`
