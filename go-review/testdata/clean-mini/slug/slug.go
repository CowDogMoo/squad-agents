// Package slug turns titles into URL path segments.
package slug

import (
	"errors"
	"strconv"
	"strings"
	"unicode"
)

// ErrEmpty is returned when a title has no letters or digits to keep.
var ErrEmpty = errors.New("slug: title has no letters or digits")

// Make lowercases title, keeps letters and digits, and joins the words with
// single hyphens. It returns ErrEmpty when nothing is left.
func Make(title string) (string, error) {
	words := strings.FieldsFunc(title, func(r rune) bool {
		return !unicode.IsLetter(r) && !unicode.IsDigit(r)
	})
	if len(words) == 0 {
		return "", ErrEmpty
	}
	return strings.ToLower(strings.Join(words, "-")), nil
}

// Unique returns base, or base with the smallest numeric suffix ("-2",
// "-3", ...) that taken does not already hold.
func Unique(base string, taken map[string]bool) string {
	if !taken[base] {
		return base
	}
	for n := 2; ; n++ {
		candidate := base + "-" + strconv.Itoa(n)
		if !taken[candidate] {
			return candidate
		}
	}
}
