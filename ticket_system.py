import sqlite3
import json


# Mimic payload from an API call returning tickets
mock_api_payload = """
    [
        {
            "api_ticket_ref": "INC-99412",
            "customer_name": "Global Logistics Corp",
            "issue": "BGP Flapping - Primary link dropping peers intermittently",
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
            "api_ticket_ref": "INC-99413",
            "customer_name": "Fintech Secure Pay",
            "issue": "IPsec VPN Tunnel Down between HQ and AWS VPC",
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
                    infra = ticket['infrastructure']

                    # Insert values into network_devices table
                    cursor.execute("""
                        INSERT OR IGNORE INTO network_devices (device_id, hostname, model, firmware_version, ip_address)
                        VALUES (?,?,?,?,?);
                    """, (
                        infra['device_id'],
                        infra['hostname'],
                        infra['model'],
                        infra['firmware'],
                        infra['ip']
                    ))

                    # Insert values into tickets table
                    cursor.execute("""
                        INSERT INTO tickets (external_ref_id, customer, device_id, issue_category, description, priority, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        ticket['api_ticket_ref'], 
                        ticket['customer_name'], 
                        infra['device_id'], 
                        ticket['category'], 
                        ticket['issue'], 
                        ticket['severity'], 
                        ticket['status'], 
                        ticket['timestamp']
                    ))

                    # Get last generated auto increment key
                    ticket_id = cursor.lastrowid

                    for history in ticket['tier_history']:
                        cursor.execute("""
                            INSERT INTO ticket_routing_history (ticket_id, assigned_tier, notes)
                            VALUES (?, ?, ?);
                        """, (
                            ticket_id,
                            history['tier'],
                            history['notes']
                        ))

            #Pipeline Error Handling
            except sqlite3.Error as e:
                print(f"Database pipeline error: {e}")
        
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
