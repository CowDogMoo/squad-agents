# Go Resources, Memory Safety, and Cryptography

Vulnerable and secure patterns for path traversal, memory safety, integer
overflow, `unsafe` and cgo, and cryptography in Go.

## Contents

- [Path Traversal](#path-traversal)
- [Memory Safety](#memory-safety)
- [Integer Overflow and Underflow](#integer-overflow-and-underflow)
- [The unsafe Package and cgo](#the-unsafe-package-and-cgo)
- [Cryptography](#cryptography)

## Path Traversal

The attacker controls a file path and escapes the intended directory.

```go
// Vulnerable: userInput could be "../../etc/passwd"
content, err := os.ReadFile("/var/www/files/" + userInput)
```

```go
// Go 1.24+: os.Root confines every operation to the directory
root, err := os.OpenRoot("/var/www/files")
if err != nil {
    return err
}
defer root.Close()
f, err := root.Open(userInput)          // Go 1.24+
content, err := root.ReadFile(userInput) // Go 1.25+
```

```go
// Go 1.20+: reject non-local paths
if !filepath.IsLocal(userInput) {
    return errors.New("path escapes directory")
}
fullPath := filepath.Join(basePath, userInput)
```

```go
// Any version: Clean + Join, then check the prefix
fullPath := filepath.Join(basePath, filepath.Clean(userInput))
if !strings.HasPrefix(fullPath, filepath.Clean(basePath)+string(os.PathSeparator)) {
    return errors.New("invalid path")
}
```

- Prefer `os.OpenRoot` where the module's Go version allows it. It also
  guards against symlinks that point outside the root, which the string
  checks do not.
- `os.OpenInRoot(dir, name)` (Go 1.24+) opens a single file inside a
  directory in one call.
- The prefix check must append the separator; `strings.HasPrefix(p, base)`
  alone accepts `/var/www/files-other`.
- CVE-2022-41722: on Windows, `filepath.Clean` could turn `a/../c:/b` into
  `c:\b`, enabling traversal. Fixed in Go 1.19.6 and 1.20.1.

Sources: [Traversal-resistant file APIs](https://go.dev/blog/osroot),
[golang/go#57274](https://github.com/golang/go/issues/57274)

## Memory Safety

Go bounds-checks slices and arrays (an out-of-range index panics rather than
corrupting memory), has no dangling pointers, and manages memory with a
garbage collector. Memory corruption in Go comes from `unsafe`, cgo, data
races, and bugs in the toolchain or standard library. Keep Go on a supported
release; examples of the last kind:

- **CVE-2021-38297**: buffer overflow via large arguments in a function
  invocation from a WASM module (`GOARCH=wasm GOOS=js`). Fixed in Go 1.16.9
  and 1.17.2.
- **CVE-2022-24675**: stack overflow in `encoding/pem` `Decode` on large PEM
  input. Fixed in Go 1.17.9 and 1.18.1.

## Integer Overflow and Underflow

Go does not check integer overflow. Unsigned arithmetic wraps modulo 2^n;
signed arithmetic wraps in two's complement. No error or panic is raised.

```go
var x uint8 = 255
x = x + 1 // x is now 0

// Dangerous: a wrapped size allocates too little
size := userInput1 * userInput2
buffer := make([]byte, size)

// Dangerous: wrapped offset with unsafe
ptr := unsafe.Pointer(uintptr(base) + userOffset)
```

Where overflow matters:

- Size and length calculations from input that feed `make`, slicing, or
  copy bounds.
- Values passed to system calls or written to the network in fixed-width
  fields, which can be silently truncated.
- Any arithmetic that feeds `unsafe`; bounds checking does not protect
  pointer arithmetic.

```go
func SafeAdd(a, b uint32) (uint32, error) {
    if a > math.MaxUint32-b {
        return 0, errors.New("integer overflow")
    }
    return a + b, nil
}

func SafeMultiply(a, b uint32) (uint32, error) {
    if a != 0 && b > math.MaxUint32/a {
        return 0, errors.New("integer overflow")
    }
    return a * b, nil
}
```

Use `math/big` when arbitrary precision is needed.

## The unsafe Package and cgo

`unsafe` bypasses the type system and Go's memory-safety guarantees. Combined
with input, it gives an attacker the same bugs as C.

```go
// Dangerous: offset from input
ptr := unsafe.Pointer(uintptr(unsafe.Pointer(&someVar)) + offset)

// Dangerous: reinterpreting memory
bits := *(*uint64)(unsafe.Pointer(&f))

// Low risk
size := unsafe.Sizeof(someStruct)
```

cgo rules to check:

- `C.CString` and `C.CBytes` allocate C memory that must be released with
  `C.free`; a missing free is a leak.
- C code must not keep a Go pointer to unpinned memory after the call
  returns; the garbage collector can move or free it.
- Pass Go values to C through `runtime/cgo.Handle` instead of raw pointers:

```go
h := cgo.NewHandle(goValue)
defer h.Delete()
// pass h (a uintptr) to C
```

Data races can break Go's memory safety even without `unsafe`, for example a
racy write to an interface or slice header. Run `go test -race` on code that
shares state across goroutines.

Flag every `unsafe` use that is unjustified, takes offsets or lengths from
input, or lacks a comment explaining why it is safe.

Sources: [unsafe](https://pkg.go.dev/unsafe),
[Golang data races to break memory safety](https://blog.stalkr.net/2015/04/golang-data-races-to-break-memory-safety.html)

## Cryptography

What to flag in Go code, and the fix:

| Finding | Fix |
|---------|-----|
| `math/rand` (or `math/rand/v2`) for tokens, keys, nonces, session IDs, or password-reset codes | `crypto/rand` (`rand.Read`, or `rand.Text()` on Go 1.24+) |
| MD5, SHA-1, or plain SHA-256 for password storage | `golang.org/x/crypto/bcrypt`, `scrypt`, or `argon2` |
| MD5 or SHA-1 for signatures or integrity | SHA-256 or SHA-512 |
| DES, 3DES, or RC4 | AES-GCM (`cipher.NewGCM`) |
| Reused or constant GCM nonce, or a nonce from `math/rand` | Fresh nonce from `crypto/rand` per message |
| RSA keys under 2048 bits | 2048 bits or more, or Ed25519 / ECDSA P-256 |
| Keys or IVs hardcoded in source | Load from the environment or a secret manager |
| `tls.Config{InsecureSkipVerify: true}`, or `MinVersion` below TLS 1.2 | Verify certificates; `MinVersion: tls.VersionTLS12` or later |

AES-GCM with a random nonce prepended to the ciphertext:

```go
func encrypt(plaintext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key) // 16, 24, or 32 bytes
    if err != nil {
        return nil, err
    }
    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }
    nonce := make([]byte, gcm.NonceSize())
    if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
        return nil, err
    }
    return gcm.Seal(nonce, nonce, plaintext, nil), nil
}

func decrypt(ciphertext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }
    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }
    if len(ciphertext) < gcm.NonceSize() {
        return nil, errors.New("ciphertext too short")
    }
    nonce, ct := ciphertext[:gcm.NonceSize()], ciphertext[gcm.NonceSize():]
    return gcm.Open(nil, nonce, ct, nil)
}
```

Password hashing with bcrypt (cost 10-12):

```go
hash, err := bcrypt.GenerateFromPassword([]byte(password), 12)
err = bcrypt.CompareHashAndPassword(hash, []byte(password)) // nil means match
```

Sources: [crypto](https://pkg.go.dev/crypto),
[Go Cryptography Security Audit](https://go.dev/blog/tob-crypto-audit)
