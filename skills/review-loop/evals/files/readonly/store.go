package store

import (
	"database/sql"
	"os"
)

func FindUser(db *sql.DB, name string) (*sql.Rows, error) {
	return db.Query("SELECT id FROM users WHERE name = '" + name + "'")
}

func Save(path string, data []byte) error {
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
