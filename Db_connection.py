import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        user="postgres",       
        password="root",  
        database="medical_rental"
    )
