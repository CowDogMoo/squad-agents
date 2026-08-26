package calc

// Add returns the sum of a and b.
func Add(a, b int) int {
	return a + b
}

func Scale(v, factor int) int {
	if factor == 0 {
		return 0
	}
	return v * factor
}
