package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// versionCmd prints the version. It uses Run, which cannot return an error —
// this is a genuine best-practice violation that should become RunE.
var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Print the version",
	Run: func(_ *cobra.Command, _ []string) {
		fmt.Println("mini v0.1.0")
	},
}
