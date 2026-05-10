import kuzu

KUZU_DB_PATH = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/loci.db"

def migrate():
    db = kuzu.Database(KUZU_DB_PATH)
    conn = kuzu.Connection(db)
    
    print("Iniciando migración de esquema para Embeddings...")
    try:
        # Kùzu 0.11+ admite FLOAT[] para vectores
        conn.execute("ALTER TABLE MemoryNode4D ADD embedding FLOAT[]")
        print("Columna 'embedding' (FLOAT[]) añadida a MemoryNode4D.")
    except Exception as e:
        if "Duplicate column name" in str(e) or "already exists" in str(e).lower():
            print("La columna 'embedding' ya existe.")
        else:
            print(f"Error en migración: {e}")

if __name__ == "__main__":
    migrate()
