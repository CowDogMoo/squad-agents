package cmd

import "github.com/spf13/cobra"

// initCmd groups the init subcommands. It is a parent/container command: it
// only routes to subcommands, so it intentionally has no Run/RunE — Cobra
// prints help when invoked with no subcommand.
var initCmd = &cobra.Command{
	Use:   "init",
	Short: "Initialize resources",
	Long: `Initialize resources.

Available subcommands:
  agent    Create a new agent from templates`,
}

var initAgentCmd = &cobra.Command{
	Use:   "agent",
	Short: "Create a new agent",
	RunE: func(_ *cobra.Command, _ []string) error {
		return nil
	},
}

func init() {
	initCmd.AddCommand(initAgentCmd)
}
