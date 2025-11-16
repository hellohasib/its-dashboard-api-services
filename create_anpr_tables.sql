-- Create ANPR service tables manually
-- This is needed because auth-service and anpr-service share the same database

CREATE TABLE IF NOT EXISTS anpr_cameras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    model VARCHAR(255) NOT NULL,
    mac VARCHAR(32) NOT NULL UNIQUE,
    firmware_version VARCHAR(128),
    system_boot_time DATETIME,
    wireless BOOLEAN DEFAULT FALSE NOT NULL,
    dhcp_enable BOOLEAN DEFAULT TRUE NOT NULL,
    ipaddress VARCHAR(45) UNIQUE,
    netmask VARCHAR(45),
    gateway VARCHAR(45),
    device_name VARCHAR(255),
    device_location VARCHAR(255),
    INDEX idx_anpr_cameras_id (id),
    INDEX idx_anpr_cameras_mac (mac),
    INDEX idx_anpr_cameras_ipaddress (ipaddress)
);

CREATE TABLE IF NOT EXISTS lpr_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    camera_id INT,
    device_name VARCHAR(255),
    device_ip VARCHAR(45),
    device_model VARCHAR(255),
    device_firmware_version VARCHAR(128),
    event_type VARCHAR(50) NOT NULL,
    event_uid VARCHAR(255) NOT NULL UNIQUE,
    event_time DATETIME NOT NULL,
    event_description VARCHAR(512),
    plate_number VARCHAR(32) NOT NULL,
    plate_color VARCHAR(32),
    vehicle_color VARCHAR(32),
    vehicle_type VARCHAR(32),
    vehicle_brand VARCHAR(64),
    travel_direction VARCHAR(16),
    speed FLOAT,
    confidence INT,
    image_url VARCHAR(512),
    plate_roi_x INT,
    plate_roi_y INT,
    plate_roi_width INT,
    plate_roi_height INT,
    FOREIGN KEY (camera_id) REFERENCES anpr_cameras(id) ON DELETE SET NULL,
    INDEX idx_lpr_events_id (id),
    INDEX idx_lpr_events_camera_id (camera_id),
    INDEX idx_lpr_events_device_ip (device_ip),
    INDEX idx_lpr_events_event_time (event_time),
    INDEX idx_lpr_events_event_type (event_type),
    INDEX idx_lpr_events_event_uid (event_uid),
    INDEX idx_lpr_events_plate_number (plate_number)
);

CREATE TABLE IF NOT EXISTS list_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    event_id INT NOT NULL UNIQUE,
    matched_list VARCHAR(64),
    list_id VARCHAR(64),
    matched_by VARCHAR(64),
    confidence INT,
    description VARCHAR(255),
    FOREIGN KEY (event_id) REFERENCES lpr_events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attribute_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    event_id INT NOT NULL UNIQUE,
    vehicle_presence BOOLEAN,
    vehicle_make VARCHAR(64),
    vehicle_color VARCHAR(32),
    vehicle_size VARCHAR(32),
    vehicle_direction VARCHAR(16),
    FOREIGN KEY (event_id) REFERENCES lpr_events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS violation_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    event_id INT NOT NULL UNIQUE,
    violation_type VARCHAR(64),
    speed_limit FLOAT,
    measured_speed FLOAT,
    violation_status VARCHAR(32),
    violation_image VARCHAR(512),
    FOREIGN KEY (event_id) REFERENCES lpr_events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vehicle_counting_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    event_id INT NOT NULL UNIQUE,
    lane_id INT,
    counting_region VARCHAR(128),
    count_in INT,
    count_out INT,
    current_count INT,
    FOREIGN KEY (event_id) REFERENCES lpr_events(id) ON DELETE CASCADE
);

-- Update alembic_version to mark ANPR migration as complete
UPDATE alembic_version SET version_num = '4b2f19ae1c3d';

