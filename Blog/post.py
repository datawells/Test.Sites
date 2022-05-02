from mimetypes import init
from multiprocessing import AuthenticationError


class Post:
    def __init__(self, post_id, title, subtitle, body, author, date) -> None:
        self.id = post_id
        self.title = title
        self.subtitle = subtitle
        self.body = body
        self.author = author
        self.date = date