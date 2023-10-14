dbload = open('data/dbload.sql','a')
with open('carmodel.html') as r:
    brand = ""
    model = ""
    for line in r:
        if "name" in line:
            brand = line.split("\"")[3]
            dbload.write("-- insert carmodels for "+brand+"\n")
        elif 'value' in line:
            l = line.replace(">","<")
            model =  l.split("<")[2]
            if model =='其他':
                model = 'other'
            sql = "INSERT INTO carmodel (brand, model) VALUES ('"+brand+"','"+model+"');\n"
            dbload.write(sql)
            
dbload.write("\n")     
dbload.close()