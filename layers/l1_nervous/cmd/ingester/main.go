package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"io.dummie.v2/nervous/internal/skill"
	skill_proto "io.dummie.v2/nervous/pkg/proto/skill"
)

func main() {
	registryPath := flag.String("registry", "", "Path to mcp_config.registry.json")
	blueprintDir := flag.String("blueprints", ".agents/skills", "Directory containing skill blueprints")
	outputPath := flag.String("output", "skills_registry.json", "Output file for ingested skills")
	flag.Parse()

	if *registryPath == "" {
		log.Fatal("Error: --registry is required")
	}

	// 1. Load Registry
	data, err := ioutil.ReadFile(*registryPath)
	if err != nil {
		log.Fatalf("Failed to read registry: %v", err)
	}

	var config skill.MCPConfig
	if err := json.Unmarshal(data, &config); err != nil {
		log.Fatalf("Failed to parse registry: %v", err)
	}

	var finalRegistry skill_proto.SkillRegistry

	// 2. Discover Tools per server
	for name, serverCfg := range config.MCPServers {
		fmt.Printf("Ingesting from server: %s...\n", name)
		tools, err := skill.DiscoverTools(name, serverCfg)
		if err != nil {
			fmt.Printf("  [!] Failed to discover tools for %s: %v\n", name, err)
			continue
		}

		for _, t := range tools {
			fmt.Printf("  - Found tool: %s\n", t.Name)
			
			// Transform to Proto Skill
			s := &skill_proto.Skill{
				Id:            fmt.Sprintf("%s.%s", name, t.Name),
				TechnicalName: t.Name,
				BackendServer: name,
				Description:   t.Description,
				JsonSchema:    fmt.Sprintf("%v", t.InputSchema), // In a real app, use JSON string
			}

			// 3. Hydrate with Blueprints
			hydrated := skill.Hydrate(s, *blueprintDir)
			finalRegistry.Skills = append(finalRegistry.Skills, hydrated)
		}
	}

	// 4. Save results
	outputData, err := json.MarshalIndent(finalRegistry, "", "  ")
	if err != nil {
		log.Fatalf("Failed to marshal output: %v", err)
	}

	if err := ioutil.WriteFile(*outputPath, outputData, 0644); err != nil {
		log.Fatalf("Failed to write output: %v", err)
	}

	fmt.Printf("\nIngestion complete! %d skills saved to %s\n", len(finalRegistry.Skills), *outputPath)
}
