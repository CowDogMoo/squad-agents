package store

import (
	"errors"
	"os"
	"path/filepath"
)

var ErrLocked = errors.New("store: locked")

type Store struct {
	path   string
	locked bool
}

func New(path string) *Store {
	return &Store{path: path}
}

func (s *Store) String() string {
	return s.path
}

func (s *Store) Load(name string) ([]byte, error) {
	if s.locked {
		return nil, ErrLocked
	}
	return os.ReadFile(filepath.Join(s.path, name))
}

func (s *Store) TryLock() bool {
	if s.locked {
		return false
	}
	s.locked = true
	return true
}
