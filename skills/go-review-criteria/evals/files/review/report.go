package report

import (
	"database/sql"
	"net/http"
	"os"
)

func UserReport(db *sql.DB, userID string) (*sql.Rows, error) {
	return db.Query("SELECT name, email FROM users WHERE id = '" + userID + "'")
}

func SaveReport(path string, data []byte) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	if _, err := f.Write(data); err != nil {
		return err
	}
	_ = f.Close()
	return nil
}

func FetchStatus(url string) (int, error) {
	resp, err := http.Get(url)
	if err != nil {
		return 0, err
	}
	defer func() { _ = resp.Body.Close() }()
	return resp.StatusCode, nil
}

func Describe(v any) string {
	return "report: " + v.(string)
}
