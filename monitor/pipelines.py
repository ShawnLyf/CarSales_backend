# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2,psycopg2.extras
from datetime import time

class MonitorPipeline:
     def process_item(self, item, spider):
        return item 


class TopsqlPipeline:
    def open_spider(self,spider):
        self.cnn = psycopg2.connect(
            host = 'uowlibrary.cfgr3kbul23x.ap-southeast-2.rds.amazonaws.com',
            database = 'todaysydney',
            user = 'shawn',
            password = 'mlpmlpmlp'
        )
        self.cur = self.cnn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def process_item(self, item, spider):
        self.load_seller(item)
        self.load_post(item) 
        return item 
        
    def close_spider(self,spider):
        self.cur.execute("delete from post where images IS NULL")
        self.cur.execute("""
                    DELETE FROM post_tag 
                    WHERE postid IN (
                        SELECT postid 
                        FROM post
                        WHERE title LIKE '%学妹%'
                           or title like '%按摩%'
                           or title like '%Ka Kit Yau%'
                           or title like '%全澳最大埃尔法经销商Evan有现车%'
                    );
                    """)
        self.cur.execute("""delete from post where 
                               title like '%学妹%' 
                            or title like '%按摩%'
                            or title like '%Ka Kit Yau%'
                            or title like '%全澳最大埃尔法经销商Evan有现车%'
                         """) 
        
        self.cnn.commit() 
        self.cur.close()
        self.cnn.close()

    def load_seller(self,item): 
        def insert_user():
            self.cur.execute('''insert into seller(username,is_private,userage,userimage,phones,wechats,emails,qqs) values(%s,%s,now()-interval %s,%s,%s,%s,%s,%s);''',
            (new_username,is_private,interval,userimage,self.filter_none([phone]),self.filter_none([wechat]),self.filter_none([email]),self.filter_none([qq])))
            self.cnn.commit()
        def update_userothers():
            self.cur.execute('''update seller set 
            is_private = %s, 
            userage = now()-interval %s, 
            userimage = %s,
            phones = array_remove(array_prepend(%s,array_remove(phones,%s)),Null),
            wechats = array_remove(array_prepend(%s,array_remove(wechats,%s)),Null),
            emails = array_remove(array_prepend(%s,array_remove(emails,%s)),Null),
            qqs = array_remove(array_prepend(%s,array_remove(qqs,%s)),Null)
            where username = %s;''',(is_private,interval,userimage,phone,phone,wechat,wechat,email,email,qq,qq,new_username))
            self.cnn.commit()
       
        def update_userusername(new_username,crnt_username):
            self.cur.execute("update seller set username = %s where username = %s",(new_username,crnt_username))
            self.cnn.commit()
        def get_phone_email(contactsScript):
            contacts =  contactsScript.split(";")[:3]
            phone = None
            email = None
            
            for contact in contacts:
                if 'uMobile' in contact:
                    phoneText = contact.split('"')[1]
                    phone = phoneText if phoneText != '' else None
                if 'uMail' in contact:
                    emailText = contact.split('"')[1]
                    email = emailText if emailText != '' else None
            return phone,email

        id = item.get('postid')
        new_username = item.get('username')
        is_private = item.get('is_private')
        userage = item.get('userage')
        interval = f'{userage[0]} year {userage[1]} months {userage[2]} days'

        userimage =item.get('userimage')
        wechat = item.get('wechat')  
        qq = item.get('qq')
        
        # phone = item.get('phone')
        # email = item.get('email')
        phone,email = get_phone_email(item.get('contactsScript'))

        # check if is new post, all old post have a username, new post don't 
        self.cur.execute("select seller_username from post where id = %s",(id,))
        crnt_username = self.cur.fetchone()['seller_username']
        is_newpost =  crnt_username == None # with record but not username 
        print("------------------------------ if new post ----------------------------------- ")
        print()
        print("is_newpost: "+str( is_newpost))
        print()
        print("************************************************************************* ")
        if is_newpost:
            # check if new_username is exist or not, if not exist, means new user, 
            self.cur.execute("select username from seller where username = %s",(new_username,))
            is_newuser = self.cur.fetchone() == None # without record
            if is_newuser: # new user, new post -> insert new user
                print("------------------------------ if new post ----------------------------------- ")
                print()
                print("is new user: "+str( is_newuser))
                print()
                print("************************************************************************* ")
                insert_user()
            else: # existing user, new post -> update userdetail
                update_userothers()
        else:# if old post, means refresh 
            if new_username != crnt_username: # user_changed username when having posting -> update the existing post's username by update the current username and cascade update
                update_userusername(new_username,crnt_username)
            update_userothers()   # then update the seller other information 
       
    

    # load post for posts with preload, and  posts refreshed
    def load_post(self,item):
        id = item.get('postid')
        title = item.get('title')
        views = item.get('views')
        mileage = item.get('mileage')
        is_auto = item.get('transmission')
        regodue = item.get('regodue')
        suburb = item.get('suburb')
        year = item.get('year')
        boughtyear = item.get('boughtyear')
        content = item.get('content')
        fueltype = item.get('fueltype')
        lastservice = item.get('lastservice')
        images = item.get('images')
        username = item.get('username')
        price = item.get('price')
        updatetime = item.get('updatetime')
        brand = item.get('brand')
        model = self.getModelFromTitle(item.get('title'),brand)
        self.cur.execute("select id from carmodel where brand = %s and model = %s",(brand,model))
        return_id = self.cur.fetchone()
        if return_id:
            carmodel_id = return_id.get('id')
        else:
            carmodel_id = 1498 # be careful with this number(it means the car with unknown model and brand)
        
        self.cur.execute("""update post set
        lastrequest_time = now(),
        title = %s,
        views = %s,
        mileage = %s,
        is_auto = %s,
        regodue = %s,
        suburb = %s,
        year = %s,
        boughtyear = %s,
        content = %s,
        fueltype = %s,
        lastservice = %s,
        images = %s,
        carmodel_id = %s,
        seller_username = %s,
        price = %s,
        updatetime = %s
        where id = %s""",(title,views,mileage,is_auto,regodue,suburb,year,boughtyear,content,fueltype,lastservice,images,carmodel_id,username,price,updatetime
        ,id))
        self.cnn.commit()

        tagid_list = item.get('tags')
        print("tagid_list")
        print(tagid_list)
        self.load_postTag(id,True,tagid_list)


    def filter_none(self,list):
        return [x for x in list if x is not None]
    
    def getModelFromTitle(self,title,brand):
        self.cur.execute("select model from carmodel where brand = %s and model <> 'other' order by length(model) desc",(brand,))
        model_list = self.cur.fetchall()
        model = "other"
        for modelDict in model_list:
            if (modelDict['model']+" ").lower() in title.lower():
                model = modelDict['model']
                break
        return model

    def load_postTag(self,postid,is_active,tagid_list):
        #remove old many to many table first 
        self.cur.execute("delete from post_tag where postid = %s",(postid,))
        self.cnn.commit()
        if tagid_list:
            for tag_id in tagid_list:
                self.cur.execute("insert into post_tag values(%s,%s,%s)",(postid,is_active,tag_id))
                self.cnn.commit()
   
  


        
