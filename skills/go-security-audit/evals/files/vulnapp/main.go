package main

import (
	"crypto/md5"
	"fmt"
	"net/http"
	"os/exec"
)

const dbPassword = "hunter2-prod-2024"

func trace(w http.ResponseWriter, r *http.Request) {
	host := r.URL.Query().Get("host")
	out, err := exec.Command("sh", "-c", "traceroute "+host).CombinedOutput()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	_, _ = w.Write(out)
}

func hashPassword(pw string) string {
	return fmt.Sprintf("%x", md5.Sum([]byte(pw)))
}

func main() {
	http.HandleFunc("/trace", trace)
	if err := http.ListenAndServe(":8080", nil); err != nil {
		fmt.Println(err)
	}
}
