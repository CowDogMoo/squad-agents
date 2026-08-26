import requests


def add_item(item, items=[]):
    items.append(item)
    return items


def get_user(db, user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    try:
        return db.execute(query)
    except:
        return None


async def fetch_profile(url):
    return requests.get(url).text
