package skill

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"
	"io.dummie.v2/nervous/pkg/proto/skill"
)

type Blueprint struct {
	SkillID     string   `yaml:"skill_id"`
	Description string   `yaml:"description"`
	Invariants  []string `yaml:"invariants"`
}

func Hydrate(technicalSkill *skill.Skill, blueprintDir string) *skill.Skill {
	// Try to find a matching blueprint
	// Convention: .agents/skills/<technical_name>.yaml or <id>.yaml
	bpPath := filepath.Join(blueprintDir, fmt.Sprintf("%s.yaml", technicalSkill.Id))
	if _, err := os.Stat(bpPath); os.IsNotExist(err) {
		// Try fallback to technical name
		bpPath = filepath.Join(blueprintDir, fmt.Sprintf("%s.yaml", technicalSkill.TechnicalName))
	}

	if _, err := os.Stat(bpPath); err == nil {
		data, err := ioutil.ReadFile(bpPath)
		if err == nil {
			var bp Blueprint
			if err := yaml.Unmarshal(data, &bp); err == nil {
				// Apply hydration
				if bp.Description != "" {
					technicalSkill.Description = bp.Description
				}
				technicalSkill.Invariants = append(technicalSkill.Invariants, bp.Invariants...)
			}
		}
	}

	return technicalSkill
}
