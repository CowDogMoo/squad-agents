package slug_test

import (
	"errors"
	"testing"

	"clean-mini/slug"
)

func TestMake(t *testing.T) {
	tests := []struct {
		title   string
		want    string
		wantErr error
	}{
		{"Hello, World!", "hello-world", nil},
		{"  Go 1.26  release notes ", "go-1-26-release-notes", nil},
		{"Ünïcode Títle", "ünïcode-títle", nil},
		{"--- !!! ---", "", slug.ErrEmpty},
	}
	for _, tt := range tests {
		t.Run(tt.title, func(t *testing.T) {
			got, err := slug.Make(tt.title)
			if !errors.Is(err, tt.wantErr) {
				t.Fatalf("Make(%q) error = %v, want %v", tt.title, err, tt.wantErr)
			}
			if got != tt.want {
				t.Fatalf("Make(%q) = %q, want %q", tt.title, got, tt.want)
			}
		})
	}
}

func TestUnique(t *testing.T) {
	taken := map[string]bool{"post": true, "post-2": true}
	tests := []struct {
		base string
		want string
	}{
		{"fresh", "fresh"},
		{"post", "post-3"},
	}
	for _, tt := range tests {
		if got := slug.Unique(tt.base, taken); got != tt.want {
			t.Errorf("Unique(%q) = %q, want %q", tt.base, got, tt.want)
		}
	}
}
