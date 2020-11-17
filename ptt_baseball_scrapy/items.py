# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PttBaseballScrapyPostItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    author = scrapy.Field()
    title = scrapy.Field()
    post_time = scrapy.Field()
    good_push = scrapy.Field()
    bad_push = scrapy.Field()
    post_score = scrapy.Field()
    update_time = scrapy.Field()
    post_url = scrapy.Field()

class PttBaseballScrapyReplyItem(scrapy.Item):
	_id = scrapy.Field()
	article_id = scrapy.Field()
	push = scrapy.Field()
	reply_content = scrapy.Field()
	reply_id = scrapy.Field()
	reply_time = scrapy.Field()
