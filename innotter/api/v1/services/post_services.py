from person.models import User
from post.models import Post


class PostServices:
    @classmethod
    def like_or_unlike_post(cls, post: Post, user: User) -> None:
        if user in post.users_liked.all():
            post.users_liked.remove(user.pk)
        else:
            post.users_liked.add(user.pk)
