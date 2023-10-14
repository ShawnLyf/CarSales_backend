from scrapy import Item,Field
from itemloaders.processors import MapCompose,TakeFirst
from datetime import datetime,date
import re

# for filter post list
def get_createtimelist(updatetimeText):
    updatePassed = [0,0,0,0]
    number = int(re.sub("\D","",updatetimeText))
    if '秒' in updatetimeText:
        updatePassed[3]=number
    elif '分钟' in updatetimeText:
        updatePassed[2]=number
    elif '小时' in updatetimeText:
        updatePassed[1]=number
    elif '天' in updatetimeText:
        updatePassed[0]=number
    return updatePassed


#from list page not null 
def get_updatetime(text):
    return text.replace("更新时间：","")
    
def getPrice(priceText):
    dolloar_replaced = priceText.replace("$","") # $9999->9999 
    meetup_repalced = dolloar_replaced.replace("面议","0")# 面议->0 
    int_price = int(meetup_repalced) 
    return int_price

def getSellertype(userText):
    is_private = True if userText=='个人' else False
    return is_private
 
def getCity(postText):
    cleaned_city = postText.strip('\n ') # "\n悉尼 "->"悉尼"
    return cleaned_city
    
def getId(link):
    trimed_id = link.split("/")[-1]  
    int_id = int(trimed_id) 
    return int_id


##  for detail page
# not null 
def views(viewsText):
    cleaned_views = viewsText.strip('浏览量 次')
    int_views = int(cleaned_views)
    return int_views

def brand(brandText):
    if brandText:
        cleaned_brand = brandText.strip('\n ') # "\nLexus "->"Lexus"
        return cleaned_brand

def boughtyear(boughtText):
    if boughtText:
        cleaned_boughtText = boughtText.strip(" ")
        int_year = int(cleaned_boughtText)
        return int_year

def cartype(typeText):
    if typeText:
        cleaned_typeText = typeText.strip(" ")
        return cleaned_typeText

def fueltype(typeText):
    if typeText:
        cleaned_typeText = typeText.strip(" ")
        return cleaned_typeText

def content(conetentList):
    if content:
        content_str =""
        for i in conetentList:
            content_str +=i
        cleaned_content = content_str.strip(" \n")
        
        return cleaned_content 


def mileage(mileageText):
    if mileageText: 
        cleaned_mileage = mileageText.strip(' 公里\n') #"25000 公里\n"->"2500"
        int_mileage = int(cleaned_mileage)  
        return int_mileage

def transmission(transmissionText):
    if transmissionText:
        ifauto = True if '手动' not in transmissionText else False
        return ifauto

def regodue(regoText):
    if regoText:
        cleaned_rego = regoText.strip(' ')
        return cleaned_rego

def lastservice(lastText):
    if lastText:
        cleaned_last = lastText.strip(' ')
        return cleaned_last

def getTagidList(tagsText):
    if tagsText:
        cleaned_tags = tagsText.strip(" ")
        tags = cleaned_tags.split(",") 
        tag_list_text = ['无事故','无划痕','保养正常','顶级配置','高性价比','准新车','回国急售','自动巡航','自带导航','真皮座椅','电动天窗','自带蓝牙','高级车载音响'] 
        tagid_list = []
        for tag in tags:
            tagid_list.append(tag_list_text.index(tag)+1)
        return tagid_list

def year(TitleText):
    replace_year = TitleText.replace("年","0101101嘂") # replace 年 since this is a usekeyword 
    number_string = re.sub("\D"," ",replace_year) # repalce all non-digit character
    string_list = number_string.split(" ") # split them 
    number_list = [x for x in string_list if x !="" and len(x) in [11,9,2,4]] # get number list 

    
    crnt_year = date.today().year
    for numberString in number_list:
        #if contain "0101101(年)" must is year
        if '0101101' in numberString:
            year = int(numberString.split("0101101")[0])
            if year <100: # 如果是两位数且<40或>80,则部族世纪（前两位）
                if year >=80:
                    year += 1900 
                elif year <= crnt_year%100+1:
                    year += 2000
                else:
                    year = None # 注意65年这种关键出现，year则直接被判为None
            return year
    # if year not found  check if 4 digits number are valid or not, if valid, return year
    for numberString in number_list:
        int_year = int(numberString)
        if len(numberString)==4 and int_year>=1980 and int_year<=crnt_year+1:
            return int_year
    
    # if year not found  check if 2 digits number are valid or not, if valid, return year
    for numberString in number_list:
        int_year = int(numberString)
        if len(numberString)==2:
            if int_year >=80:
                int_year += 1900 
                return int_year
            elif int_year <= crnt_year%100+1:
                int_year += 2000
                return int_year


## user detail
def get_userage(ageText):
    if ageText:
        cleaned_ageText = ageText.strip("加入「今日澳洲」天").replace("年","月")
        age_texts = cleaned_ageText.split("月")
        age_texts.reverse()
        user_age = [0,0,0]
        for idx in range(0,len(age_texts)):
            user_age[2-idx]= int(age_texts[idx])
        return user_age 


class PostItem(Item): 
    ## from list page
    is_active = Field(output_processor = TakeFirst())
    postid = Field(output_processor = TakeFirst()) 
    price = Field(output_processor = TakeFirst())
    updatetime = Field(output_processor = TakeFirst())
    
    ## form detail page: post info
    title = Field(output_processor = TakeFirst())
    mileage = Field(input_processor = MapCompose(mileage),output_processor = TakeFirst())
    transmission = Field(input_processor = MapCompose(transmission),output_processor = TakeFirst())
    regodue = Field(input_processor = MapCompose(regodue),output_processor = TakeFirst())
    suburb = Field(output_processor = TakeFirst())
    year = Field(input_processor = MapCompose(year),output_processor = TakeFirst())
    views = Field(input_processor = MapCompose(views),output_processor = TakeFirst())
    brand = Field(input_processor = MapCompose(brand),output_processor = TakeFirst())
    boughtyear = Field(input_processor = MapCompose(boughtyear),output_processor = TakeFirst())
    lastservice = Field(input_processor = MapCompose(lastservice),output_processor = TakeFirst())
    cartype = Field(input_processor = MapCompose(cartype),output_processor = TakeFirst())
    fueltype = Field(input_processor = MapCompose(fueltype),output_processor = TakeFirst())
    content = Field(input_processor = MapCompose(content),output_processor = TakeFirst())
    images = Field()
    tags = Field(input_processor = MapCompose(getTagidList))
   
    # from mobile page: seller info
    username = Field(output_processor = TakeFirst())
    is_private = Field(input_processor = MapCompose(getSellertype),output_processor = TakeFirst())
    userage = Field(input_processor = MapCompose(get_userage),)
    userimage = Field(output_processor = TakeFirst())
    wechat = Field(output_processor = TakeFirst())
    # phone = Field(output_processor = TakeFirst())
    # email = Field(output_processor = TakeFirst())
    qq = Field(output_processor = TakeFirst())
    contactsScript = Field(output_processor = TakeFirst())
    
    


  
     
