import kuzu
import os

db_path = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/loci.db"
print(f"Opening {db_path}...")
try:
    db = kuzu.Database(db_path)
    conn = kuzu.Connection(db)
    print("Success!")
    results = conn.execute("MATCH (n) RETURN count(n)")
    print(f"Count: {results.get_next()[0]}")
except Exception as e:
    print(f"Error: {e}")
