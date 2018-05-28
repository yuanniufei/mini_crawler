import json

from crawlers.stackoverflow.constants import redis_stackoverflow_tagged_key


class BaseStackOverflowHandler:
    def __init__(self, redis_client):
        self.redis_client = redis_client


class StackOverflowTagsHandler(BaseStackOverflowHandler):
    def __init__(self, redis_client):
        super().__init__(redis_client)

    async def handle(self, result):
        if not result['items']:
            return

        for tag in result['items']:
            data = {'tag': tag, 'page': 1}
            await self.redis_client.execute('rpush', redis_stackoverflow_tagged_key, json.dumps(data))


class StackOverflowTaggedHandler(BaseStackOverflowHandler):
    def __init__(self, redis_client, mysql_client):
        super().__init__(redis_client)
        self.mysql_client = mysql_client

    async def handle(self, result):
        pass
