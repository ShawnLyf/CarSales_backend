create table authuser_post(
    authuser_id int,
    post_id bigint,
    post_isactive BOOLEAN,
    is_viewed boolean not null default false,
    is_favorite boolean not null default false,
    price_viewed bigint not null,
    PRIMARY KEY(authuser_id,post_id,post_isactive),
    FOREIGN KEY(authuser_id) REFERENCES auth_user(id),
    FOREIGN KEY(post_id,post_isactive) REFERENCES post(id,is_active)
)