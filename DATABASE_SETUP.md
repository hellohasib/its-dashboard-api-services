# Database Setup Options

You have MariaDB running locally on port 3306. Here are your options:

## Option 1: Use Docker MySQL on Different Port (Recommended for Development)

**Default configuration** - Docker MySQL will run on port **3307** (host) → 3306 (container)

This avoids conflicts with your local MariaDB.

### Setup:
1. Update your `.env` file:
```env
DB_PORT=3307
DB_NAME=its_dashboard
DB_HOST=localhost  # For local connections outside Docker
```

2. For services inside Docker, they'll connect to `mysql:3306` (service name)
3. For local development (outside Docker), use `localhost:3307`

### Start services:
```bash
docker-compose up -d
```

## Option 2: Use Your Existing Local MariaDB

If you prefer to use your existing MariaDB instance:

### Step 1: Create Database and User

Connect to your MariaDB:
```bash
mysql -u root -p
```

Then run:
```sql
CREATE DATABASE IF NOT EXISTS its_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'traffic_db_user'@'%' IDENTIFIED BY '$!gM!nd00125680';
GRANT ALL PRIVILEGES ON its_dashboard.* TO 'traffic_db_user'@'%';
FLUSH PRIVILEGES;
```

### Step 2: Configure MariaDB to Allow Remote Connections

Edit MariaDB config (usually `/etc/my.cnf` or `/usr/local/etc/my.cnf`):
```ini
[mysqld]
bind-address = 0.0.0.0  # Allow connections from Docker containers
```

Or for macOS Homebrew installation:
```bash
# Edit: /opt/homebrew/etc/my.cnf or /usr/local/etc/my.cnf
```

Restart MariaDB:
```bash
brew services restart mariadb
# or
sudo systemctl restart mariadb
```

### Step 3: Use Local DB Compose Override

Use the local database compose file:
```bash
docker-compose -f docker-compose.yml -f docker-compose.local-db.yml up -d
```

This will:
- Skip starting the MySQL container
- Connect services to `host.docker.internal:3306` (your local MariaDB)

### Step 4: Update .env
```env
DB_HOST=host.docker.internal  # For Docker services
# OR
DB_HOST=localhost  # For local development
DB_PORT=3306
DB_NAME=its_dashboard
DB_USER=traffic_db_user
DB_PASS=$!gM!nd00125680
```

## Option 3: Stop Local MariaDB Temporarily

If you want to use Docker MySQL only:

### macOS (Homebrew):
```bash
brew services stop mariadb
```

### Start Docker MySQL:
```bash
docker-compose up -d mysql
```

### To restart MariaDB later:
```bash
brew services start mariadb
```

## Verify Database Connection

### For Docker MySQL (port 3307):
```bash
docker-compose exec mysql mysql -uroot -p its_dashboard
# Or from local machine:
mysql -h localhost -P 3307 -u root -p its_dashboard
```

### For Local MariaDB:
```bash
mysql -u traffic_db_user -p its_dashboard
```

## Troubleshooting

### Port Already in Use
- **Error**: `bind: address already in use`
- **Solution**: Use Option 1 (different port) or Option 2 (local DB)

### Can't Connect from Docker to Host
- **Error**: `Can't connect to MySQL server on host.docker.internal`
- **Solution**: 
  - Ensure MariaDB is bound to `0.0.0.0` not just `127.0.0.1`
  - Check firewall settings
  - Verify user has remote access: `'traffic_db_user'@'%'`

### Connection Refused
- Check if MariaDB is running: `brew services list`
- Verify port: `lsof -i :3306`
- Check MariaDB logs: `/opt/homebrew/var/mysql/*.err`

## Recommended for Development

**Option 1** is recommended because:
- ✅ Isolated development environment
- ✅ Easy to reset/clean up
- ✅ No conflicts with local services
- ✅ Consistent across team members

## Recommended for Production-like Testing

**Option 2** is better if:
- You want to test with your actual database setup
- You need to access the database from other local tools
- You prefer managing one database instance

