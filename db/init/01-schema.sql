CREATE TABLE service_requests (
    unique_key BIGINT PRIMARY KEY,
    created_date TIMESTAMP NOT NULL,
    closed_date TIMESTAMP,
    agency VARCHAR(10) NOT NULL,
    agency_name VARCHAR(50) NOT NULL,
    complaint_type VARCHAR(50) NOT NULL,
    descriptor VARCHAR(50),
    location_type VARCHAR(40),
    incident_zip VARCHAR(10),
    incident_address VARCHAR(255),
    street_name VARCHAR(255),
    cross_street_1 VARCHAR(255),
    cross_street_2 VARCHAR(255),
    intersection_street_1 VARCHAR(255),
    intersection_street_2 VARCHAR(255),
    address_type VARCHAR(20),
    city VARCHAR(100),
    landmark VARCHAR(255),
    facility_type VARCHAR(15),
    STATUS VARCHAR(15) NOT NULL,
    due_date TIMESTAMP,
    resolution_description TEXT,
    resolution_action_updated_date TIMESTAMP,
    community_board VARCHAR(25),
    borough VARCHAR(20) NOT NULL,
    x_coordinate INTEGER,
    y_coordinate INTEGER,
    park_facility_name VARCHAR(100),
    park_borough VARCHAR(20),
    school_name VARCHAR(100),
    school_number VARCHAR(20),
    school_region VARCHAR(20),
    school_code VARCHAR(20),
    school_phone_number VARCHAR(20),
    school_address VARCHAR(255),
    school_city VARCHAR(100),
    school_state VARCHAR(30),
    school_zip VARCHAR(20),
    school_not_found VARCHAR(10),
    school_or_citywide_complaint VARCHAR(50),
    vehicle_type VARCHAR(50),
    taxi_company_borough VARCHAR(50),
    taxi_pick_up_location VARCHAR(255),
    bridge_highway_name VARCHAR(100),
    bridge_highway_direction VARCHAR(50),
    road_ramp VARCHAR(50),
    bridge_highway_segment VARCHAR(100),
    garage_lot_name VARCHAR(100),
    ferry_direction VARCHAR(50),
    ferry_terminal_name VARCHAR(100),
    latitude NUMERIC(18, 15),
    longitude NUMERIC(18, 15),
    location VARCHAR(50)
);

CREATE INDEX idx_service_requests_created_date ON service_requests(created_date);

CREATE INDEX idx_service_requests_closed_date ON service_requests(closed_date);

CREATE INDEX idx_service_requests_agency ON service_requests(agency);

CREATE INDEX idx_service_requests_complaint_type ON service_requests(complaint_type);

CREATE INDEX idx_service_requests_agency_complaint ON service_requests(agency, complaint_type);

CREATE INDEX idx_service_requests_borough ON service_requests(borough);

CREATE INDEX idx_service_requests_coordinates ON service_requests(latitude, longitude)
WHERE
    latitude IS NOT NULL
    AND longitude IS NOT NULL;

CREATE INDEX idx_service_requests_status ON service_requests(STATUS);
