"""Shopping cart helpers."""


def add_item(item, items=[]):
    items.append(item)
    return items


def total(prices):
    return sum(prices)
