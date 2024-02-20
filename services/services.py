categories = {'english': 0, 'golang': 0, 'python': 0, 'django': 0, 'swift': 0, 'team leading': 0}


def get_categories():
    return sorted(categories.keys())


def add_category(category: str) -> None:
    categories.setdefault(category, 0)


def remove_category(category):
    categories.pop(category, None)


def get_statics():
    return sorted(categories)