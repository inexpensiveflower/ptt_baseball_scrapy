# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import ptt_baseball_scrapy.items as items
from scrapy.exceptions import DropItem


class PttBaseballScrapyPipeline:
    def process_item(self, item, spider):
        return item


import pymongo

class AbstractMongoPipeline(object):
	collection_name = 'None'

	def __init__(self, mongo_uri, mongo_db):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db
		self.client = pymongo.MongoClient(self.mongo_uri)
		self.db = self.client[self.mongo_db]
		self.collection = self.db[self.collection_name]

	@classmethod
	def from_crawler(cls, crawler):
		return cls(
			mongo_uri = crawler.settings.get('MONGO_URI'),
			mongo_db = crawler.settings.get('MONGO_DATABASE')
		)

	def close_spider(self, spider):
		self.client.close()

class PttBaseballPostPipeline(AbstractMongoPipeline):
	
	collection_name = 'article_scrapy'

	def process_item(self, item, spider):
		if type(item) is items.PttBaseballScrapyPostItem:
			document = self.collection.find_one({'post_url': item['post_url']})

			if not document:
				insert_result = self.collection.insert_one(dict(item))
				item['_id'] = insert_result.inserted_id
				print(item['title'], "   新增成功!")
			else:
				self.collection.update_one(
					{'_id': document['_id']},
					{'$set': dict(item)},
					upsert=True
				)

				item['_id'] = document['_id']
				print(item['title'], "   更新成功!")
			
		return item

class PttBaseballReplyPipeline(AbstractMongoPipeline):

	collection_name = 'response_scrapy'

	def process_item(self, item, spider):
		if type(item) is items.PttBaseballScrapyReplyItem:
			document = self.collection.find_one({'reply_content':item['reply_content']})

			if not document:
				self.collection.insert_one(dict(item))
				print("回覆內容新增成功")
				
			else:
				
				self.collection.update_one(
					{'_id':document['_id']},
					{'$set':dict(item)},
					upsert = True
				)
				print("回覆內容新增成功")
		return item

class DeleteNullTitlePipeline(object):
	def process_item(self, item, spider):
		if type(item) is items.PttBaseballScrapyPostItem:
			title = item['title']

			if title:
				return item
			else:
				raise DropItem('Found null title %s', item)