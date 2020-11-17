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
    MAX_PAGES = 2


    	

    def parse(self, response):

    	self._page += 1

    	for href in response.css('div.r-ent > div.title > a::attr(href)'):
    		url = href.get()
    		# print("!!!!", response.urljoin(url))
    		yield scrapy.Request(response.urljoin(url), callback = self.parse_post)

    	if self._page < PttBaseballSpider.MAX_PAGES:
    		next_page = response.css('#action-bar-container > div > div.btn-group.btn-group-paging  > a::attr(href)').getall()
    		# print("~~~~~~~", next_page[1])

    		if next_page:
    			url = response.urljoin(next_page[1])
    			# print("~~~~", url)
    			time.sleep(1)
    			yield scrapy.Request(url, self.parse)
    		else:
    			logging.warning("no next page")
    	else:
    		logging.warning("max page reached")

    def parse_post(self, response):

    	post_info = items.PttBaseballScrapyPostItem()
    	
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

    	print("作者 ", post_author)
    	print("標題 ", post_title)
    	print("時間 ", post_time)
    	reply_list = response.css('div.push > span.push-tag')
    	reply_push = reply_list.css('::text').getall()
    	print("留言數 ", len(reply_list))

    	score = 0
    	push_count = 0
    	abstract_count = 0
    	
    	for push in reply_push:
    		if "推" in push:
    			push_count += 1
    		elif "噓" in push:
    			abstract_count += 1
    		else:
    			pass
    	score = score + push_count - abstract_count
    	print("文章分數 ", score)

    	post_info['author'] = post_author
    	post_info['title'] = post_title
    	post_info['post_time'] = post_time
    	post_info['good_push'] = push_count
    	post_info['bad_push'] = abstract_count
    	post_info['post_score'] = score
    	post_info['post_url'] = response.url
    	post_info['update_time'] = datetime.now()

    	yield post_info

    	if '_id' in post_info:
    		article_id = post_info['_id']
    		# print(type(article_id))

    	yield from self.parse_reply(response, article_id)
    		
    def parse_reply(self, response, article_id):

    	reply = items.PttBaseballScrapyReplyItem()

    	reply['article_id'] = article_id

    	push_list = response.css('div.push')

    	for each_reply in push_list:	
    		 
    		reply['push'] = each_reply.css('span.push-tag').css('::text').get()
    		reply['reply_id'] = each_reply.css('span.push-userid').css('::text').get()
    		reply['reply_content'] = each_reply.css('span.push-content').css('::text').get()
    		reply['reply_time'] = datetime.strptime(each_reply.css('span.push-ipdatetime').css('::text').get().strip(), '%m/%d %H:%M')

    		yield reply
    	