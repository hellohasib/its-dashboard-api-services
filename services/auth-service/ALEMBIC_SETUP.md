# Alembic Database Setup

## Database Connection Options

Alembic needs database credentials to connect. You have two options:

### Option 1: Use Environment Variables (Recommended)

Set environment variables before running Alembic:

```bash
export DB_HOST=localhost
export DB_PORT=3306  # or 3307 for Docker MySQL
export DB_NAME=its_dashboard
export DB_USER=root  # or your MariaDB user
export DB_PASS=your_password_here
```

Then run Alembic:
```bash
alembic revision --autogenerate -m "Initial auth service schema"
```

### Option 2: Update alembic.ini Directly

Edit `alembic.ini` and update the `sqlalchemy.url` line:

```ini
sqlalchemy.url = mysql+pymysql://root:your_password@localhost:3306/its_dashboard?charset=utf8mb4
```

Replace:
- `root` with your MariaDB username
- `your_password` with your MariaDB password
- `3306` with your MariaDB port (3307 if using Docker MySQL)
- `its_dashboard` with your database name

### Option 3: Use .env File

Create a `.env` file in the `auth-service` directory:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=its_dashboard
DB_USER=root
DB_PASS=your_password
```

Note: The `.env` file needs to be loaded. You can use `python-dotenv` or set variables manually.

## For Local MariaDB

If you're using your local MariaDB:

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=its_dashboard
export DB_USER=traffic_db_user  # or root
export DB_PASS=$!gM!nd00125680  # or your root password
```

## For Docker MySQL

If you're using Docker MySQL on port 3307:

```bash
export DB_HOST=localhost
export DB_PORT=3307
export DB_NAME=its_dashboard
export DB_USER=root
export DB_PASS=rootpassword  # or your Docker MySQL root password
```

## Verify Connection

Test the connection first:

```python
python -c "from services.shared.database.session import DATABASE_URL; print(DATABASE_URL)"
```

This will show you the connection string being used.

