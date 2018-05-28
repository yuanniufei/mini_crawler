# GithubProfileFetcher 是用于抓取个人主页的相关信息，包括
# Profile、Stars、Repositories、Followers、Following
# TODO 各个 Fetcher 的分页处理
# TODO 需要处理请求时的各种异常
import json
import codecs
from crawlers.github.extractors import GithubStarsExtractor
from crawlers.github.extractors import GithubProfileExtractor


class BaseGithubFetcher:
    def __init__(self, http_session):
        self.headers = {
            'Host': 'github.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.http_session = http_session

        self.profile_url_tpl = 'https://github.com/{}'
        self.stars_url_tpl = 'https://github.com/{}?tab=stars&page={}'
        self.repos_url_tpl = 'https://github.com/{}?tab=repositories&page={}'
        self.followers_url_tpl = 'https://github.com/{}?tab=followers&page={}'
        self.following_url_tpl = 'https://github.com/{}?tab=following&page={}'

        self.username = None
        self.page = None
        self.url = None


class GithubProfileFetcher(BaseGithubFetcher):
    def __init__(self, http_session):
        super().__init__(http_session)

    async def before(self, redis_client, redis_key):
        username = await redis_client.execute('lpop', redis_key)
        if not username:
            if await redis_client.execute('llen', redis_key) == 0:
                return False
        else:
            username = username.decode('utf-8')
            self.url = self.profile_url_tpl.format(username)
        return True

    async def fetch(self):
        async with self.http_session.get(self.url, headers=self.headers) as response:
            html = await response.text()
            extractor = GithubProfileExtractor(html)
            profile_data = extractor.parse()

            return {'items': profile_data, 'next_page': None}


class GithubStarsFetcher(BaseGithubFetcher):
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

            self.username = json_data['username']
            self.page = json_data['page']
            self.url = self.stars_url_tpl.format(self.username, self.page)
        return True

    async def fetch(self):
        async with self.http_session.get(self.url, headers=self.headers) as response:
            html = await response.text()
            extractor = GithubStarsExtractor(html)
            stars_list = extractor.parse(page=self.page)

            next_page_url = extractor.next_page()
            if next_page_url:
                next_page = dict()
                next_page['username'] = self.username
                next_page['page'] = self.page + 1
            else:
                next_page = None

            return {'items': stars_list, 'next_page': next_page}


class GithubReposFetcher(BaseGithubFetcher):
    def __init__(self, http_session):
        super().__init__(http_session)

    async def fetch(self, username):
        async with self.http_session.get(self.repos_url_tpl.format(username), headers=self.headers) as response:
            print(await response.text())

            with codecs.open('github_repos_{}.html'.format(username), 'w', 'utf-8') as fp:
                fp.write(await response.text())


class GithubFollowersFetcher(BaseGithubFetcher):
    def __init__(self, http_session):
        super().__init__(http_session)

    async def fetch(self, username):
        async with self.http_session.get(self.followers_url_tpl.format(username), headers=self.headers) as response:
            print(await response.text())

            with codecs.open('github_followers_{}.html'.format(username), 'w', 'utf-8') as fp:
                fp.write(await response.text())


class GithubFollowingFetcher(BaseGithubFetcher):
    def __init__(self, http_session):
        super().__init__(http_session)

    async def fetch(self, username):
        async with self.http_session.get(self.following_url_tpl.format(username), headers=self.headers) as response:
            print(await response.text())

            with codecs.open('github_following_{}.html'.format(username), 'w', 'utf-8') as fp:
                fp.write(await response.text())
