# Handler 是用于善后解析的数据，并不负责写入数据。
import json

from crawlers.github.constants import redis_github_stars_list_key


class BaseGithubHandler:
    def __init__(self, redis_client):
        self.redis_client = redis_client


class GithubProfileHandler(BaseGithubHandler):
    def __init__(self, redis_client):
        super().__init__(redis_client)

    async def handle(self, result):
        if not result['next_page']:
            return

        await self.redis_client.execute('rpush', redis_github_stars_list_key, json.dumps(result['next_page']))


class GithubStarsHandler(BaseGithubHandler):
    def __init__(self, redis_client):
        super().__init__(redis_client)

    async def handle(self, result):
        pass


class GithubReposHandler(BaseGithubHandler):
    def __init__(self, redis_client):
        super().__init__(redis_client)

    async def handle(self, result):
        pass


class GithubFollowersHandler(BaseGithubHandler):
    def __init__(self, redis_client):
        super().__init__(redis_client)

    async def handle(self, result):
        pass


class GithubFollowingHandler(BaseGithubHandler):
    def __init__(self, redis_client):
        super().__init__(redis_client)

    async def handle(self, result):
        pass
