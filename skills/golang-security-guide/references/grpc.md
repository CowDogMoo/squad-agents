# Go gRPC Security for Auditors

What a resources or injection auditor should flag in grpc-go code. gRPC
authentication design and rate limiting are out of scope here.

## Plaintext Transport (resources)

```go
// Vulnerable: both are plaintext
conn, err := grpc.Dial(addr, grpc.WithInsecure())
conn, err := grpc.NewClient(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))

// Vulnerable: server with no credentials
grpcServer := grpc.NewServer()
```

`grpc.WithInsecure()` is deprecated and sets the same transport credentials
as `insecure.NewCredentials()`, so flag both. Accept plaintext only for
loopback or test code.

```go
// Client with TLS
creds, err := credentials.NewClientTLSFromFile("server.crt", "")
conn, err := grpc.NewClient(addr, grpc.WithTransportCredentials(creds))

// Server with TLS
creds, err := credentials.NewServerTLSFromFile("server.crt", "server.key")
grpcServer := grpc.NewServer(grpc.Creds(creds))

// Server requiring client certificates (mTLS)
creds := credentials.NewTLS(&tls.Config{
    Certificates: []tls.Certificate{cert},
    ClientAuth:   tls.RequireAndVerifyClientCert,
    ClientCAs:    certPool,
})
```

A `tls.Config` passed to `credentials.NewTLS` gets the same checks as any
other: no `InsecureSkipVerify: true`, TLS 1.2 or later.

## Message Size and Stream Limits (resources)

- grpc-go servers default to a 4 MB receive limit. Flag code that raises
  `grpc.MaxRecvMsgSize` or `grpc.MaxCallRecvMsgSize` to very large values or
  derives them from input; large messages can exhaust memory.
- CVE-2023-44487 (HTTP/2 Rapid Reset): clients open and cancel streams
  quickly to exhaust the server. Set `grpc.MaxConcurrentStreams` and keep
  grpc-go on a patched release
  ([GHSA-m425-mq94-257g](https://github.com/grpc/grpc-go/security/advisories/GHSA-m425-mq94-257g)).

```go
grpcServer := grpc.NewServer(
    grpc.Creds(creds),
    grpc.MaxRecvMsgSize(4*1024*1024),
    grpc.MaxConcurrentStreams(100),
)
```

## Input Validation at RPC Boundaries (injection)

An RPC handler is a system boundary: request fields are untrusted input, the
same as HTTP parameters. Trace them into SQL, shell, and template sinks as in
`references/injection.md`. Projects that use protovalidate declare
constraints in the `.proto` file and enforce them in an interceptor; a
handler that skips the interceptor, or a field without constraints that
reaches a sink, is a finding.

Sources: [OWASP gRPC Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/gRPC_Security_Cheat_Sheet.html),
[gRPC authentication guide](https://grpc.io/docs/guides/auth/)
