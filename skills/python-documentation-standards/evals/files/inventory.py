def calc_total(items, tax_rate=0.0):
    '''Returns the total price for all items.'''
    total = sum(item.price for item in items)
    total = total * (1 + tax_rate)  # multiply total by 1 plus tax_rate
    return total


def apply_discount(total, discount):
    """apply the discount"""
    # def old_apply(total):
    #     return total * 0.9
    return total * (1 - discount)


def validate_email(email):
    return "@" in email
