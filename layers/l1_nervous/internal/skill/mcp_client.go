package skill

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
)

func DiscoverTools(name string, cfg ServerConfig) ([]ToolDefinition, error) {
	if cfg.Disabled {
		return nil, nil
	}

	cmd := exec.Command(cfg.Command, cfg.Args...)
	
	// Set working directory to project root if available
	if rootDir := os.Getenv("DUMMIE_ROOT_DIR"); rootDir != "" {
		cmd.Dir = rootDir
	}
	
	// Setup env
	cmd.Env = os.Environ()
	for k, v := range cfg.Env {
		cmd.Env = append(cmd.Env, fmt.Sprintf("%s=%s", k, v))
	}

	stdin, err := cmd.StdinPipe()
	if err != nil {
		return nil, err
	}
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, err
	}
	cmd.Stderr = os.Stderr

	if err := cmd.Start(); err != nil {
		return nil, err
	}
	defer cmd.Process.Kill()

	reader := bufio.NewReader(stdout)

	// 1. Initialize
	initReq := JSONRPCRequest{
		JSONRPC: "2.0",
		ID:      1,
		Method:  "initialize",
		Params: map[string]interface{}{
			"protocolVersion": "2024-11-05",
			"capabilities":    map[string]interface{}{},
			"clientInfo":      map[string]string{"name": "DummieIngester", "version": "1.0.0"},
		},
	}
	if err := sendRequest(stdin, initReq); err != nil {
		return nil, err
	}
	if _, err := readResponse(reader); err != nil {
		return nil, err
	}

	// 2. List Tools
	listReq := JSONRPCRequest{
		JSONRPC: "2.0",
		ID:      2,
		Method:  "tools/list",
		Params:  map[string]interface{}{},
	}
	if err := sendRequest(stdin, listReq); err != nil {
		return nil, err
	}
	
	resp, err := readResponse(reader)
	if err != nil {
		return nil, err
	}

	var result ToolsListResult
	b, _ := json.Marshal(resp.Result)
	if err := json.Unmarshal(b, &result); err != nil {
		return nil, err
	}

	return result.Tools, nil
}

func sendRequest(w io.Writer, req JSONRPCRequest) error {
	b, err := json.Marshal(req)
	if err != nil {
		return err
	}
	_, err = w.Write(append(b, '\n'))
	return err
}

func readResponse(r *bufio.Reader) (*JSONRPCResponse, error) {
	line, err := r.ReadBytes('\n')
	if err != nil {
		return nil, err
	}
	var resp JSONRPCResponse
	if err := json.Unmarshal(line, &resp); err != nil {
		return nil, err
	}
	return &resp, nil
}
