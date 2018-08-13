"""
草榴社区 > 成人文学交流区
"""
import scrapy


class FacetiaeSpider(scrapy.Spider):
    name = "facetiae_spider"
    host = "http://t66y.com"

    def start_requests(self):
        urls = [
            'http://www.t66y.com/thread0806.php?fid=20'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        urls = response.xpath(u'//*[contains(@class, "tr3 t_one")]//h3//@href').extract()
        for url in urls[:]:
            if 'htm_data' not in url:
                urls.remove(url)
                continue
            yield scrapy.Request(url, callback=self.parse_post, errback=self.handle_failure, dont_filter=True)

        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
