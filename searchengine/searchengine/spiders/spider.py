import scrapy
from urllib.parse import urlparse, urlunparse, urljoin
from ..items import SearchEngineItem

class GenericSpider(scrapy.Spider):
    name = 'generic'
    
    # Initialize spider values
    def __init__(self, start_url=None, spider_name=None, *args, **kwargs):
        super(GenericSpider, self).__init__(*args, **kwargs)
        if not start_url:
            raise ValueError("Must pass a start_url to the spider.")
        self.start_urls = [start_url]
        if spider_name:
            self.name = spider_name
        # Track which urls have been visited to avoid revisiting the same page
        self.visited_urls = set()
    
    def normalize_url(self, url):
        """
        Normalize and canonicalize a URL:
        - Prefer HTTPS
        - Strip www
        - Lowercase scheme and netloc
        - Keep query (important for product pages)
        - Remove fragments
        - Remove trailing slash
        """
        parsed = urlparse(url)

        # Prefer https
        scheme = 'https' if parsed.scheme == 'http' else parsed.scheme.lower()
        netloc = parsed.netloc.lower().replace("www.", "")
        path = parsed.path.rstrip('/')

        return urlunparse((scheme, netloc, path, parsed.params, parsed.query, ''))
    
    def parse(self, response):
        # Normalize URL
        normalized_url = self.normalize_url(response.url)

        # Look for <link rel="canonical"> tag and prefer that URL if it exists
        canonical_link = response.css('link[rel="canonical"]::attr(href)').get()
        if canonical_link:
            canonical_url = response.urljoin(canonical_link)
            normalized_url = self.normalize_url(canonical_url)
        
        # Check if url is unvisited
        if normalized_url in self.visited_urls:
            return
        self.visited_urls.add(normalized_url)
        
        items = SearchEngineItem()
        
        # Get page url
        items['url'] = normalized_url
        
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

        base_url = urlparse(response.url).netloc.lower().replace("www.", "")
        for link in response.css('a::attr(href)').getall():
            absolute_url = response.urljoin(link)
            normalized_link = self.normalize_url(absolute_url)
            if base_url in normalized_link and normalized_link not in self.visited_urls:
                yield scrapy.Request(absolute_url, callback=self.parse)

        pagination_xpath = '//a[contains(translate(text(), "NEXT›→»", "next›→»"), "next") or contains(text(), "›") or contains(text(), "→") or contains(text(), "»")]/@href'
        next_page = response.xpath(pagination_xpath).get()
        if next_page:
            next_url = response.urljoin(next_page)
            normalized_next = self.normalize_url(next_url)
            if normalized_next not in self.visited_urls:
                yield scrapy.Request(
                    url=response.urljoin(next_page),
                    callback=self.parse,
                    meta={'depth': response.meta.get('depth', 0)}  # preserve current depth
                )

        yield items