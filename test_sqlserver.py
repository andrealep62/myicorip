import pyodbc

# 🔹 Inserisci qui i tuoi parametri reali
server = '172.16.0.10\\NTS'   # esempio: '192.168.1.100\\SQLEXPRESS'
database = 'ICOSHOP'
username = 'sa'
password = 'Sipi1Business'

# Stringa di connessione standard per SQL Server
conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # testiamo la vista
    cursor.execute("SELECT TOP 5 * FROM vw_AND_webappordini_articoli")

    rows = cursor.fetchall()
    for row in rows:
        print(row)

    conn.close()
except Exception as e:
    print("Errore di connessione:", e)
