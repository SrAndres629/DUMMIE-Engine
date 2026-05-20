package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

type HealthReport struct {
	Timestamp        string        `json:"timestamp"`
	Version          string        `json:"version"`
	PyTests          TestSummary   `json:"python_tests"`
	Procs            ProcessStatus `json:"processes"`
	Git              GitInfo       `json:"git"`
	L2ImportHealth   bool          `json:"l2_import_health"`
	FlatBrainModules int           `json:"flat_brain_modules"`
	CanonicalModules int           `json:"canonical_modules"`
}

type TestSummary struct {
	Passed int      `json:"passed"`
	Failed int      `json:"failed"`
	Errors int      `json:"errors"`
	Total  int      `json:"total"`
	FailedTests []string `json:"failed_tests,omitempty"`
}

type ProcessStatus struct {
	DummiedRunning bool `json:"dummied_running"`
	NatsRunning    bool `json:"nats_running"`
	OllamaRunning  bool `json:"ollama_running"`
}

type GitInfo struct {
	Branch string `json:"branch"`
	SHA    string `json:"sha"`
	Status string `json:"status"`
}

func main() {
	repoRoot := findRepoRoot()
	if repoRoot == "" {
		log.Fatal("Cannot find DUMMIE Engine root")
	}

	report := HealthReport{
		Timestamp: time.Now().UTC().Format(time.RFC3339),
	}

	report.Git = getGitStatus(repoRoot)
	report.Procs = checkProcesses()
	report.L2ImportHealth = checkL2Import(repoRoot)
	report.FlatBrainModules, report.CanonicalModules = countFlatBrainModules(repoRoot)

	out, _ := json.MarshalIndent(report, "", "  ")
	fmt.Println(string(out))
}

func findRepoRoot() string {
	cwd, _ := os.Getwd()
	for dir := cwd; dir != "/"; dir = filepath.Dir(dir) {
		if _, err := os.Stat(filepath.Join(dir, ".aiwg", "state")); err == nil {
			return dir
		}
		if _, err := os.Stat(filepath.Join(dir, "AGENTS.md")); err == nil {
			return dir
		}
	}
	return ""
}

func getGitStatus(root string) GitInfo {
	g := GitInfo{}

	if out, err := exec.Command("git", "-C", root, "branch", "--show-current").Output(); err == nil {
		g.Branch = strings.TrimSpace(string(out))
	}
	if out, err := exec.Command("git", "-C", root, "rev-parse", "--short", "HEAD").Output(); err == nil {
		g.SHA = strings.TrimSpace(string(out))
	}
	if out, err := exec.Command("git", "-C", root, "status", "--short").Output(); err == nil {
		lines := strings.Split(strings.TrimSpace(string(out)), "\n")
		if len(lines) == 1 && lines[0] == "" {
			g.Status = "clean"
		} else {
			g.Status = fmt.Sprintf("%d modified", len(lines))
		}
	}
	return g
}

func checkProcesses() ProcessStatus {
	p := ProcessStatus{}
	out, err := exec.Command("ps", "-eo", "cmd").Output()
	if err != nil {
		return p
	}
	lines := strings.ToLower(string(out))
	p.DummiedRunning = strings.Contains(lines, "dummied")
	p.NatsRunning = strings.Contains(lines, "nats-server")
	p.OllamaRunning = strings.Contains(lines, "ollama")
	return p
}

func checkL2Import(root string) bool {
	cmd := exec.Command("python3", "-c", `
from layers.l2_brain.domain.authority import AuthorityLevel
from layers.l2_brain.safe_fallbacks import FailClosedAuditor
from layers.l2_brain.daemon import DummieDaemon
print("ALL_OK")
`, "-S")
	cmd.Dir = root
	cmd.Env = append(os.Environ(), "PYTHONPATH="+root)
	out, err := cmd.Output()
	if err != nil {
		return false
	}
	return strings.TrimSpace(string(out)) == "ALL_OK"
}

func countFlatBrainModules(root string) (flat, canonical int) {
	flatDir := filepath.Join(root, "layers", "l2_brain", "flat_brain")
	entries, err := os.ReadDir(flatDir)
	if err == nil {
		for _, e := range entries {
			if !e.IsDir() && strings.HasSuffix(e.Name(), ".py") && !strings.HasPrefix(e.Name(), "__") {
				flat++
			}
		}
	}

	canonicalDirs := []string{"infrastructure", "governance", "cognition", "context",
		"memory", "mission", "strategic", "daemon", "heartbeat", "model_mesh",
		"embedding_mesh", "structural_hardening", "metacognition", "sdk", "proto"}

	for _, d := range canonicalDirs {
		dir := filepath.Join(root, "layers", "l2_brain", d)
		entries, err := os.ReadDir(dir)
		if err == nil {
			for _, e := range entries {
				if !e.IsDir() && strings.HasSuffix(e.Name(), ".py") && !strings.HasPrefix(e.Name(), "__") {
					canonical++
				}
			}
		}
	}
	return
}
