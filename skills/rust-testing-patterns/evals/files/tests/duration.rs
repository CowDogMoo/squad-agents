use std::time::Duration;

#[derive(Debug, PartialEq)]
pub enum ParseError {
    Empty,
    InvalidFormat,
}

pub fn parse_duration(input: &str) -> Result<Duration, ParseError> {
    if input.is_empty() {
        return Err(ParseError::Empty);
    }
    let (num, unit) = input.split_at(input.len() - 1);
    let value: u64 = num.parse().map_err(|_| ParseError::InvalidFormat)?;
    match unit {
        "s" => Ok(Duration::from_secs(value)),
        "m" => Ok(Duration::from_secs(value * 60)),
        "h" => Ok(Duration::from_secs(value * 3600)),
        _ => Err(ParseError::InvalidFormat),
    }
}
