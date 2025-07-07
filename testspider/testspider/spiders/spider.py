import scrapy
from ..items import TestspiderItem

class Spider(scrapy.Spider):
    name = 'spiderbot'
    start_urls = [
        'https://quotes.toscrape.com/'
    ]
    
    # Track which urls have been visited to avoid revisiting the same page
    visited_urls = set()
    
    def parse(self, response):
        
        # Check if url is unvisited
        if response.url in self.visited_urls:
            return
        self.visited_urls.add(response.url)
        
        items = TestspiderItem()
        
        # Get page url
        items['url'] = response.url
        
        # Get page title
        title = response.css('title::text').get()
        items["title"] = title
        
        # Get all text from the page body
        all_text = response.css("body *::text").getall()
        # Remove extra whitespace and join
        cleaned_text = ' '.join([text.strip() for text in all_text if text.strip()])
        items["text"] = cleaned_text

        # Get all image links from page
        images = response.css("img::attr(src)").getall()
        full_images = [response.urljoin(img) for img in images if img]
        items["images"] = full_images

        base_url = response.url.split('/')[2]
        for link in response.css('a::attr(href)').getall():
            absolute_url = response.urljoin(link)
            if base_url in absolute_url:
                yield scrapy.Request(absolute_url, callback=self.parse)

        pagination_xpath = '//a[contains(translate(text(), "NEXT›→»", "next›→»"), "next") or contains(text(), "›") or contains(text(), "→") or contains(text(), "»")]/@href'
        next_page = response.xpath(pagination_xpath).get()
        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse,
                meta={'depth': response.meta.get('depth', 0)}  # preserve current depth
            )

        yield items