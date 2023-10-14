import scrapy
from monitor.items import *
from scrapy.loader import ItemLoader
import psycopg2,psycopg2.extras

class ListenSpider(scrapy.Spider):
    name = 'listen'
    start_urls = ['https://www.sydneytoday.com/car_sale/']
    
    # for filter the visited list and make sure the the loading 
    def preload(self,response):
        cnn = psycopg2.connect(
            host='uowlibrary.cfgr3kbul23x.ap-southeast-2.rds.amazonaws.com',
            database = 'todaysydney',
            user = 'shawn',
            password = 'mlpmlpmlp'
        )
        cur = cnn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        post_elements = response.xpath("//div[@class='yp-list-item'][not(descendant::span[@class='mtg-pill mtg-pill_red'])]")
        city = getCity(response.xpath("//div[@class='header-left__cityname pull-right']/text()").get())

        post_folinks = []
        for post_element in reversed(post_elements):
            id = getId(post_element.xpath(".//div[@class='col-xs-3']/a/@href").get())
            crnt_price = getPrice(post_element.xpath(".//span[@class='yp-list-price__bold']/text()").get())

            cur.execute(f"select id,price,prevprice from post where is_active = True and id = {id}")
            identified_post = cur.fetchone()
            print("--------identified_post--------")
            print(identified_post)
            print("----------------")
            if identified_post:
                # if exist, check if the price changed or not 
                recored_price =  identified_post['price']
                # if changed, update the new price, and record the old price
                if crnt_price != recored_price:
                    cur.execute(f'update post set prevprice = {recored_price} where id = {id}')
                    cur.execute(f'update post set price = {crnt_price} where id = {id}')
                    cnn.commit()
            else:
                # if not exist(new post) preload the to database and put it into new_postids list
                updatetime = post_element.xpath(".//div[@class='yp-list-mix']/span[1]/text()").get()
                createtime_list = get_createtimelist(updatetime)
                interval = f'{createtime_list[0]} {createtime_list[1]}:{createtime_list[2]}:{createtime_list[3]}'
                cur.execute('''insert into post(id,createtime,postcity,price) 
                                         values(%s,now()-interval %s,%s,%s)''',(id,interval,city,crnt_price))
                cnn.commit()             
                post_folinks.append(str(id))

        cur.close()
        cnn.close()
        return post_folinks
    # decrepated, use pipeline close function instead
     # to remove none-image records, otherwise will cause display error in Django HTML Templates
    # def remove_none_image_records(self): 
    #     cnn = psycopg2.connect(
    #         host='uowlibrary.cfgr3kbul23x.ap-southeast-2.rds.amazonaws.com',
    #         database = 'todaysydney',
    #         user = 'shawn',
    #         password = 'mlpmlpmlp'
    #     )
    #     cur = cnn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #     cur.execute("delete from post where images IS NULL")
    #     cnn.commit()  
    #     cnn.close() 

    def parse(self, response):
        # post_folinks= ['1423468985804001','1423468750177002','1423468838896007','1423468838896007','1423469163789001','1422456056094016','1422462238632012','1422464537832008']
        # post_folinks = ['1422466972354010']
        post_folinks = self.preload(response)

        mobile_headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36"}

        for post_folink in post_folinks:     
            yield response.follow(url=post_folink,callback=self.parse_mobile_detail,headers=mobile_headers,dont_filter=True)
        # self.remove_none_image_records()

    def parse_mobile_detail(self,response):   
        item = PostItem()
        item['updatetime']= get_updatetime(response.xpath("//div[@class='mtg-yptitle-time']/text()").get())
        item['price'] = getPrice(response.xpath("//span[@class='mtg-ypprice__text']/text()").get())
       
        item['username'] = response.xpath("//p[@style=' margin-top: -6px;']/text()").get()
        item["is_private"]= getSellertype(response.xpath("//span[@class='mtg-pill mtg-pill_blue mtg-pill_filled']/text()").get())
        item["userage"]= get_userage(response.xpath("//p[@style='color: #888;font-size: 12px;']/text()").get())
        item['userimage'] = response.xpath("//img[@style='border-radius:30px']/@src").get()
        #item['phone'] = response.xpath("//label[@id='uMobile']/text()").get()
        item['wechat'] = response.xpath("//img[contains(@src,'wechat')]/following-sibling::span[1]/text()").get()
        #item['email'] = response.xpath("//label[@id='uMail']/text()").get()
        item['qq'] = response.xpath("//img[contains(@src,'qq')]/following-sibling::span[1]/text()").get()
        item['contactsScript']= response.xpath("//script[contains(text(),'uMobile')]/text()").get()

        desktop_headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
        yield scrapy.Request(url=response.url,callback = self.parse_desktop_detail,headers = desktop_headers,dont_filter=True,meta={'item': item})

    def parse_desktop_detail(self,response):
        xpath = response.xpath("//body")
        loader = ItemLoader(item=response.meta['item'],selector=xpath)

        id = getId(response.url)
        loader.add_value("postid", id)
        loader.add_xpath("title",".//div[@class='padding20']/h1/text()")
        loader.add_xpath("mileage",".//div[contains(text(),'公里数') and @style='color:#888']/parent::node()/text()[2]")
        loader.add_xpath("transmission",".//div[contains(text(),'变速箱') and @style='color:#888']/parent::node()/text()[2]")
        loader.add_xpath("regodue",".//div[contains(text(),'Rego到期') and @style='color:#888']/parent::node()/text()[2]")
        loader.add_xpath("suburb",".//ol[@class='breadcrumb']/li[3]/a/text()")
        loader.add_xpath("fueltype",".//div[contains(text(),'汽油类型') and @style='color:#888']/parent::node()/text()[2]")
        loader.add_xpath("views",".//span[@class='icon-eye']/parent::node()/text()")
        loader.add_xpath("year",".//div[@class='padding20']/h1/text()")
        loader.add_xpath("brand",".//div[contains(text(),'汽车品牌') and @style='color:#888']/parent::node()/text()")
        loader.add_xpath("boughtyear",".//div[contains(text(),'购买年份') and @style='color:#888']/parent::node()/text()[2]")
        loader.add_xpath("lastservice",".//div[contains(text(),'上一次保养') and @style='color:#888']/parent::node()/text()[2]")
        loader.add_xpath("cartype",".//div[contains(text(),'车辆类型') and @style='color:#888']/parent::node()/text()[2]")
        loader.add_xpath("content",".//div[@class='yp-descriprion']/text()") 
        loader.add_xpath("images",".//a[@class='venobox']/@href")
        loader.add_xpath("tags",".//div[contains(text(),'标签') and @style='color:#888']/parent::node()/text()[2]") 

        yield loader.load_item()
        