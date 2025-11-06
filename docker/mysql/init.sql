-- Initialize database for Traffic System
CREATE DATABASE IF NOT EXISTS its_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create application user (if not using root)
-- CREATE USER IF NOT EXISTS 'traffic_db_user'@'%' IDENTIFIED BY '$!gM!nd00125680';
-- GRANT ALL PRIVILEGES ON its_dashboard.* TO 'traffic_db_user'@'%';
-- FLUSH PRIVILEGES;

