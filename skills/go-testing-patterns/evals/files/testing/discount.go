package pricing

import "errors"

// ErrNegativePrice is returned when a price below zero is supplied.
var ErrNegativePrice = errors.New("price cannot be negative")

// ErrBadPercent is returned when percent is outside the 0-100 range.
var ErrBadPercent = errors.New("percent must be between 0 and 100")

// Discount returns price reduced by percent.
func Discount(price float64, percent int) (float64, error) {
	if price < 0 {
		return 0, ErrNegativePrice
	}
	if percent < 0 || percent > 100 {
		return 0, ErrBadPercent
	}
	return price * (100 - float64(percent)) / 100, nil
}

// Item is a purchasable thing.
type Item struct {
	name string
}

// Name returns the item name.
func (i Item) Name() string {
	return i.name
}
