package store_test

import (
	"testing"

	"covmini/store"
)

func TestFindByID(t *testing.T) {
	names := []string{"review", "tests"}
	if got, ok := store.FindByID(names, 2); !ok || got != "tests" {
		t.Fatalf("FindByID(2) = %q, %v", got, ok)
	}
	if _, ok := store.FindByID(names, 3); ok {
		t.Fatal("FindByID(3) found a name past the end")
	}
}
