def divide(a, b):
    """Divide a by b."""
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b


def classify(n):
    """Classify an integer as negative, zero, or positive."""
    if n < 0:
        return "negative"
    if n == 0:
        return "zero"
    return "positive"
