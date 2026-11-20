# Refactoring for Testability

Read when writing the "Refactoring Recommendations" section of a coverage
report, or when I/O-heavy code blocks coverage and you need to recommend a
structural change. A test-only agent recommends these changes; it does not
make them in non-test code.

## Contents

- Trait extraction (hexagonal architecture, ports and adapters): before and
  after
- Testing with mockall
- Testing with manual mock structs
- Integration tests with testcontainers: Postgres, Redis
- When to use testcontainers versus mocks

## Trait Extraction for Testability (Hexagonal Architecture)

When I/O-heavy code blocks coverage, the fix is to separate business
logic from I/O by introducing traits. This is the "ports and adapters"
pattern.

### Before (untestable — logic coupled to Redis)

```rust
pub struct AgentCache {
    client: redis::Client,
}

impl AgentCache {
    pub async fn get_or_fetch(&self, id: &str) -> Result<Agent, Error> {
        let mut conn = self.client.get_multiplexed_async_connection().await?;
        if let Some(cached) = redis::cmd("GET").arg(id).query_async(&mut conn).await? {
            return Ok(serde_json::from_str(&cached)?);
        }
        // ... fetch from DB, cache it, return
    }
}
```

### After (testable — logic separated from I/O)

```rust
// Port (trait) — defines what the business logic needs
#[async_trait::async_trait]
pub trait CachePort: Send + Sync {
    async fn get(&self, key: &str) -> Result<Option<String>, CacheError>;
    async fn set(&self, key: &str, val: &str, ttl: u64) -> Result<(), CacheError>;
}

// Business logic — generic over the port
pub struct AgentService<C: CachePort> {
    cache: C,
}

impl<C: CachePort> AgentService<C> {
    pub async fn get_or_fetch(&self, id: &str) -> Result<Agent, Error> {
        if let Some(cached) = self.cache.get(id).await? {
            return Ok(serde_json::from_str(&cached)?);
        }
        // ... fetch, cache, return
    }
}

// Adapter (real implementation) — thin I/O wrapper
pub struct RedisCache { client: redis::Client }

#[async_trait::async_trait]
impl CachePort for RedisCache {
    async fn get(&self, key: &str) -> Result<Option<String>, CacheError> {
        let mut conn = self.client.get_multiplexed_async_connection().await?;
        Ok(redis::cmd("GET").arg(key).query_async(&mut conn).await?)
    }
    async fn set(&self, key: &str, val: &str, ttl: u64) -> Result<(), CacheError> {
        let mut conn = self.client.get_multiplexed_async_connection().await?;
        redis::cmd("SET").arg(key).arg(val).arg("EX").arg(ttl)
            .query_async(&mut conn).await?;
        Ok(())
    }
}
```

### Testing with mockall

When traits exist, use `mockall` to auto-generate mocks:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use mockall::mock;

    mock! {
        Cache {}
        #[async_trait::async_trait]
        impl CachePort for Cache {
            async fn get(&self, key: &str) -> Result<Option<String>, CacheError>;
            async fn set(&self, key: &str, val: &str, ttl: u64) -> Result<(), CacheError>;
        }
    }

    #[tokio::test]
    async fn cache_hit_returns_deserialized_agent() {
        let mut mock = MockCache::new();
        let agent = Agent { id: "a1".into(), name: "test".into() };
        let json = serde_json::to_string(&agent).unwrap();

        mock.expect_get()
            .with(mockall::predicate::eq("a1"))
            .returning(move |_| Ok(Some(json.clone())));

        let svc = AgentService { cache: mock };
        let result = svc.get_or_fetch("a1").await.unwrap();
        assert_eq!(result.name, "test");
    }

    #[tokio::test]
    async fn cache_miss_fetches_and_caches() {
        let mut mock = MockCache::new();
        mock.expect_get().returning(|_| Ok(None));
        mock.expect_set().times(1).returning(|_, _, _| Ok(()));

        let svc = AgentService { cache: mock };
        let result = svc.get_or_fetch("a1").await;
        // assert on the fetch + cache behavior
    }
}
```

### Testing with manual mock structs (no mockall)

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;
    use std::sync::Mutex;

    struct FakeCache {
        data: Mutex<HashMap<String, String>>,
    }

    #[async_trait::async_trait]
    impl CachePort for FakeCache {
        async fn get(&self, key: &str) -> Result<Option<String>, CacheError> {
            Ok(self.data.lock().unwrap().get(key).cloned())
        }
        async fn set(&self, key: &str, val: &str, _ttl: u64) -> Result<(), CacheError> {
            self.data.lock().unwrap().insert(key.into(), val.into());
            Ok(())
        }
    }
}
```

## Integration Tests with testcontainers

When you need to verify real I/O behavior (SQL query correctness, Redis
serialization), use `testcontainers` to spin up disposable containers.
These are slower (~2-5s startup) but catch bugs mocks cannot.

### Setup

```toml
# Cargo.toml [dev-dependencies]
testcontainers = "0.27"
testcontainers-modules = { version = "0.15", features = ["redis", "postgres"] }
```

### Postgres Example

```rust
use testcontainers::runners::AsyncRunner;
use testcontainers_modules::postgres::Postgres;

#[tokio::test]
async fn saves_and_retrieves_agent() {
    let container = Postgres::default()
        .with_db_name("test_db")
        .with_user("test")
        .with_password("test")
        .start()
        .await
        .expect("postgres container");

    let host = container.get_host().await.unwrap();
    let port = container.get_host_port_ipv4(5432).await.unwrap();
    let url = format!("postgres://test:test@{host}:{port}/test_db");

    let pool = sqlx::PgPool::connect(&url).await.unwrap();
    sqlx::migrate!("./migrations").run(&pool).await.unwrap();

    let repo = PgRepo::new(pool);
    repo.save(&agent).await.unwrap();
    let found = repo.find_by_id(agent.id).await.unwrap();
    assert_eq!(found.unwrap().name, "test-agent");
    // container auto-cleans on drop
}
```

### Redis Example

```rust
use testcontainers::runners::AsyncRunner;
use testcontainers_modules::redis::Redis;

#[tokio::test]
async fn redis_set_and_get() {
    let container = Redis::default()
        .start()
        .await
        .expect("redis container");

    let host = container.get_host().await.unwrap();
    let port = container.get_host_port_ipv4(6379).await.unwrap();
    let url = format!("redis://{host}:{port}");

    let client = redis::Client::open(url).unwrap();
    let cache = RedisCache { client };

    cache.set("key", "value", 60).await.unwrap();
    assert_eq!(cache.get("key").await.unwrap(), Some("value".into()));
}
```

### When to Use testcontainers vs Mocks

| Use mocks when... | Use testcontainers when... |
|---|---|
| Testing business logic that consumes a trait | Verifying SQL queries return correct results |
| Fast feedback loop needed | Validating migrations work |
| Testing error/retry paths | Testing serialization round-trips with real Redis |
| The trait boundary is clean | The adapter itself has complex logic |
