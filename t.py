import psycopg2,psycopg2.extras 
def remove_none_image_records():
    cnn = psycopg2.connect(
        host='uowlibrary.cfgr3kbul23x.ap-southeast-2.rds.amazonaws.com',
        database = 'todaysydney',
        user = 'shawn',
        password = 'mlpmlpmlp'
    )
    cur = cnn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("delete from post where images IS NULL")
    cnn.commit()  
    cnn.close() 
remove_none_image_records()