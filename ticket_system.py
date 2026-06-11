import sqlite3

# Establish connection to or create 'support_center.db' if doesnt exist
# Cursor is used to run SQL commands
connection = sqlite3.connect('support_center.db')
cursor = connection.cursor()


# Get table structure from 'schema.sql' and apply it to 'support_center.db'
def structure_table():
    try: 
        # Read the 'schema.sql' file and store as sql_script
        # Data from the file is stored as plain string
        with open('schema.sql', 'r') as file:
            #Read File
            sql_script = file.read()

            # Use cursor.executescript() instead of .execute() to parse multiple lines of SQL
            cursor.executescript(sql_script)
        
        # Apply the table layout to 'support_center.db'
        connection.commit()
    except:

        # Error message
        print("File not found or unreadable")
    finally:

        # Close connections for safety
        cursor.close()
        connection.close()
