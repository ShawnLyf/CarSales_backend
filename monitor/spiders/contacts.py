import scrapy


class ContactsSpider(scrapy.Spider):
    name = 'contacts'
    allowed_domains = ['www.sydneytoday.com']
    start_urls = ['http://www.sydneytoday.com/']


    def start_requests(self):
        mobile_headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36"}
        yield scrapy.Request(
            'https://www.sydneytoday.com/car_sale/1422467967442001',
            headers=mobile_headers
        )

    def parse(self, response):
        phone = response.xpath("//label[@id='uMobile']/text()").get()
        script = response.xpath("//script[contains(text(),'uMobile')]/text()").get()

        yield{
            'phone':phone,
            'scritp':script
        }
