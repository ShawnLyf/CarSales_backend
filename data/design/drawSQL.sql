CREATE TABLE "post"(
    "postid" BIGINT NOT NULL,
    "isActivate" BOOLEAN NOT NULL,
    "mileage" BIGINT NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "price" INTEGER NOT NULL,
    "transmission" BOOLEAN NOT NULL,
    "rego" DATE NOT NULL,
    "suburb" VARCHAR(255) NOT NULL,
    "video" VARCHAR(255) NULL,
    "year" INTEGER NULL,
    "lastprice" INTEGER NULL,
    "boughtyear" DATE NULL,
    "content" VARCHAR(255) NULL,
    "fueltype" VARCHAR(255) CHECK
        ("fueltype" IN('')) NULL,
        "lastservice" DATE NULL,
        "views" SMALLINT NOT NULL,
        "createtime" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
        "updatetime" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
        "updates" SMALLINT NOT NULL,
        "postcity" VARCHAR(255)
    CHECK
        ("postcity" IN('')) NOT NULL,
        "likes" SMALLINT NOT NULL,
        "reviews" VARCHAR(255) NULL,
        "brandmodel" SMALLINT NULL,
        "images" TEXT NOT NULL,
        "seller" SMALLINT NOT NULL,
        "tags" VARCHAR(255)
    CHECK
        ("tags" IN('')) NOT NULL
);
ALTER TABLE
    "post" ADD PRIMARY KEY("postid");
COMMENT
ON COLUMN
    "post"."rego" IS 'year and month';
COMMENT
ON COLUMN
    "post"."year" IS 'slice from title, if not found, set none';
COMMENT
ON COLUMN
    "post"."boughtyear" IS 'year only';
COMMENT
ON COLUMN
    "post"."lastservice" IS 'year/month';
COMMENT
ON COLUMN
    "post"."createtime" IS 'post = activepost.object.get(postid=postid)
if post == None: ->(now - interval) (when create the activepost)';
COMMENT
ON COLUMN
    "post"."updatetime" IS 'if new:
    createtime = now - interval
else:
    updates +=1 
updatetime = now-interval

-- lastupdatetime';
COMMENT
ON COLUMN
    "post"."reviews" IS 'future fuction';
CREATE TABLE "tags"(
    "id" SMALLINT NOT NULL,
    "tag" VARCHAR(255) CHECK
        ("tag" IN('')) NOT NULL
);
ALTER TABLE
    "tags" ADD PRIMARY KEY("id");
CREATE TABLE "model"(
    "id" SMALLINT NOT NULL,
    "brand" VARCHAR(255) NOT NULL,
    "model" VARCHAR(255) NOT NULL
);
ALTER TABLE
    "model" ADD PRIMARY KEY("id");
CREATE TABLE "car-tags"("id" BIGINT NOT NULL);
ALTER TABLE
    "car-tags" ADD PRIMARY KEY("id");
CREATE TABLE "seller"(
    "username" VARCHAR(255) NOT NULL,
    "userage" SMALLINT NOT NULL,
    "sellerimage" VARCHAR(255) NOT NULL,
    "contacts" SMALLINT NOT NULL,
    "reports" SMALLINT NOT NULL,
    "phones" TEXT NOT NULL,
    "wechat" TEXT NOT NULL,
    "qqs" TEXT NOT NULL,
    "emails" TEXT NOT NULL,
    "sellertype" BOOLEAN NOT NULL,
    "dealerage" SMALLINT NOT NULL,
    "website" VARCHAR(255) NULL,
    "dealertitle" VARCHAR(255) NULL,
    "company" VARCHAR(255) NULL,
    "business" VARCHAR(255) NULL
);
ALTER TABLE
    "seller" ADD PRIMARY KEY("username");
CREATE TABLE "brand"(
    "id" BIGINT NOT NULL,
    "brandname" BIGINT NOT NULL
);
ALTER TABLE
    "brand" ADD PRIMARY KEY("id");
ALTER TABLE
    "model" ADD CONSTRAINT "model_brand_foreign" FOREIGN KEY("brand") REFERENCES "brand"("id");