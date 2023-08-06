from .base import get_post, get_async_post, SubredditBase
from .classes.post import Post


class Subreddit(SubredditBase):
    """
    This class is for getting posts from a subreddit
    """

    def get_post(self, subreddit) -> Post:
        """
        :return: The randomly selected post from the subreddit (hot)
        :rtype: Post
        """

        return get_post(self, rtype="hot", rfor=subreddit, slash="r")

    def get_top_post(self, subreddit) -> Post:
        """
        :return: The randomly selected post from the subreddit (This will return the TOP POST OF TODAY,
         not the top post of all time)
        :rtype: Post
        """

        return get_post(self, rtype="top", rfor=subreddit, slash="r")

    def get_new_post(self, subreddit) -> Post:
        """
        :return: The randomly selected post from the subreddit (new)
        :rtype: Post
        """

        return get_post(self, rtype="new", rfor=subreddit, slash="r")

    def get_controversial_post(self, subreddit) -> Post:
        """
        :return: The randomly selected post from the subreddit (controversial)
        :rtype: Post
        """

        return get_post(self, rtype="controversial", rfor=subreddit, slash="r")


class AsyncSubreddit(SubredditBase):
    """
    This class is for getting posts from a subreddit in an async way
    """

    async def get_post(self, subreddit) -> Post:
        """
        :return: The randomly selected post from the subreddit (hot)
        :rtype: Post
        """

        return await get_async_post(self, rtype="hot", rfor=subreddit, slash="r")

    async def get_top_post(self, subreddit) -> Post:
        """
        :return: The randomly selected post from the subreddit (This will return the TOP POST OF TODAY,
         not the top post of all time)
        :rtype: Post
        """

        return await get_async_post(self, rtype="top", rfor=subreddit, slash="r")

    async def get_new_post(self, subreddit) -> Post:
        """
        :return: Info about the randomly selected post from the subreddit (new)
        :rtype: Post
        """

        return await get_async_post(self, rtype="new", rfor=subreddit, slash="r")

    async def get_controversial_post(self, subreddit) -> Post:
        """
        :return: Info about the randomly selected post from the subreddit (controversial)
        :rtype: Post
        """

        return await get_async_post(self, rtype="controversial", rfor=subreddit, slash="r")
