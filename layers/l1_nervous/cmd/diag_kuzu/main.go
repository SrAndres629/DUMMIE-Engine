package main

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/kuzudb/go-kuzu"
)

func main() {
	// [HARDENING] Centralización de resolución de ruta canónica
	path := os.Getenv("DUMMIE_KUZU_DB_PATH")
	if path == "" {
		aiwg := os.Getenv("DUMMIE_AIWG_DIR")
		if aiwg == "" {
			// Intento de fallback a raíz relativa (DUMMIE_ROOT -> .aiwg)
			root := os.Getenv("DUMMIE_ROOT")
			if root == "" {
				root = "."
			}
			aiwg = filepath.Join(root, ".aiwg")
		}
		path = filepath.Join(aiwg, "memory", "loci.db")
	}

	fmt.Printf("Diagnosing Kuzu at: %s\n", path)
	db, err := kuzu.OpenDatabase(path, kuzu.DefaultSystemConfig())
	if err != nil {
		fmt.Printf("FAIL: %v\n", err)
		os.Exit(1)
	}
	defer db.Close()
	fmt.Println("SUCCESS: Database opened successfully.")
}
