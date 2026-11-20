// Package leakcheck builds the environment a skill subprocess runs with.
package leakcheck

// SkillEnv returns the environment entries for the skill stack. With an
// empty stack it should return none, but it still sets the variable: a known
// bug, tracked separately, that TestSkillEnvEmptyWhenStackEmpty exists to
// catch.
func SkillEnv(stack []string) []string {
	if len(stack) == 0 {
		return []string{"SQUAD_SKILL_DIR="}
	}
	return []string{"SQUAD_SKILL_DIR=" + stack[len(stack)-1]}
}
