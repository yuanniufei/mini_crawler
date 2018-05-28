# 注：之所以有些数字类型不直接做 int 转换，是因为 Github
# 在显示数字的时候，如果过多，一般会显示成 k（千）的形式。
from bs4 import BeautifulSoup
from bs4.element import NavigableString


class BaseGithubExtractor:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')


class GithubProfileExtractor(BaseGithubExtractor):
    def __init__(self, html):
        super().__init__(html)

    def parse(self):
        user_profile_data = dict()

        # User Profile Bio
        user_profile_bio_elem = self.soup.find('div', {'class': 'user-profile-bio'})
        user_profile_bio_data = user_profile_bio_elem.text

        # User Profile Nav
        user_profile_nav_elem = self.soup.find('div', {'class': 'user-profile-nav'}).nav
        for tab in user_profile_nav_elem:
            if isinstance(tab, NavigableString):
                continue
            if tab['title'] == 'Overview':
                continue
            title = tab['title']
            count = tab.find('span', {'class': 'Counter'}).text.replace('\n', '').replace(' ', '')
            user_profile_data[title] = count

        user_profile_data['bio'] = user_profile_bio_data

        # Vcard Details
        vcard_details_elem = self.soup.find('ul', {'class': 'vcard-details'})
        vcard_details_data = dict()
        # TODO 电子邮件需要登录才能查看。
        for vcard_detail_elem in vcard_details_elem:
            if isinstance(vcard_detail_elem, NavigableString):
                continue
            vcard_details_data[vcard_detail_elem['aria-label']] = vcard_detail_elem.text.replace('\n', '')

        # Organizations
        organizations_elem = self.soup.find('div', {'class': 'border-top py-3 clearfix'})
        organizations_data = list()
        if organizations_elem:
            for organization_elem in organizations_elem:
                if organization_elem.name != 'a':
                    continue
                organizations_data.append(organization_elem['aria-label'])

        # Pinned Repositories
        pinned_repos_elem = self.soup.find('div', {'class': 'js-pinned-repos-reorder-container'})
        pinned_repos_data = list()
        for pinned_repo_elem in pinned_repos_elem.ol:
            if isinstance(pinned_repo_elem, NavigableString):
                continue
            pinned_repos_data.append(pinned_repo_elem.find('span').find('a')['href'])

        # Contributions
        contributions_elem = self.soup.find('div', {'class': 'js-contribution-graph'})
        contributions_count = contributions_elem.find('h2').text.replace('\n', '').strip().split()[0]

        data_date_elems = contributions_elem.find_all('rect')
        data_date_data = list()
        for data_date_elem in data_date_elems:
            if int(data_date_elem['data-count']) == 0:
                continue
            data_date_data.append((data_date_elem['data-date'], data_date_elem['data-count']))

        contributions_data = dict()
        contributions_data['count'] = contributions_count
        contributions_data['data_date'] = data_date_data

        data = dict()
        data['user_profile'] = user_profile_data
        data['vcard_details'] = vcard_details_data
        data['organizations'] = organizations_data
        data['pinned_repos'] = pinned_repos_data
        data['contributions'] = contributions_data
        return data


class GithubStarsExtractor(BaseGithubExtractor):
    def __init__(self, html):
        super().__init__(html)

    # 记录下 Star 项目的顺序
    def parse(self, page=1):
        stars_list_elem = self.soup.find_all("div", {"class": "col-12 d-block width-full py-4 border-bottom"})
        stars_list = list()
        for i, star_elem in enumerate(stars_list_elem):
            elem = star_elem.find("div", {"class": "d-inline-block mb-1"}).h3.a
            project_name = elem.text.replace('\n', '').replace(' ', '')
            stars_list.append((page, i + 1, project_name))
        return stars_list

    def next_page(self):
        pagination_elem = self.soup.find("div", {"class": "pagination"})
        if pagination_elem:
            last_page_elem = pagination_elem.find("span", {'class': "next_page disabled"})
            if not last_page_elem:
                next_page_elem = pagination_elem.find("a", {"class": "next_page"})
                if next_page_elem:
                    next_page_url = 'https://www.github.com{}'.format(next_page_elem['href'])
                else:
                    next_page_url = None
            else:
                next_page_url = None
        else:
            next_page_url = None
        return next_page_url


class GithubReposExtractor(BaseGithubExtractor):
    def __init__(self, html):
        super().__init__(html)

    def parse(self):
        pass


class GithubFollowersExtractor(BaseGithubExtractor):
    def __init__(self, html):
        super().__init__(html)

    def parse(self):
        pass


class GithubFollowingExtractor(BaseGithubExtractor):
    def __init__(self, html):
        super().__init__(html)

    def parse(self):
        pass
