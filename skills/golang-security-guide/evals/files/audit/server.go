package main

import (
	"crypto/md5"
	"database/sql"
	"fmt"
	"math/rand"
	"net/http"
	"os/exec"
)

const apiKey = "sk-live-9f8e7d6c5b4a3210"

func ping(w http.ResponseWriter, r *http.Request) {
	host := r.URL.Query().Get("host")
	out, _ := exec.Command("sh", "-c", "ping -c 1 "+host).Output()
	fmt.Fprintf(w, "%s", out)
}

func findUser(db *sql.DB, name string) (*sql.Rows, error) {
	return db.Query(fmt.Sprintf("SELECT id, email FROM users WHERE name = '%s'", name))
}

func hashPassword(pw string) string {
	return fmt.Sprintf("%x", md5.Sum([]byte(pw)))
}

func sessionToken() string {
	return fmt.Sprintf("%016x", rand.Uint64())
}

func main() {
	http.HandleFunc("/ping", ping)
	http.ListenAndServe(":8080", nil)
}
