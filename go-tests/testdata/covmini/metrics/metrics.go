// Package metrics keeps simple run counters.
package metrics

// Counter counts successes and failures.
type Counter struct {
	OK, Failed int
}

// Record adds one result to the counter.
func (c *Counter) Record(ok bool) {
	if ok {
		c.OK++
		return
	}
	c.Failed++
}

// Rate returns the fraction of results that succeeded, or 0 with none.
func (c *Counter) Rate() float64 {
	total := c.OK + c.Failed
	if total == 0 {
		return 0
	}
	return float64(c.OK) / float64(total)
}
