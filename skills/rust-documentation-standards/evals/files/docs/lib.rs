/// the configuration
pub struct Config {
    /// Maximum time to wait, in seconds.
    pub timeout: u64,
}

impl Config {
    /// Creates a new Config.
    pub fn new() -> Config {
        Config { timeout: 30 }
    }
}

pub fn load(path: &str) -> Result<Config, String> {
    std::fs::read_to_string(path)
        .map(|_| Config::new())
        .map_err(|e| e.to_string())
}

pub unsafe fn read_raw(ptr: *const u8, len: usize) -> Vec<u8> {
    std::slice::from_raw_parts(ptr, len).to_vec()
}
