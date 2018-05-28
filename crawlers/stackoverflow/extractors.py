from bs4 import BeautifulSoup


class BaseStackOverflowExtractor:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')


class StackOverflowTagsExtractor(BaseStackOverflowExtractor):
    def __init__(self, html):
        super().__init__(html)

    def parse(self):
        tags_data = list()

        tag_cell_elems = self.soup.find_all('div', {'class': 'tag-cell'})
        for tag_cell_elem in tag_cell_elems:
            tag_name = tag_cell_elem.a.text
            # tag_url = tag_cell_elem.a['href']
            tags_data.append(tag_name)

        return tags_data


class StackOverflowTaggedExtractor(BaseStackOverflowExtractor):
    def __init__(self, html):
        super().__init__(html)

    def parse(self):
        questions_data = list()

        question_summary_elems = self.soup.find_all('div', {'class': 'question-summary'})
        for question_summary_elem in question_summary_elems:
            summary_elem = question_summary_elem.find('div', {'class': 'summary'})
            question_hyperlink_elem = summary_elem.find('a', {'class': 'question-hyperlink'})

            question_name = question_hyperlink_elem.text
            question_href = question_hyperlink_elem['href']
            question_id = question_href.split('/')[2]

            questions_data.append((question_id, question_name, question_href))

        return questions_data
