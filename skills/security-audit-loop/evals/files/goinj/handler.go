package goinj

import (
	"fmt"
	"math/rand"
	"net/http"
	"os/exec"
)

// Ping runs ping against the host named in the request.
func Ping(w http.ResponseWriter, r *http.Request) {
	host := r.URL.Query().Get("host")
	out, err := exec.Command("sh", "-c", "ping -c 1 "+host).CombinedOutput()
	if err != nil {
		http.Error(w, "ping failed", http.StatusBadGateway)
		return
	}
	w.Write(out)
}

// RequestID returns an identifier used only to correlate log lines.
func RequestID() string {
	return fmt.Sprintf("%08x", rand.Uint32())
}
