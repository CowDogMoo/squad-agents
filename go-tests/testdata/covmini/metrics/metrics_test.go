package metrics_test

import (
	"testing"

	"covmini/metrics"
)

func TestRecord(t *testing.T) {
	var c metrics.Counter
	c.Record(true)
	c.Record(false)
	c.Record(true)
	if c.OK != 2 || c.Failed != 1 {
		t.Fatalf("Counter = %+v, want OK 2, Failed 1", c)
	}
}

func TestRate(t *testing.T) {
	tests := []struct {
		name string
		c    metrics.Counter
		want float64
	}{
		{"empty", metrics.Counter{}, 0},
		{"mixed", metrics.Counter{OK: 3, Failed: 1}, 0.75},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.c.Rate(); got != tt.want {
				t.Fatalf("Rate = %v, want %v", got, tt.want)
			}
		})
	}
}
