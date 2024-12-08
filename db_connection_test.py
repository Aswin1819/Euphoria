import psycopg2

def test_database_connection():
    try:
        connection = psycopg2.connect(
            host="euphoriadatabase.czgeis4oszit.us-east-1.rds.amazonaws.com",
            database="euphoriadatabase",
            user="mysuperuser",
            password="mysuperuser",
            port="5432"
        )
        print("✅ Connection successful!")
        
        # Optional: Get database version
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"Database Version: {db_version}")
        
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed. Error: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()