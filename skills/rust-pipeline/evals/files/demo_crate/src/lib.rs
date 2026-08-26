pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

pub fn is_even(n: i32) -> bool {
    n % 2 == 0
}

pub fn clamp_percent(value: i32) -> i32 {
    value.max(0).min(100)
}
