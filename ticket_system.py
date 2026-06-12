import sqlite3
import json


# Mimic payload from an API call returning tickets
mock_api_payload = """
    [
        {
            "external_ref_id": "INC-99412",
            "customer": "Global Logistics Corp",
            "description": "BGP Flapping - Primary link dropping peers intermittently",
            "category": "Routing / BGP",
            "severity": "P1",
            "status": "In_Progress",
            "timestamp": "2026-06-12T08:30:00Z",
            "tier_history": [
                {"tier": 1, "notes": "Customer reported total drop. Verified physical link up. Escalated."},
                {"tier": 2, "notes": "Analyzing BGP route maps and prefix lists."}
            ],
            "infrastructure": {
                "device_id": "RTR-NYC-01",
                "hostname": "nyc-core-router1",
                "model": "Cisco ASR 1002-X",
                "firmware": "IOS-XE 17.09.04a",
                "ip": "10.240.12.1"
            }
        },
        {
            "external_ref_id": "INC-99413",
            "customer": "Fintech Secure Pay",
            "description": "IPsec VPN Tunnel Down between HQ and AWS VPC",
            "category": "Security / VPN",
            "severity": "P2",
            "status": "Open",
            "timestamp": "2026-06-12T09:15:00Z",
            "tier_history": [
                {"tier": 1, "notes": "Phase 1 IKE negotiation failing. Escalated to Tier 2 Network Security."}
            ],
            "infrastructure": {
                "device_id": "FW-MIA-05",
                "hostname": "mia-edge-firewall5",
                "model": "Palo Alto PA-3220",
                "firmware": "PAN-OS 10.1.10",
                "ip": "172.16.85.4"
            }
        }
    ]
    """



def ticket_system(db_path='support_center.db'):
        
    # Keep connection variable at this scope
    connection = None

    try: 
        # Establish connection to or create 'support_center.db' if doesnt exist
        # Cursor is used to run SQL commands
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Get table structure from 'schema.sql' and apply it to 'support_center.db'
        def structure_tables(schema_path='schema.sql'):
            
            try:
                with open(schema_path, 'r') as file:
                    # Read the 'schema.sql' file and store as sql_script
                    # Data from the file is stored as plain string
                    sql_script = file.read()

                    # Use cursor.executescript() instead of .execute() to parse multiple lines of SQL
                    cursor.executescript(sql_script)
            
            except FileNotFoundError:
                print(f"File '{schema_path}' not found.")
                
            finally:
                # Apply the table layout to 'support_center.db'
                connection.commit()
                print("Database tables built")
        
        structure_tables()


        #Ingest ticket data from API payload and insert into tables
        def ingest_api_payload():
            
            try:

                # Parse the JSON string from payload into list of dictionaries
                tickets_data = json.loads(mock_api_payload) 
                print(f"Ingesting {len(tickets_data)} tickets")

                # Iterate the parsed ticket data and insert values into corresponding fields in DB
                for ticket in tickets_data:
                    
                    #ticket_id = ticket[]
                    #print(f"ticket id is {ticket_id}")

                    infra = ticket['infrastructure']

                    # Insert values into network_devices table
                    cursor.execute("""
                        INSERT OR IGNORE INTO network_devices (device_id, hostname, model, firmware_version, ip_address)
                        VALUES (?,?,?,?,?)
                        ON CONFLICT(device_id) DO UPDATE SET
                            hostname = excluded.hostname,
                            firmware_version = excluded.firmware_version,
                            ip_address = excluded.ip_address;
                    """, (
                        infra['device_id'],
                        infra['hostname'],
                        infra['model'],
                        infra['firmware'],
                        infra['ip']
                    ))

                    # Insert values into tickets table
                    cursor.execute("""
                        INSERT INTO tickets (external_ref_id, customer, device_id, category, description, severity, status, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(external_ref_id) DO UPDATE SET
                            status = excluded.status,
                            description = excluded.description,
                            severity = excluded.severity;
                    """, (
                        ticket['external_ref_id'], 
                        ticket['customer'], 
                        infra['device_id'], 
                        ticket['category'], 
                        ticket['description'], 
                        ticket['severity'], 
                        ticket['status'], 
                        ticket['timestamp']
                    ))

                    # Get last generated auto increment key
                    ticket_id = cursor.lastrowid
                    print(f"ticket id is {ticket_id}")
                    
                    # Create triage history trail
                    for history in ticket['tier_history']:
                        cursor.execute("""
                            INSERT INTO ticket_routing_history (ticket_id, assigned_tier, notes)
                            VALUES (?, ?, ?);
                        """, (
                            ticket_id,
                            history['tier'],
                            history['notes']
                        ))

            # Pipeline Error Handling
            except sqlite3.Error as e:
                print(f"Database pipeline error: {e}")
        
            finally:
                # Save changes to database
                connection.commit()
                print("Payload ingested and DB populated")
        
        ingest_api_payload()


    # Operational Error Handling
    except sqlite3.OperationalError as e:
        print(f"SQL operational error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    finally:
        # Close connections for safety
        # Otherwise I get scared 
        if connection:
            cursor.close()
            connection.close()


if __name__ == "__main__":
  ticket_system()
