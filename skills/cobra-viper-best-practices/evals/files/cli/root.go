package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var rootCmd = &cobra.Command{
	Use:   "shipit",
	Short: "Deploy environments",
}

var deployCmd = &cobra.Command{
	Use:   "deploy",
	Short: "Deploy the named environment",
	Run: func(cmd *cobra.Command, args []string) {
		env := args[0]
		if err := runDeploy(env); err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
	},
}

func init() {
	viper.SetConfigName("shipit")
	viper.AddConfigPath(".")
	_ = viper.ReadInConfig()
	deployCmd.Flags().String("cluster", "", "target cluster")
	_ = deployCmd.MarkFlagRequired("cluster")
	rootCmd.AddCommand(deployCmd)
}

func runDeploy(env string) error {
	fmt.Println("deploying", env)
	return nil
}
