# reset database
export PGPASSWORD='mlpmlpmlp'
psql -h uowlibrary.cfgr3kbul23x.ap-southeast-2.rds.amazonaws.com -U shawn  -d postgres -c 'drop database todaysydney'
psql -h uowlibrary.cfgr3kbul23x.ap-southeast-2.rds.amazonaws.com -U shawn  -d postgres -c 'create database todaysydney'

# creat schemas
psql -h uowlibrary.cfgr3kbul23x.ap-southeast-2.rds.amazonaws.com -U shawn  -d todaysydney -a -f data/dbcreate.sql

# # # load initial records for monitor database
psql -h uowlibrary.cfgr3kbul23x.ap-southeast-2.rds.amazonaws.com -U shawn  -d todaysydney  -f data/dbload.sql


# reset django migration to database
rm -rf today/migrations
mkdir today/migrations
touch today/migrations/__init__.py

# import the datamodel from legacy database and migrate django schemas,  run this if anyupdate of your data model
# python manage.py inspectdb > today/models.py



# after create auth_user schema, now we can create authuser_post
psql -h uowlibrary.cfgr3kbul23x.ap-southeast-2.rds.amazonaws.com -U shawn  -d todaysydney -a -f data/dbcreate2.sql;

