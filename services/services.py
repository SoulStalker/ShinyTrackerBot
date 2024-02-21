from database.database import users_db
categories = {'english': 0, 'golang': 0, 'python': 0, 'django': 0, 'swift': 0, 'team leading': 0}


def get_categories():
    return sorted(users_db.values())


def add_category(category: str) -> None:
    users_db.setdefault(category, 0)


def remove_category(category):
    users_db.pop(category, None)


def get_statics():
    return sorted(users_db)
