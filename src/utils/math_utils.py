import math


def distance(x1, y1, x2, y2):
    """Calculate the distance between two points"""
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)


def normalize_vector(x, y):
    """Normalize a vector to unit length"""
    length = math.sqrt(x * x + y * y)
    if length == 0:
        return 0, 0
    return x / length, y / length


def vector_length(x, y):
    """Calculate the length of a vector"""
    return math.sqrt(x * x + y * y)


def dot_product(x1, y1, x2, y2):
    """Calculate the dot product of two vectors"""
    return x1 * x2 + y1 * y2


def angle_between(x1, y1, x2, y2):
    """Calculate the angle between two vectors in radians"""
    dot = dot_product(x1, y1, x2, y2)
    len1 = vector_length(x1, y1)
    len2 = vector_length(x2, y2)

    if len1 == 0 or len2 == 0:
        return 0

    # Clamp to avoid floating point errors
    cos_angle = max(-1.0, min(1.0, dot / (len1 * len2)))
    return math.acos(cos_angle)


def lerp(a, b, t):
    """Linear interpolation between a and b by t (0-1)"""
    return a + (b - a) * t


def clamp(value, min_value, max_value):
    """Clamp a value between min and max"""
    return max(min_value, min(value, max_value))
