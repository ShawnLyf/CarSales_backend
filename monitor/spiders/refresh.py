import scrapy
from monitor.items import *
import json
import psycopg2,psycopg2.extras
# remvoed posts['1423468667862001']
class RefreshSpider(scrapy.Spider):
    name = 'refresh'
    start_urls = []
    handle_httpstatus_list = [404] 
    def opendb(self):
        self.cnn = psycopg2.connect(host='localhost',database = 'monitor',user = 'shawn',password = 'shawn')
        self.cur = self.cnn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    def closedb(self):
        self.cur.close()
        self.cnn.close()

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

        # check  is the refresh id in the active list, if not filter it out
        def is_activepost(id):
            self.opendb()
            self.cur.execute('select id from post where id = %s and is_active = True',(id,))
            is_active = self.cur.fetchone() != None
            self.closedb()
            return is_active
            
        self.start_urls = []
        with open('monitor/refreshids.json') as re:
            ids = json.load(re)['ids']
            for id in ids:
                if is_activepost(id):
                    print(id)
                    self.start_urls.append("https://www.sydneytoday.com/car_sale/"+str(id))
        
        
    def parse(self, response):# parse desktop 
        def updatePostStatus(id):
            self.opendb()
            self.cur.execute('select tagid from post_tag where postid = %s',(id,))
            tag_list = self.cur.fetchall()
            self.cur.execute('delete from post_tag where postid = %s',(id,))
            self.cnn.commit()
            self.cur.execute('update post set is_active = False where id = %s',(id,))
            self.cnn.commit()
            for tag_id in tag_list:
                self.cur.execute('insert into post_tag values(%s,False,%s)',(id,tag_id['tagid']))
                self.cnn.commit()
            self.closedb()
        
        id = getId(response.url)
        if response.status == 404:
            updatePostStatus(id)
        else:
            item = PostItem()
            item['postid'] = id
            item['title'] = response.xpath("//div[@class='padding20']/h1/text()").get()
            item["mileage"]= mileage(response.xpath("//div[contains(text(),'公里数') and @style='color:#888']/parent::node()/text()[2]").get())
            item["transmission"]= transmission(response.xpath("//div[contains(text(),'变速箱') and @style='color:#888']/parent::node()/text()[2]").get())
            item["regodue"]=regodue(response.xpath("//div[contains(text(),'Rego到期') and @style='color:#888']/parent::node()/text()[2]").get())
            item["suburb"]=response.xpath("//ol[@class='breadcrumb']/li[3]/a/text()").get()
            item["fueltype"]= fueltype(response.xpath("//div[contains(text(),'汽油类型') and @style='color:#888']/parent::node()/text()[2]").get())
            item["views"] = views(response.xpath("//span[@class='icon-eye']/parent::node()/text()").get())
            item["year"] = year(item['title'])
            item["brand"] = brand(response.xpath("//div[contains(text(),'汽车品牌') and @style='color:#888']/parent::node()/text()").get())
            item["boughtyear"] = boughtyear(response.xpath("//div[contains(text(),'购买年份') and @style='color:#888']/parent::node()/text()[2]").get())
            item["lastservice"] = lastservice(response.xpath("//div[contains(text(),'上一次保养') and @style='color:#888']/parent::node()/text()[2]").get())
            item["cartype"] = cartype(response.xpath("//div[contains(text(),'车辆类型') and @style='color:#888']/parent::node()/text()[2]").get())
            item["content"] = content(response.xpath("//div[@class='yp-descriprion']/text()").get())
            item["images"] = response.xpath("//a[@class='venobox']/@href").getall()
            item["tags"] = getTagidList(response.xpath("//div[contains(text(),'标签') and @style='color:#888']/parent::node()/text()[2]").get())
            
            mobile_headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36"}
            yield response.follow(url=str(id),callback =self.parse_mobile,headers = mobile_headers,dont_filter=True,meta={'item':item})

    def parse_mobile(self,response):
        item = response.meta['item']
        item['price'] = getPrice(response.xpath("//span[@class='mtg-ypprice__text']/text()").get())
        item['updatetime']= get_updatetime(response.xpath("//div[@class='mtg-yptitle-time']/text()").get())

        #seller info 
        item['username'] = response.xpath("//p[@style=' margin-top: -6px;']/text()").get()
        item["is_private"]= getSellertype(response.xpath("//span[@class='mtg-pill mtg-pill_blue mtg-pill_filled']/text()").get())
        item["userage"]=  get_userage(response.xpath("//p[@style='color: #888;font-size: 12px;']/text()").get())
        item['userimage'] = response.xpath("//img[@style='border-radius:30px']/@src").get()
       #item['phone'] = response.xpath("//label[@id='uMobile']/text()").get()
        item['wechat'] = response.xpath("//img[contains(@src,'wechat')]/following-sibling::span[1]/text()").get()
        #item['email'] = response.xpath("//label[@id='uMail']/text()").get()
        item['qq'] = response.xpath("//img[contains(@src,'qq')]/following-sibling::span[1]/text()").get()
        item['contactsScript']= response.xpath("//script[contains(text(),'uMobile')]/text()").get()
        yield item