create type cartag as enum ('无事故','无划痕','保养正常','顶级配置','高性价比','准新车','回国急售','自动巡航','自带导航','真皮座椅','电动天窗','自带蓝牙','高级车载音响');
create type fueltype as enum ('汽油','柴油','混合动力','天然气','纯电动');
create type city as enum('悉尼','卧龙岗','纽卡斯尔','中央海岸','墨尔本','基隆','布里斯班','黄金海岸','凯恩斯','阳光海岸','堪培拉','阿德莱德','珀斯','霍巴特','达尔文');
set timezone = 'Australia/Sydney';
CREATE TABLE tag (
    id SERIAL PRIMARY KEY,
    tagname cartag NOT NULL
);

CREATE TABLE carmodel (
    id SERIAL PRIMARY KEY,
    brand varchar(50) NOT NULL,
    model varchar(50) NOT NULL,
    unique(brand, model)
);

CREATE TABLE seller (
    username varchar(50) NOT NULL PRIMARY KEY,
    is_private boolean ,
    userage date ,
    userimage varchar(300),

    phones varchar(50)[],
    wechats varchar(50)[],
    qqs varchar(50)[],
    emails varchar(100)[],

    contacts smallint,
    reports smallint,
    dealerage smallint,
    website varchar(100),
    dealertitle varchar(100),
    company varchar(100),
    business varchar(50)[],
    CHECK (contacts >= 0),
    CHECK (dealerage >= 0),
    CHECK (reports >= 0)
);

CREATE TABLE post (
    id bigint NOT NULL,
    is_active boolean NOT NULL default True,
    title varchar(100) ,
    price integer,
    createtime timestamptz not null,
    updatetime varchar(20),
    lastrequest_time timestamp, -- default sydney time, since the server in East
    postcity city,

    views smallint,
    mileage bigint, 
    is_auto boolean,
    regodue varchar(20),
    suburb varchar(50),
    video varchar(300),
    year smallint,
    prevprice integer,
    boughtyear smallint,
    content text,
    fueltype fueltype,
    lastservice varchar(20),
    
    likes smallint,
    reviews varchar(300)[],
    images varchar(300)[],
    carmodel_id smallint,
    seller_username varchar(50),
    PRIMARY KEY(id,is_active),
    FOREIGN KEY(seller_username) REFERENCES seller(username) on update cascade,
    FOREIGN KEY(carmodel_id) REFERENCES carmodel(id),

    CHECK (mileage >= 0),
    CHECK (price >= 0),
    CHECK (year >= 1000),
    CHECK (boughtyear >= 1000),
    CHECK (prevprice >= 1000),
    CHECK (likes >= 0),
    CHECK (views >= 0)
) PARTITION BY LIST(is_active);
create table active partition of post for values in(True);
create table removed partition of post for values in(False);

CREATE TABLE post_tag (
    postid bigint not NULL,
    post_isactive boolean not NULL,
    tagid int not null,
    unique(postid,post_isactive,tagid),
    FOREIGN KEY (postid,post_isactive) REFERENCES post(id,is_active) on update cascade,
    FOREIGN KEY (tagid) REFERENCES tag(id)
);