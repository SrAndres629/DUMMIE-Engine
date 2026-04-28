package main
import (
	"fmt"
	"github.com/kuzudb/go-kuzu"
	"os"
)
func main() {
	path := "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/kuzu_data"
	// No borramos, queremos ver si abre el que existe
	db, err := kuzu.OpenDatabase(path, kuzu.DefaultSystemConfig())
	if err != nil {
		fmt.Printf("FAIL: %v\n", err)
		os.Exit(1)
	}
	defer db.Close()
	fmt.Println("SUCCESS")
}
