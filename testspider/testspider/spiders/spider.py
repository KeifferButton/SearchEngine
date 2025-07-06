import scrapy
from ..items import TestspiderItem

class Spider(scrapy.Spider):
    name = 'spiderbot'
    start_urls = [
        'https://quotes.toscrape.com/'
    ]
    
    def parse(self, response):
        
        items = TestspiderItem()
        
        # Get page title
        title = response.css('title::text').get()
        items["title"] = title
        
        # Get all text from the page body
        all_text = response.css("body *::text").getall()
        # Remove extra whitespace and join
        cleaned_text = ' '.join([text.strip() for text in all_text if text.strip()])
        items["text"] = cleaned_text
        
        # Get all outgoing links from page
        links = response.css("a::attr(href)").getall()
        full_links = [response.urljoin(link) for link in links if link]
        items["links"] = full_links

        # Get all image links from page
        images = response.css("img::attr(src)").getall()
        full_images = [response.urljoin(img) for img in images if img]
        items["images"] = full_images

        yield items