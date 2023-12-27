
from pathlib import Path

import arrow
import functools
import json
import logging
import scrapy


# Set logger.
log_file_handler = logging.FileHandler('TaiwanRegulationCrawlerLogger.log')
logger = logging.getLogger('TaiwanRegulationCrawlerLogger.log')
logger.addHandler(log_file_handler)
logger.setLevel(logging.ERROR)

REGULATION_PATH = Path('./regulations')
if not REGULATION_PATH.exists():
    REGULATION_PATH.mkdir()


class RegulationSpider(scrapy.Spider):
    # The main task of this spider is to crawl all the data in 全國法規資料庫, and then stores them into .json files.

    name = 'regulation'

    allowed_domains = ['law.moj.gov.tw']

    DEPRECATED_KEYWORDS = ('廢止法規', '停止適用')
    LAW_LIST_URL = 'https://law.moj.gov.tw/Law/'
    # LAW_CONTENT_URL = 'https://law.moj.gov.tw/Law/'

    def start_requests(self):
        urls = [
            # 全國法規資料庫
            'https://law.moj.gov.tw/Law/LawSearchLaw.aspx',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_all_links)

    def parse_all_links(self, response):
        # Get all links in a tree-like ul-li structure, which has `tree` as its id.

        def __is_deprecated_regulation(regulation_name):
            for keyword in self.DEPRECATED_KEYWORDS:
                if keyword in regulation_name:
                    return True
            return False

        def get_tree(ul):
            name_link_dict = {}
            for li in ul.xpath('li'):
                a_tag = li.xpath('.//a')
                name = a_tag.xpath('./text()').get().strip()
                sub_ul = li.xpath('ul')
                if not __is_deprecated_regulation(name):
                    if sub_ul: # if have sub-ul, recursively solve it.
                        sub_tree = get_tree(sub_ul)
                        name_link_dict[name] = sub_tree
                    else:
                        name_link_dict[name] = a_tag.xpath('./@href').get()
            return name_link_dict

        # TODO: Abstractize the following functions, make iterating the tree-like dict easier.
        # This function is a kind of pseudo code of doing so.
        # def _iterate_tree_dict(root_dict, func, kwargs):
        #     for key, value in root_dict.items():
        #         do_something_here(): for those who don't have sub-tree.
        #         if type(value) == dict: # Means this one have sub-tree.
        #             _iterate_tree_dict(value) # recursively got the sub-tree.
        #     return

        def make_directories_for_regulations(regulation_tree_dict, parrent_path=REGULATION_PATH):
            # Make directories in the tree-like structure.
            for regulation_name, link in regulation_tree_dict.items():
                # Make new directory first.
                new_dir = parrent_path / regulation_name.strip()
                if not new_dir.exists():
                    new_dir.mkdir()

                # If it have sub-tree, we need to create sub-direcotry.
                if type(link) == dict:
                    make_directories_for_regulations(link, parrent_path=new_dir) # link here is a sub-tree, it's a dict.
            return

        def get_data_to_request_by_link_tree(regulation_tree_dict, parrent_path=REGULATION_PATH):
            result = []
            for regulation_name, link in regulation_tree_dict.items():
                current_dir = parrent_path / regulation_name
                # If it have sub-tree, we need to create sub-direcotry.
                if type(link) == dict:
                    # link here is a sub-tree, it's a dict.
                    result.extend(get_data_to_request_by_link_tree(link, parrent_path=current_dir))
                else: # don't have sub-tree, so we can call the request for link.
                    url = f'{self.LAW_LIST_URL}{link}'
                    result.append({'url': url, 'storage_dir': current_dir})
            return result


        ul_root = response.xpath('//ul[@id="tree"]')
        regulation_name_link_dict = get_tree(ul_root)

        # Make directories for the following data storage.
        make_directories_for_regulations(regulation_name_link_dict)

        # Call requests.
        for data in get_data_to_request_by_link_tree(regulation_name_link_dict):
            parse_link = functools.partial(
                self.parse_link,
                storage_dir=data['storage_dir'],
            )
            yield scrapy.Request(url=data['url'], callback=parse_link)


    def parse_link(self, response, storage_dir=REGULATION_PATH):
        regulation_links = response.xpath('//td//a')
        for a_tag in regulation_links:
            regulation_name = a_tag.xpath('./text()').get()
            if not regulation_name:
                continue
            link = a_tag.xpath('./@href').get()
            parse_regulation = functools.partial(
                self.parse_regulation,
                storage_dir=storage_dir,
                regulation_name=regulation_name,
            )
            url = f'{self.LAW_LIST_URL}{link}'
            yield scrapy.Request(url=url, callback=parse_regulation)


    def parse_regulation(self, response, storage_dir, regulation_name):
        file_download_links = response.xpath('//a[contains(@href, "LawGetFile.ashx")]')
        if file_download_links:
            # FIXME: Download file here.
            pass

        regulation_article_number_content_dict = {}
        regulation_rows = response.xpath('//div[@id="pnLawFla"]/div/div')
        if regulation_rows: # Since some regulation pages have only PDF file, have no regulation content.
            for row in regulation_rows:
                article_number = [i.strip() for i in row.xpath('.//div[@class="col-no"]//text()').getall() if i.strip()]
                if not article_number:
                    continue
                if len(article_number) > 1:
                    article_number = article_number[1]
                else:
                    article_number = article_number[0]
                contents = [i.strip() for i in row.xpath('.//div[@class="col-data"]//text()').getall() if i.strip()]
                contents = '\n'.join(contents)
                regulation_article_number_content_dict[article_number] = contents

        with open(storage_dir / f'{regulation_name}.json', 'w', encoding='UTF-8') as file:
            json.dump(regulation_article_number_content_dict, file, ensure_ascii=False, indent=4)


    def download_files(self, response, args):
        pass


