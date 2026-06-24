package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var gradeCmd = &cobra.Command{
	Use:   "grade",
	Short: "Grade an agent run",
	RunE:  runGrade,
}

func runGrade(cmd *cobra.Command, _ []string) error {
	agent, err := cmd.Flags().GetString("agent")
	if err != nil {
		return err
	}
	// Presence of --agent is already enforced here in RunE.
	if agent == "" {
		return fmt.Errorf("--agent is required")
	}
	fmt.Printf("grading agent %q\n", agent)
	return nil
}

func init() {
	gradeCmd.Flags().StringP("agent", "a", "", "Agent name (required for grading)")
}
