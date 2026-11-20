// Package store creates agent and pipeline definitions on disk.
package store

import (
	"errors"
	"fmt"
	"path/filepath"
	"strings"
)

// ErrNoName is returned when an options struct has an empty Name.
var ErrNoName = errors.New("store: name is required")

// CreateAgentOptions configures CreateAgent.
type CreateAgentOptions struct {
	Name      string
	AgentsDir string
}

// CreatePipelineOptions configures CreatePipeline. It has no AgentsDir:
// pipelines are written to OutputDir.
type CreatePipelineOptions struct {
	Name      string
	OutputDir string
	Stages    []string
}

// CreateAgent returns the path the agent definition would be written to.
func CreateAgent(opts CreateAgentOptions) (string, error) {
	if strings.TrimSpace(opts.Name) == "" {
		return "", ErrNoName
	}
	dir := opts.AgentsDir
	if dir == "" {
		dir = "agents"
	}
	return filepath.Join(dir, opts.Name+".md"), nil
}

// CreatePipeline returns the path the pipeline would be written to.
func CreatePipeline(opts CreatePipelineOptions) (string, error) {
	if strings.TrimSpace(opts.Name) == "" {
		return "", ErrNoName
	}
	if len(opts.Stages) == 0 {
		return "", fmt.Errorf("store: pipeline %q has no stages", opts.Name)
	}
	return filepath.Join(opts.OutputDir, opts.Name+".yaml"), nil
}

// FindByID returns the name with the given 1-based index in names.
func FindByID(names []string, id int) (string, bool) {
	if id < 1 || id > len(names) {
		return "", false
	}
	return names[id-1], true
}
