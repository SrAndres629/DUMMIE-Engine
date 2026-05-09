package orchestrator

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"strings"

	"io.dummie.v2/nervous/pkg/proto/skill"
)

// SkillManager gestiona el inventario de habilidades disponibles para el enjambre
type SkillManager struct {
	Registry *skill.SkillRegistry
}

func NewSkillManager(path string) (*SkillManager, error) {
	data, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("error leyendo registro de skills: %v", err)
	}

	var registry skill.SkillRegistry
	if err := json.Unmarshal(data, &registry); err != nil {
		return nil, fmt.Errorf("error parseando registro de skills: %v", err)
	}

	return &SkillManager{Registry: &registry}, nil
}

// FilterSkills retorna habilidades relevantes para un objetivo dado (Búsqueda Semántica básica)
func (sm *SkillManager) FilterSkills(query string) []*skill.Skill {
	var filtered []*skill.Skill
	query = strings.ToLower(query)

	for _, s := range sm.Registry.Skills {
		// Por ahora una búsqueda simple por palabras clave en descripción e ID
		if strings.Contains(strings.ToLower(s.Description), query) || 
		   strings.Contains(strings.ToLower(s.Id), query) {
			filtered = append(filtered, s)
		}
	}
	return filtered
}

// GetSkillById recupera una habilidad específica
func (sm *SkillManager) GetSkillById(id string) *skill.Skill {
	for _, s := range sm.Registry.Skills {
		if s.Id == id {
			return s
		}
	}
	return nil
}
