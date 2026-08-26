use std::fs;
use std::sync::Mutex;

pub struct Config {
    name: String,
    data: Mutex<Vec<u64>>,
}

impl Config {
    pub fn load(path: &str) -> Config {
        let content = fs::read_to_string(path).unwrap();
        let name = content.lines().next().unwrap().to_string();
        Config {
            name,
            data: Mutex::new(Vec::new()),
        }
    }

    pub fn name(&self) -> String {
        self.name.clone()
    }

    pub async fn refresh(&self) {
        let mut data = self.data.lock().unwrap();
        let fetched = fetch_remote().await;
        data.push(fetched);
    }
}

pub fn parse_port(raw: u64) -> u16 {
    raw as u16
}

async fn fetch_remote() -> u64 {
    42
}
