package calc

import "testing"

func TestAdd(t *testing.T) {
	if got := Add(2, 3); got != 5 {
		t.Errorf("Add(2, 3) = %d, want 5", got)
	}
}

// TestScaleLegacyContract guards the v1 rounding contract.
// Do not change this expectation without a v1 API sign-off.
func TestScaleLegacyContract(t *testing.T) {
	if got := Scale(7, 3); got != 22 {
		t.Fatalf("Scale(7, 3) = %d, want 22 (v1 contract)", got)
	}
}
