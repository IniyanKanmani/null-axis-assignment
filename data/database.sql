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

-- COMMENT ON TABLE service_requests IS 'NYC 311 Service Requests from 2010 to Present - Contains all service requests submitted by NYC residents';
--
-- COMMENT ON COLUMN service_requests.unique_key IS 'Unique identifier for each service request';
--
-- COMMENT ON COLUMN service_requests.created_date IS 'Date and time when the service request was created';
--
-- COMMENT ON COLUMN service_requests.closed_date IS 'Date and time when the service request was closed (NULL if still open)';
--
-- COMMENT ON COLUMN service_requests.agency IS 'Abbreviation of the agency responsible for handling the request';
--
-- COMMENT ON COLUMN service_requests.agency_name IS 'Full name of the agency responsible for handling the request';
--
-- COMMENT ON COLUMN service_requests.complaint_type IS 'Category of the complaint or request';
--
-- COMMENT ON COLUMN service_requests.descriptor IS 'Additional details about the complaint type';
--
-- COMMENT ON COLUMN service_requests.location_type IS 'Type of location where the incident occurred';
--
-- COMMENT ON COLUMN service_requests.incident_zip IS 'ZIP code where the incident occurred';
--
-- COMMENT ON COLUMN service_requests.incident_address IS 'Street address where the incident occurred';
--
-- COMMENT ON COLUMN service_requests.street_name IS 'Street name where the incident occurred';
--
-- COMMENT ON COLUMN service_requests.cross_street_1 IS 'First cross street near the incident';
--
-- COMMENT ON COLUMN service_requests.cross_street_2 IS 'Second cross street near the incident';
--
-- COMMENT ON COLUMN service_requests.intersection_street_1 IS 'First street of the intersection';
--
-- COMMENT ON COLUMN service_requests.intersection_street_2 IS 'Second street of the intersection';
--
-- COMMENT ON COLUMN service_requests.address_type IS 'Type of address (Address, Intersection, Blockface)';
--
-- COMMENT ON COLUMN service_requests.city IS 'City where the incident occurred';
--
-- COMMENT ON COLUMN service_requests.landmark IS 'Landmark near the incident location';
--
-- COMMENT ON COLUMN service_requests.facility_type IS 'Type of facility related to the request';
--
-- COMMENT ON COLUMN service_requests.status IS 'Current status of the service request (Open, Closed, Pending)';
--
-- COMMENT ON COLUMN service_requests.due_date IS 'Expected resolution date for the request';
--
-- COMMENT ON COLUMN service_requests.resolution_description IS 'Description of how the request was resolved';
--
-- COMMENT ON COLUMN service_requests.resolution_action_updated_date IS 'Date when the resolution action was last updated';
--
-- COMMENT ON COLUMN service_requests.community_board IS 'Community board district';
--
-- COMMENT ON COLUMN service_requests.borough IS 'Borough where the incident occurred';
--
-- COMMENT ON COLUMN service_requests.x_coordinate IS 'X coordinate in New York State Plane coordinate system';
--
-- COMMENT ON COLUMN service_requests.y_coordinate IS 'Y coordinate in New York State Plane coordinate system';
--
-- COMMENT ON COLUMN service_requests.park_facility_name IS 'Name of the park facility';
--
-- COMMENT ON COLUMN service_requests.park_borough IS 'Borough where the park is located';
--
-- COMMENT ON COLUMN service_requests.school_name IS 'Name of the school';
--
-- COMMENT ON COLUMN service_requests.school_number IS 'School number/identifier';
--
-- COMMENT ON COLUMN service_requests.school_region IS 'School region code';
--
-- COMMENT ON COLUMN service_requests.school_code IS 'School code';
--
-- COMMENT ON COLUMN service_requests.school_phone_number IS 'School phone number';
--
-- COMMENT ON COLUMN service_requests.school_address IS 'School address';
--
-- COMMENT ON COLUMN service_requests.school_city IS 'School city';
--
-- COMMENT ON COLUMN service_requests.school_state IS 'School state';
--
-- COMMENT ON COLUMN service_requests.school_zip IS 'School ZIP code';
--
-- COMMENT ON COLUMN service_requests.school_not_found IS 'Flag indicating if school was not found';
--
-- COMMENT ON COLUMN service_requests.school_or_citywide_complaint IS 'School or citywide complaint type';
--
-- COMMENT ON COLUMN service_requests.vehicle_type IS 'Type of vehicle involved';
--
-- COMMENT ON COLUMN service_requests.taxi_company_borough IS 'Borough of the taxi company';
--
-- COMMENT ON COLUMN service_requests.taxi_pick_up_location IS 'Taxi pickup location';
--
-- COMMENT ON COLUMN service_requests.bridge_highway_name IS 'Name of bridge or highway';
--
-- COMMENT ON COLUMN service_requests.bridge_highway_direction IS 'Direction of bridge/highway';
--
-- COMMENT ON COLUMN service_requests.road_ramp IS 'Road ramp identifier';
--
-- COMMENT ON COLUMN service_requests.bridge_highway_segment IS 'Bridge/highway segment identifier';
--
-- COMMENT ON COLUMN service_requests.garage_lot_name IS 'Name of garage or parking lot';
--
-- COMMENT ON COLUMN service_requests.ferry_direction IS 'Ferry direction';
--
-- COMMENT ON COLUMN service_requests.ferry_terminal_name IS 'Name of ferry terminal';
--
-- COMMENT ON COLUMN service_requests.latitude IS 'Latitude coordinate (WGS84)';
--
-- COMMENT ON COLUMN service_requests.longitude IS 'Longitude coordinate (WGS84)';
--
-- COMMENT ON COLUMN service_requests.location IS 'Location as text representation (latitude, longitude)';
