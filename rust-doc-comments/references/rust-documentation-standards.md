# Rust Documentation Standards

Comprehensive reference for writing idiomatic Rust documentation.

## Core Principles

- **Every public item should be documented.** `rustdoc` generates
  documentation from `///` and `//!` comments — undocumented public items
  produce warnings with `#![warn(missing_docs)]`.
- **Write for the user, not the implementer.** Focus on what the item does,
  what parameters mean, and what errors can occur.
- **The first line is the summary.** Rustdoc uses the first paragraph as the
  short description in module listings and search results. Make it count.
- **Complete sentences.** Every doc comment must be grammatically correct
  with proper punctuation.

## Doc Comment Syntax

### Item Documentation (`///`)

`///` documents the item that follows it:

```rust
/// Computes the factorial of `n`.
///
/// Returns `None` if the result would overflow `u64`.
///
/// # Examples
///
/// ```
/// assert_eq!(factorial(5), Some(120));
/// assert_eq!(factorial(0), Some(1));
/// ```
pub fn factorial(n: u64) -> Option<u64> {
```

### Module/Crate Documentation (`//!`)

`//!` documents the enclosing item (module or crate):

```rust
//! # My Crate
//!
//! `my_crate` provides utilities for processing data
//! efficiently with zero-copy parsing.
//!
//! ## Quick Start
//!
//! ```rust
//! use my_crate::Parser;
//! let parser = Parser::new();
//! let result = parser.parse(input)?;
//! ```
```

Place `//!` at the TOP of the file, before any `use` statements.

## Documentation by Declaration Type

### Functions

```rust
/// Parses the configuration from the given TOML string.
///
/// The input must be valid TOML. Unknown keys are ignored
/// for forward compatibility.
///
/// # Errors
///
/// Returns [`ConfigError::InvalidToml`] if the input is
/// not valid TOML syntax.
///
/// Returns [`ConfigError::MissingField`] if a required
/// field is absent.
///
/// # Examples
///
/// ```
/// let config = parse_config("timeout = 30")?;
/// assert_eq!(config.timeout, 30);
/// ```
pub fn parse_config(input: &str) -> Result<Config, ConfigError>
```

### Structs

```rust
/// Configuration for the HTTP client.
///
/// Use [`ClientConfig::builder`] for construction, or
/// [`ClientConfig::default`] for sensible defaults.
///
/// # Examples
///
/// ```
/// let config = ClientConfig::builder()
///     .timeout(Duration::from_secs(30))
///     .build()?;
/// ```
pub struct ClientConfig {
    /// Maximum time to wait for a response.
    pub timeout: Duration,
    /// Maximum number of retry attempts.
    pub max_retries: u32,
}
```

### Enums

```rust
/// The current state of a background task.
#[derive(Debug, Clone, PartialEq, Eq)]
#[non_exhaustive]
pub enum TaskState {
    /// The task is waiting to be scheduled.
    Pending,
    /// The task is currently executing.
    Running {
        /// When the task started.
        started_at: Instant,
    },
    /// The task completed successfully.
    Completed {
        /// The task's output.
        result: String,
    },
    /// The task failed with an error.
    Failed {
        /// The error that caused the failure.
        error: TaskError,
    },
}
```

### Traits

```rust
/// A repository for storing and retrieving users.
///
/// Implementations must be safe for concurrent access
/// from multiple threads.
pub trait UserRepository: Send + Sync {
    /// Returns the user with the given ID.
    ///
    /// # Errors
    ///
    /// Returns [`RepoError::NotFound`] if no user exists
    /// with the given ID.
    fn find_by_id(&self, id: UserId) -> Result<User, RepoError>;

    /// Stores the user, replacing any existing user with
    /// the same ID.
    fn save(&self, user: &User) -> Result<(), RepoError>;
}
```

### Constants and Static Items

```rust
/// Default timeout for HTTP requests, in seconds.
pub const DEFAULT_TIMEOUT: u64 = 30;

/// Maximum number of concurrent connections.
pub const MAX_CONNECTIONS: usize = 100;
```

### Type Aliases

```rust
/// A thread-safe reference-counted string.
pub type SharedString = Arc<str>;

/// Result type for database operations.
pub type DbResult<T> = Result<T, DbError>;
```

### Unsafe Functions

Every `pub unsafe fn` MUST have a `# Safety` section:

```rust
/// Reads `len` bytes starting at `ptr` into a new `Vec`.
///
/// # Safety
///
/// - `ptr` must be valid for reads of `len` bytes.
/// - `ptr` must be properly aligned for `u8`.
/// - The memory referenced by `ptr` must not be mutated
///   for the duration of this call.
/// - `len` must not exceed `isize::MAX`.
pub unsafe fn read_raw(ptr: *const u8, len: usize) -> Vec<u8>
```

## Special Sections

### `# Errors`

Document every error variant a function can return:

```rust
/// # Errors
///
/// - [`IoError`] if the file cannot be read.
/// - [`ParseError`] if the content is invalid JSON.
```

### `# Panics`

Document when a function panics:

```rust
/// # Panics
///
/// Panics if `index` is out of bounds.
```

### `# Safety`

Document invariants the caller must maintain for `unsafe` functions:

```rust
/// # Safety
///
/// The caller must ensure that `ptr` is non-null and
/// points to a valid, initialized `Widget`.
```

### `# Examples`

Provide runnable code examples:

````rust
/// # Examples
///
/// ```
/// use my_crate::Config;
///
/// let config = Config::from_str("key = \"value\"")?;
/// assert_eq!(config.get("key"), Some("value"));
/// # Ok::<(), my_crate::Error>(())
/// ```
````

Use `#` prefix for hidden lines (setup/teardown):

````rust
/// ```
/// # use my_crate::Config;
/// # fn main() -> Result<(), Box<dyn std::error::Error>> {
/// let config = Config::load("app.toml")?;
/// # Ok(())
/// # }
/// ```
````

## Intra-Doc Links

Use square brackets to link to other items:

```rust
/// Returns a [`Config`] parsed from the file.
///
/// See [`ConfigBuilder`] for programmatic construction.
/// Uses [`std::fs::read_to_string`] internally.
```

Link syntax:

- `[`TypeName`]` — link to a type (preferred short form)
- `[`module::function`]` — link to a function in another module
- `[`Trait::method`]` — link to a trait method
- `[`crate::module`]` — link to a module from anywhere
- `[`Struct.field_name`]` — link to a struct field (dot notation)

### Disambiguation

When a name is ambiguous (e.g., a module and type share a name), use
prefix syntax:

- `[struct@Foo]` — disambiguate to a struct
- `[fn@bar]` — disambiguate to a function
- `[macro@baz]` — disambiguate to a macro

The prefix is stripped in rendered output. Only use disambiguation when
rustdoc emits an ambiguity warning.

### Best Practices

- **Prefer short-form links.** `[`Config`]` over
  `[`crate::config::Config`]` when the type is in scope.
- **Do NOT use full paths** when the short form resolves unambiguously.

## Doc Test Attributes

| Attribute | Purpose | Use When |
|-----------|---------|----------|
| (none) | Compile and run | Default — example should work |
| `no_run` | Compile but don't run | Network access, file I/O, long-running |
| `should_panic` | Expect a panic | Demonstrating panic behavior |
| `compile_fail` | Expect compilation failure | Showing what won't compile |
| `ignore` | Skip entirely | Temporarily broken or platform-specific |

Example with `no_run`:

````rust
/// ```no_run
/// let pool = connect("postgres://localhost/mydb").await?;
/// ```
````

## Enforcing Documentation

Add `#![warn(missing_docs)]` at the crate root (`lib.rs`) to produce
compiler warnings for undocumented public items. For stricter enforcement,
use `#![deny(missing_docs)]`.

## Common Mistakes

### Mistake 1: Fragment Instead of Sentence

```rust
// BAD
/// the configuration

// GOOD
/// Application configuration loaded from disk.
```

### Mistake 2: Restating the Name

```rust
// BAD
/// Creates a new Config.
pub fn new() -> Config

// GOOD (skip it — `new` is self-documenting)
// OR if it has important details:
/// Creates a new [`Config`] with default values.
///
/// The default timeout is 30 seconds. Use
/// [`ConfigBuilder`] for custom configuration.
pub fn new() -> Config
```

### Mistake 3: Describing Implementation

```rust
// BAD
/// Iterates over the internal HashMap and collects
/// matching entries into a Vec using filter_map.

// GOOD
/// Returns all entries matching the given predicate.
```

### Mistake 4: Missing Error Documentation

```rust
// BAD
/// Loads the configuration file.
pub fn load(path: &Path) -> Result<Config, Error>

// GOOD
/// Loads the configuration from the file at `path`.
///
/// # Errors
///
/// Returns an error if the file does not exist or
/// contains invalid TOML.
pub fn load(path: &Path) -> Result<Config, Error>
```

### Mistake 5: Doc Comment Not Adjacent

```rust
// BAD — blank line separates comment from item
/// Does something useful.

pub fn useful() {}

// GOOD — comment directly above item
/// Does something useful.
pub fn useful() {}
```

### Mistake 6: Using `//` Instead of `///`

```rust
// BAD — regular comment, not a doc comment
// Parses the input.
pub fn parse(input: &str) {}

// GOOD — doc comment
/// Parses the input.
pub fn parse(input: &str) {}
```

## Deprecated Items

```rust
/// Processes the data.
///
/// # Deprecated
///
/// Use [`process_v2`] instead, which supports streaming.
#[deprecated(since = "0.5.0", note = "use `process_v2` instead")]
pub fn process(data: &[u8]) -> Vec<u8>
```

## Conditional Compilation

Doc comments on conditional items should note the condition:

```rust
/// Unix-specific file permission utilities.
///
/// This module is only available on Unix platforms.
#[cfg(unix)]
pub mod permissions {
```

## Quality Checklist

Before finishing, verify:

- [ ] Every `pub` function/method has a `///` doc comment
- [ ] Every `pub` struct/enum/trait has a `///` doc comment
- [ ] Every module has a `//!` doc comment
- [ ] Every `pub unsafe fn` has a `# Safety` section
- [ ] Every `Result`-returning public function has `# Errors`
- [ ] Every panicking function has `# Panics`
- [ ] Complex public functions have `# Examples`
- [ ] No fragments — all comments are complete sentences
- [ ] No redundant comments — every comment adds value
- [ ] Intra-doc links used for cross-references
- [ ] Comments are directly adjacent to declarations (no blank lines)
- [ ] All comment lines within 80 characters
