import scrapy
import re
import time
import logging
import ptt_baseball_scrapy.items as items
from datetime import datetime


class PttBaseballSpider(scrapy.Spider):
    name = 'ptt_baseball'
    allowed_domains = ['ptt.cc']
    start_urls = ['http://www.ptt.cc/bbs/Baseball/index.html', ]

    _page = 0
    MAX_PAGES = 10

    def parse(self, response):

        self._page += 1

        for href in response.css('div.r-ent > div.title > a::attr(href)'):
            url = href.get()
            yield scrapy.Request(response.urljoin(url), callback = self.parse_post)

        if self._page < PttBaseballSpider.MAX_PAGES:
            next_page = response.css('#action-bar-container > div > div.btn-group.btn-group-paging  > a::attr(href)').getall()
    		
            if next_page:
                url = response.urljoin(next_page[1])
                time.sleep(1)
                yield scrapy.Request(url, self.parse)
            else:
                logging.warning("no next page")
        else:
            logging.warning("max page reached")

    def parse_post(self, response):
        post_info = items.ArticleReplyItem()

        try:
            post_author = response.xpath('//*[@id="main-content"]/div[1]/span[2]/text()')[0].get().split(' ')[0]
        except:
            return(0)
        try:
            post_title = response.xpath('//*[@id="main-content"]/div[3]/span[2]/text()')[0].get()
        except:
            return(0)
        try:
            post_time = datetime.strptime(response.xpath('//*[@id="main-content"]/div[4]/span[2]/text()')[0].get(), '%a %b %d %H:%M:%S %Y')
        except:
            return(0)

        content = response.css('div#main-content').css('::text').getall()
        content = ", ".join(content)
        content = content.split('--')[0]
        content = content.split('\n')
        content = "\n".join(content[1:])

        push_tag_list = response.css('div.push > span.push-tag').css('::text').getall()
        score = 0
        push_count = 0
        abstract_count = 0

        for push in push_tag_list:
            if "推" in push:
                push_count += 1
            elif "噓" in push:
                abstract_count += 1
            else:
                pass

        score = score + push_count - abstract_count

        comments = []
        reply_list = response.css('div.push')

        for reply in reply_list:
            reply_id = reply.css('span.push-userid::text').get()
            reply_tag = reply.css('span.push-tag::text').get()
            reply_content = reply.css('span.push-content::text').get()

            comments.append({'reply_id':reply_id,
                'reply_tag':reply_tag,
                'reply_content':reply_content})

        post_info['author'] = post_author
        post_info['title'] = post_title
        post_info['post_time'] = post_time
        post_info['post_score'] = score
        post_info['post_url'] = response.url
        post_info['update_time'] = datetime.now()
        post_info['content'] = content
        post_info['comments'] = comments

        yield post_info