def is_teacher(user):
    return hasattr(user, "teacher")

def is_parent(user):
    return hasattr(user, "parent")
