TODO: Fix this error.
2023-12-27 12:18:26 [scrapy.core.scraper] ERROR: Spider error processing <GET https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=S0050004> (referer: https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07004003)
Traceback (most recent call last):
  File "C:\Users\LeiHa\miniconda3\envs\ck_crawler\Lib\site-packages\twisted\internet\defer.py", line 892, in _runCallbacks
    current.result = callback(  # type: ignore[misc]
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\LeiHa\Documents\GitHub\TaiwanRegulationCrawler\RegulationCrawler\spiders\regulation_spider.py", line 152, in parse_regulation
    with open(storage_dir / f'{regulation_name}.json', 'w', encoding='UTF-8') as file:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'regulations\\考試\\公務人員保障暨培訓委員會\\培訓目    \\公務人員訓練進修法.json'