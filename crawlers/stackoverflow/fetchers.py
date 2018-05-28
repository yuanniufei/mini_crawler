import json
import codecs

from crawlers.stackoverflow.extractors import StackOverflowTagsExtractor
from crawlers.stackoverflow.extractors import StackOverflowTaggedExtractor


class BaseStackOverflowFetcher:
    def __init__(self, http_session):
        self.headers = {
            'Host': 'stackoverflow.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.http_session = http_session

        self.tags_url_tpl = 'https://stackoverflow.com/tags?page={}&tab=popular'
        self.tagged_url_tpl = 'https://stackoverflow.com/questions/tagged/{}?page={}&sort=votes&pagesize=50'
        self.question_url_tpl = 'https://stackoverflow.com/questions/{}'
        self.url = None


class StackOverflowTagsFetcher(BaseStackOverflowFetcher):
    def __init__(self, http_session):
        super().__init__(http_session)

    async def before(self, redis_client, redis_key):
        page = await redis_client.execute('lpop', redis_key)
        if not page:
            if await redis_client.execute('llen', redis_key) == 0:
                return False
        else:
            page = page.decode('utf-8')
            self.url = self.tags_url_tpl.format(page)
        return True

    async def fetch(self):
        async with self.http_session.get(self.url, headers=self.headers) as response:
            html = await response.text()
            extractor = StackOverflowTagsExtractor(html)
            tags_data = extractor.parse()

            return {'items': tags_data, 'next_page': None}


class StackOverflowTaggedFetcher(BaseStackOverflowFetcher):
    def __init__(self, http_session):
        super().__init__(http_session)

    async def before(self, redis_client, redis_key):
        json_data = await redis_client.execute('lpop', redis_key)
        if not json_data:
            if await redis_client.execute('llen', redis_key) == 0:
                return False
        else:
            json_data = json_data.decode('utf-8')
            json_data = json.loads(json_data)

            tag = json_data['tag']
            page = json_data['page']
            self.url = self.tagged_url_tpl.format(tag, page)
        return True

    async def fetch(self):
        async with self.http_session.get(self.url, headers=self.headers) as response:
            html = await response.text()
            extractor = StackOverflowTaggedExtractor(html)
            questions_data = extractor.parse()

            return {'items': questions_data, 'next_page': None}


class StackOverflowQuestionFetcher(BaseStackOverflowFetcher):
    def __init__(self, http_session):
        super().__init__(http_session)

    async def before(self, redis_client, redis_key):
        url_suffix = await redis_client.execute('lpop', redis_key)
        if not url_suffix:
            if await redis_client.execute('llen', redis_key) == 0:
                return False
        else:
            url_suffix = url_suffix.decode('utf-8')
            self.url = self.question_url_tpl.format(url_suffix)
        return True

    async def fetch(self):
        pass
