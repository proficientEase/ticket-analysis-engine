import sqlite3



# Get table structure from 'schema.sql' and apply it to 'support_center.db'
def structure_tables(db_path= 'support_center.db', schema_path='schema.sql'):
    
    # Keep connection variable at this scope
    connection = None

    try: 
        # Establish connection to or create 'support_center.db' if doesnt exist
        # Cursor is used to run SQL commands
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")

        with open(schema_path, 'r') as file:
            # Read the 'schema.sql' file and store as sql_script
            # Data from the file is stored as plain string
            sql_script = file.read()

            # Use cursor.executescript() instead of .execute() to parse multiple lines of SQL
            cursor.executescript(sql_script)
        
        # Apply the table layout to 'support_center.db'
        connection.commit()
        print("Database tables built")

    # Error Handling
    except FileNotFoundError:
        print(f"File '{schema_path}' not found.")
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
    structure_tables()