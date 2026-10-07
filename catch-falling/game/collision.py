"""
collision: figures out whether a falling object is within the basket.
"""


def is_caught(basket_rect, obj):
    return (
        basket_rect.left <= obj.x <= basket_rect.right
        and basket_rect.top <= obj.y <= basket_rect.bottom
    )