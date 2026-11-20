# Go Injection and XSS

Vulnerable and secure patterns for SQL injection, command injection, and
cross-site scripting in Go.

## Contents

- [SQL Injection](#sql-injection)
- [Command Injection](#command-injection)
- [Cross-Site Scripting (XSS)](#cross-site-scripting-xss)

## SQL Injection

Untrusted data reaches the database as part of the query text.

```go
// Vulnerable
query := fmt.Sprintf("SELECT * FROM users WHERE username='%s'", username)
rows, err := db.Query(query)
```

```go
// Secure: pass values as arguments
rows, err := db.Query("SELECT * FROM users WHERE username=$1", username)

// Or a prepared statement
stmt, err := db.Prepare("SELECT * FROM users WHERE username=?")
if err != nil {
    return err
}
defer stmt.Close()
rows, err := stmt.Query(username)
```

- Use the `database/sql` methods that take arguments (`Query`, `QueryRow`,
  `Exec`, `Prepare`); the driver handles escaping.
- The placeholder depends on the driver (`?` for MySQL and SQLite, `$1` for
  PostgreSQL).
- gosec G201 (format string) and G202 (concatenation) flag the vulnerable
  shapes.

Source: [Avoiding SQL injection risk](https://go.dev/doc/database/sql-injection)

## Command Injection

Input passed to a shell allows arbitrary command execution.

```go
// Vulnerable
cmd := exec.Command("/bin/sh", "-c", "ls "+userInput)
cmd := exec.Command("bash", "-c", "myCommand "+userInput)
```

```go
// Secure: no shell, input as a separate argument
cmd := exec.Command("/path/to/myCommand", "myArg1", inputValue)
cmd := exec.Command("/bin/ls", "-la", filepath.Clean(userPath))

// If a shell is unavoidable, allowlist the whole input first
allowedCommands := map[string]bool{"list": true, "status": true}
if !allowedCommands[userInput] {
    return errors.New("invalid command")
}
cmd := exec.Command("/bin/sh", "-c", userInput)
```

- Avoid shell invocation. Go's standard library has no shell-escaping
  function, so quoting by hand is error-prone.
- `exec.Command` does not invoke a shell; each argument reaches the program
  as one argv entry. The risk returns only when the command string is handed
  to `sh -c`, `bash -c`, or another parser that re-splits it.
- Use allowlists of permitted commands or values, not denylists.

Source: [Command injection in Go (Semgrep cheat sheet)](https://semgrep.dev/docs/cheat-sheets/go-command-injection)

## Cross-Site Scripting (XSS)

User content rendered as HTML or JavaScript in the browser.

```go
// Vulnerable: text/template does no escaping
import "text/template"

tmpl := template.Must(template.New("page").Parse(`<div>{{.UserContent}}</div>`))
tmpl.Execute(w, data)

// Vulnerable: direct write
io.WriteString(w, "<div>"+userContent+"</div>")
```

```go
// Secure: html/template escapes by context
import "html/template"

tmpl := template.Must(template.New("page").Parse(`<div>{{.UserContent}}</div>`))
tmpl.Execute(w, data)
```

`html/template` escapes each value for its context: HTML text, attribute,
URL, JavaScript, and CSS.

```go
template := `
    <script>var data = {{.JSData}};</script>
    <div class="{{.CSSClass}}"><a href="{{.URL}}">{{.Text}}</a></div>
`
```

These types tell `html/template` the value is already safe and skip
escaping. Converting user data to any of them is XSS:

```go
template.HTML      // unescaped HTML
template.HTMLAttr  // unescaped HTML attribute
template.JS        // unescaped JavaScript
template.URL       // unescaped URL
template.CSS       // unescaped CSS
```

- Use `html/template`, never `text/template`, for HTML output.
- Treat any conversion of request data to the bypass types above as a
  finding.
- Set an explicit Content-Type on responses.
- Never write user content to the response without the template engine.
