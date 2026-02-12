#!/bin/bash

set -e

echo "=== Checking if CSV data needs to be imported ==="

until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

ROW_COUNT=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM service_requests;" 2>/dev/null || echo "0")
ROW_COUNT=$(echo "$ROW_COUNT" | xargs)

echo "Current row count in service_requests table: $ROW_COUNT"

if [ "$ROW_COUNT" -gt "0" ]; then
    echo "Data already exists in the database. Skipping CSV import."
    echo "To re-import data, delete the postgres_data volume and restart:"
    echo "  docker-compose down -v"
    echo "  docker-compose up -d"
    exit 0
fi

echo "=== Importing CSV data into PostgreSQL ==="
echo "This may take a few minutes for 364,559 rows..."

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" << 'EOF'
-- Import CSV data using COPY
-- The CSV has headers, so we skip the first line
COPY service_requests (
    unique_key, created_date, closed_date, agency, agency_name, complaint_type, 
    descriptor, location_type, incident_zip, incident_address, street_name, 
    cross_street_1, cross_street_2, intersection_street_1, intersection_street_2, 
    address_type, city, landmark, facility_type, status, due_date, 
    resolution_description, resolution_action_updated_date, community_board, 
    borough, x_coordinate, y_coordinate, park_facility_name, park_borough, 
    school_name, school_number, school_region, school_code, school_phone_number, 
    school_address, school_city, school_state, school_zip, school_not_found, 
    school_or_citywide_complaint, vehicle_type, taxi_company_borough, 
    taxi_pick_up_location, bridge_highway_name, bridge_highway_direction, 
    road_ramp, bridge_highway_segment, garage_lot_name, ferry_direction, 
    ferry_terminal_name, latitude, longitude, location
)
FROM '/data/311_Service_Requests_from_2010_to_Present.csv'
WITH (
    FORMAT CSV,
    HEADER true,
    NULL '',
    ENCODING 'UTF8'
);
EOF

FINAL_COUNT=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT COUNT(*) FROM service_requests;" | xargs)
echo "=== Import complete! Total rows: $FINAL_COUNT ==="
