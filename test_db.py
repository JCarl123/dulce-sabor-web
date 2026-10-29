import pyodbc

try:
    conexion = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'
        'DATABASE=DulceSaborDB;'  # Asegúrate que sea el nombre correcto
        'Trusted_connection=yes;'
    )
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM PRODUCTO")
    resultado = cursor.fetchone()
    print("¡Conexión exitosa! Total de productos en la BD:", resultado[0])
    conexion.close()
except Exception as e:
    print("Error:", e)