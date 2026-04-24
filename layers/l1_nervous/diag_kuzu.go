package main
import (
	"fmt"
	"github.com/kuzudb/go-kuzu"
	"os"
)
func main() {
	path := "./test_diag_kuzu"
	os.RemoveAll(path)
	db, err := kuzu.OpenDatabase(path, kuzu.DefaultSystemConfig())
	if err != nil {
		fmt.Printf("FAIL: %v\n", err)
		os.Exit(1)
	}
	defer db.Close()
	fmt.Println("SUCCESS")
}
