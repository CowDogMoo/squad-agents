// Package routine decides how a scheduled routine catches up on runs it
// missed while the scheduler was down.
package routine

import (
	"errors"
	"time"
)

// ErrBadPolicy is returned for a catch-up policy Plan does not know.
var ErrBadPolicy = errors.New("routine: unknown catch-up policy")

// MissedRuns counts the runs due strictly after last and at or before now.
func MissedRuns(last, now time.Time, every time.Duration) int {
	if every <= 0 || !now.After(last) {
		return 0
	}
	return int(now.Sub(last) / every)
}

// NextRun returns the first run time after now on the schedule anchored at
// last.
func NextRun(last, now time.Time, every time.Duration) time.Time {
	if every <= 0 {
		return now
	}
	n := MissedRuns(last, now, every)
	return last.Add(time.Duration(n+1) * every)
}

// Plan returns how many of the missed runs to execute under policy: "all"
// runs every one, "latest" runs one, and "skip" runs none.
func Plan(missed int, policy string) (int, error) {
	switch policy {
	case "all":
		return missed, nil
	case "latest":
		if missed > 0 {
			return 1, nil
		}
		return 0, nil
	case "skip":
		return 0, nil
	default:
		return 0, ErrBadPolicy
	}
}
