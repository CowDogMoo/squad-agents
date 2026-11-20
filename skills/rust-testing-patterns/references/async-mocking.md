# Async Tests and Mocking

Read when the module under test is async, or when a dependency sits behind a
trait and you need a hand-written mock. For `mockall` and extracting a trait
from concrete I/O, see `refactoring-for-testability.md`.

## Async Tests

### With Tokio

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn fetch_returns_data() {
        let client = MockClient::new();
        let result = fetch_data(&client).await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn fetch_timeout_returns_error() {
        let client = MockClient::with_delay(Duration::from_secs(60));
        let result = fetch_data(&client).await;
        assert!(matches!(result, Err(FetchError::Timeout)));
    }
}
```

### Key Rules

- Check Cargo.toml for the async runtime (tokio, async-std, smol).
- Use `#[tokio::test]` for tokio-based code.
- Use `#[tokio::test(flavor = "multi_thread")]` when tests need
  multi-threaded runtime.

## Mocking

### Trait-Based Mocking

The preferred Rust approach — define a trait and implement it for tests:

```rust
// In source code
pub trait Repository {
    fn find_by_id(&self, id: u64) -> Result<User, Error>;
}

pub struct Service<R: Repository> {
    repo: R,
}

// In test code
#[cfg(test)]
mod tests {
    use super::*;

    struct MockRepo {
        users: HashMap<u64, User>,
    }

    impl Repository for MockRepo {
        fn find_by_id(&self, id: u64) -> Result<User, Error> {
            self.users.get(&id)
                .cloned()
                .ok_or(Error::NotFound)
        }
    }

    #[test]
    fn service_returns_user() {
        let mut users = HashMap::new();
        users.insert(1, User { name: "Alice".into() });
        let repo = MockRepo { users };
        let service = Service { repo };

        let user = service.get_user(1).unwrap();
        assert_eq!(user.name, "Alice");
    }
}
```

### When to Mock

- External HTTP APIs
- Database connections
- File system operations (or use `tempfile`)
- Time-dependent operations

### When NOT to Mock

- Internal functions in the same module
- Pure functions with no side effects
- Types that are cheap to construct
