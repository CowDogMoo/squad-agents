package cache

import (
	"sync"
	"time"
)

// Cache is a cache.
type Cache struct {
	mu      sync.Mutex
	entries map[string]entry
	ttl     time.Duration
}

type entry struct {
	value   string
	expires time.Time
}

// Returns the value stored under key and whether it is present.
func (c *Cache) Get(key string) (string, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	e, ok := c.entries[key]
	return e.value, ok && time.Now().Before(e.expires)
}

// Set sets the value.

func (c *Cache) Set(key, value string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.entries[key] = entry{value, time.Now().Add(c.ttl)}
}

func (c *Cache) Purge() int {
	n := 0
	for k, e := range c.entries {
		if time.Now().After(e.expires) {
			delete(c.entries, k)
			n++
		}
	}
	return n
}
