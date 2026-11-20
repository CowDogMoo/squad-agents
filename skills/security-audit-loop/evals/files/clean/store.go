package clean

import "database/sql"

// Email returns the email address for the user with the given id.
func Email(db *sql.DB, id int64) (string, error) {
	var email string
	err := db.QueryRow("SELECT email FROM users WHERE id = $1", id).Scan(&email)
	return email, err
}
