package routine_test

import (
	"testing"
	"time"

	"covmini/routine"
)

var base = time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)

// These names predate the repo's Test<Func>_<Case> convention. They stay as
// they are: renaming them is churn, not coverage.

func TestCatchupNoMissed(t *testing.T) {
	if got := routine.MissedRuns(base, base.Add(30*time.Minute), time.Hour); got != 0 {
		t.Fatalf("MissedRuns = %d, want 0", got)
	}
}

func TestCatchupThreeMissed(t *testing.T) {
	if got := routine.MissedRuns(base, base.Add(3*time.Hour), time.Hour); got != 3 {
		t.Fatalf("MissedRuns = %d, want 3", got)
	}
}

func TestCatchupZeroInterval(t *testing.T) {
	if got := routine.MissedRuns(base, base.Add(time.Hour), 0); got != 0 {
		t.Fatalf("MissedRuns = %d, want 0", got)
	}
}
