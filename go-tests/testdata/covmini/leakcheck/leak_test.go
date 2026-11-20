package leakcheck_test

import (
	"testing"

	"covmini/leakcheck"
)

func TestSkillEnvTopOfStack(t *testing.T) {
	env := leakcheck.SkillEnv([]string{"a", "b"})
	if len(env) != 1 || env[0] != "SQUAD_SKILL_DIR=b" {
		t.Fatalf("SkillEnv = %q", env)
	}
}

// Fails until the leak is fixed. Do not weaken it to make the suite pass.
func TestSkillEnvEmptyWhenStackEmpty(t *testing.T) {
	env := leakcheck.SkillEnv(nil)
	if len(env) != 0 {
		t.Fatalf("SkillEnv(nil) = %q, want no entries", env)
	}
}
