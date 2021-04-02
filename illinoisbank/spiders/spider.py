import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import IillinoisbankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class IillinoisbankSpider(scrapy.Spider):
	name = 'illinoisbank'
	start_urls = ['https://www.illinoisbank.com/customer-service/about/news']

	def parse(self, response):
		post_links = response.xpath('//a[contains(@aria-described-by,"article-header-")]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@title="Go to next page"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="content"]/p/strong/text()').get()
		try:
			date = re.findall(r'\w+\s\d+\,\s\d+', date)
		except TypeError:
			date = "Not stated in article"
		if not date:
			date = "Not stated in article"
		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//div[@class="content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=IillinoisbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
