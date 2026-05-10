package orchestrator

import (
	"os"
	"path/filepath"
)

func resolveDummiedSocketPath() string {
	if explicit := os.Getenv("DUMMIE_DUMMIED_SOCKET_PATH"); explicit != "" {
		return explicit
	}

	if aiwgDir := os.Getenv("DUMMIE_AIWG_DIR"); aiwgDir != "" {
		return filepath.Join(aiwgDir, "sockets", "dummied.sock")
	}

	if pwd, err := os.Getwd(); err == nil {
		return filepath.Join(pwd, ".aiwg", "sockets", "dummied.sock")
	}

	return "/tmp/dummied.sock"
}
