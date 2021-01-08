import scrapy.contrib.downloadermiddleware.DownloaderMiddleware

class validateMiddle(scrapy.contrib.downloadermiddleware.DownloaderMiddleware):
    def process_response(request, response, spider):
        i = 0