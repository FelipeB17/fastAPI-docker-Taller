from fastapi import FastAPI, Request
import os
import psycopg2

app = FastAPI()
DATA_FILE = "/data/notas.txt"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "usuario"),
    "password": os.getenv("DB_PASS", "password123"),
    "dbname": os.getenv("DB_NAME", "notasdb"),
}

def crear_tabla_si_no_existe():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id SERIAL PRIMARY KEY,
            contenido TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

crear_tabla_si_no_existe()

@app.get("/")
def leer_notas():
    if not os.path.exists(DATA_FILE):
        return {"notas": []}
    with open(DATA_FILE, "r") as f:
        return {"notas": f.read().splitlines()}

@app.post("/nota")
async def guardar_nota(request: Request):
    nota = await request.body()
    contenido = nota.decode()

    # Guardar en archivo
    with open(DATA_FILE, "a") as f:
        f.write(contenido + "\n")

    # Guardar en la base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("INSERT INTO notas (contenido) VALUES (%s)", (contenido,))
    conn.commit()
    cur.close()
    conn.close()

    return {"mensaje": "Nota guardada"}

@app.get("/notas-db")
def obtener_notas_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, contenido FROM notas")
    resultados = cur.fetchall()
    cur.close()
    conn.close()
    return {"notas": [{"id": r[0], "contenido": r[1]} for r in resultados]}

@app.get("/conteo")
def contar_notas():
    if not os.path.exists(DATA_FILE):
        return {"conteo": 0}
    with open(DATA_FILE, "r") as f:
        contenido = f.read()
        notas = contenido.split("\\n")  # ojo: doble backslash
        return {"conteo": len(notas)-1}
@app.get("/autor")
def obtener_autor():
    return {"autor": os.getenv("AUTOR", "Desconocido")}
