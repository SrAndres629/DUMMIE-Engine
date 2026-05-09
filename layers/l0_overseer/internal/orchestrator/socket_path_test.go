package orchestrator

import (
	"os"
	"path/filepath"
	"testing"
)

func TestResolveDummiedSocketPathUsesExplicitOverride(t *testing.T) {
	t.Setenv("DUMMIE_DUMMIED_SOCKET_PATH", "/tmp/explicit-dummied.sock")
	t.Setenv("DUMMIE_AIWG_DIR", "")

	if got := resolveDummiedSocketPath(); got != "/tmp/explicit-dummied.sock" {
		t.Fatalf("expected explicit override, got %q", got)
	}
}

func TestResolveDummiedSocketPathUsesCanonicalAIWGSocket(t *testing.T) {
	t.Setenv("DUMMIE_DUMMIED_SOCKET_PATH", "")
	t.Setenv("DUMMIE_AIWG_DIR", "/tmp/dummie-aiwg")

	want := filepath.Join("/tmp/dummie-aiwg", "sockets", "dummied.sock")
	if got := resolveDummiedSocketPath(); got != want {
		t.Fatalf("expected canonical aiwg socket %q, got %q", want, got)
	}
}

func TestResolveDummiedSocketPathFallsBackToWorkingDirectoryAIWG(t *testing.T) {
	t.Setenv("DUMMIE_DUMMIED_SOCKET_PATH", "")
	t.Setenv("DUMMIE_AIWG_DIR", "")

	cwd, err := os.Getwd()
	if err != nil {
		t.Fatalf("getwd: %v", err)
	}
	defer os.Chdir(cwd)

	tempDir := t.TempDir()
	if err := os.Chdir(tempDir); err != nil {
		t.Fatalf("chdir: %v", err)
	}

	want := filepath.Join(tempDir, ".aiwg", "sockets", "dummied.sock")
	if got := resolveDummiedSocketPath(); got != want {
		t.Fatalf("expected cwd fallback socket %q, got %q", want, got)
	}
}
