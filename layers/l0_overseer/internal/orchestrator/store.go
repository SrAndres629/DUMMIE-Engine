package orchestrator

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	_ "modernc.org/sqlite"
)

// StateStore gestiona la persistencia de los Floating Sessions
type StateStore struct {
	db *sql.DB
}

func NewStateStore(dbPath string) (*StateStore, error) {
	if dbPath == "" {
		aiwg := os.Getenv("DUMMIE_AIWG")
		if aiwg == "" {
			root := os.Getenv("DUMMIE_ROOT")
			if root == "" {
				root = "/home/jorand/Escritorio/DUMMIE Engine"
			}
			aiwg = filepath.Join(root, ".aiwg")
		}
		dbPath = filepath.Join(aiwg, "memory", "state.db")
	}

	// Asegurar directorio
	dir := filepath.Dir(dbPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return nil, err
	}

	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		return nil, err
	}

	store := &StateStore{db: db}
	if err := store.init(); err != nil {
		return nil, err
	}

	return store, nil
}

func (s *StateStore) init() error {
	query := `
	CREATE TABLE IF NOT EXISTS states (
		id TEXT PRIMARY KEY,
		goal TEXT,
		context TEXT,
		history TEXT,
		skills TEXT,
		errors TEXT,
		result TEXT,
		branch TEXT,
		status TEXT,
		friction REAL,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);`
	_, err := s.db.Exec(query)
	return err
}

func (s *StateStore) SaveState(state *State) error {
	state.Mu.RLock()
	defer state.Mu.RUnlock()

	ctxJSON, _ := json.Marshal(state.Context)
	histJSON, _ := json.Marshal(state.History)
	skillsJSON, _ := json.Marshal(state.Skills)
	
	errStrings := make([]string, len(state.Errors))
	for i, err := range state.Errors {
		if err != nil {
			errStrings[i] = err.Error()
		}
	}
	errorsJSON, _ := json.Marshal(errStrings)

	query := `
	INSERT INTO states (id, goal, context, history, skills, errors, result, branch, status, friction, updated_at)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
	ON CONFLICT(id) DO UPDATE SET
		goal = excluded.goal,
		context = excluded.context,
		history = excluded.history,
		skills = excluded.skills,
		errors = excluded.errors,
		result = excluded.result,
		branch = excluded.branch,
		status = excluded.status,
		friction = excluded.friction,
		updated_at = CURRENT_TIMESTAMP;`

	_, err := s.db.Exec(query,
		state.ID,
		state.Goal,
		string(ctxJSON),
		string(histJSON),
		string(skillsJSON),
		string(errorsJSON),
		state.Result,
		state.Branch,
		state.Status,
		state.Friction,
	)
	return err
}

func (s *StateStore) LoadAll() ([]*State, error) {
	rows, err := s.db.Query("SELECT id, goal, context, history, skills, errors, result, branch, status, friction FROM states")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var states []*State
	for rows.Next() {
		var st State
		var ctxStr, histStr, skillsStr, errsStr string
		err := rows.Scan(&st.ID, &st.Goal, &ctxStr, &histStr, &skillsStr, &errsStr, &st.Result, &st.Branch, &st.Status, &st.Friction)
		if err != nil {
			return nil, err
		}

		json.Unmarshal([]byte(ctxStr), &st.Context)
		json.Unmarshal([]byte(histStr), &st.History)
		json.Unmarshal([]byte(skillsStr), &st.Skills)
		
		var errStrings []string
		json.Unmarshal([]byte(errsStr), &errStrings)
		st.Errors = make([]error, len(errStrings))
		for i, s := range errStrings {
			st.Errors[i] = fmt.Errorf("%s", s)
		}
		
		states = append(states, &st)
	}
	return states, nil
}

func (s *StateStore) Close() error {
	return s.db.Close()
}
