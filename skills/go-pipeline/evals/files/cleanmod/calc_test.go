package calc

import "testing"

func TestAdd(t *testing.T) {
	tests := []struct {
		name       string
		a, b, want int
	}{
		{"positive", 2, 3, 5},
		{"negative", -2, -3, -5},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := Add(tt.a, tt.b); got != tt.want {
				t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.want)
			}
		})
	}
}
