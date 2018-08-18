from scrapy import cmdline

# cmdline.execute("scrapy crawl pornhub_spider".split())
# cmdline.execute("scrapy crawl zzcartoon_spider".split())
# cmdline.execute("scrapy crawl nhentai_spider".split())
# cmdline.execute("scrapy crawl 69_story_spider".split())
# cmdline.execute("scrapy crawl book3k_spider".split())
# cmdline.execute("scrapy crawl abc111_spider".split())
cmdline.execute("scrapy crawl hentaifox_spider -s JOBDIR=crawls/hentaifox".split())
