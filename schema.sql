create table if not exists flickr_meta (
    id                integer primary key autoincrement not null,
    photo_id          integer not null,
    username          text,
    photo_title       text,
    description       text,
    photo_url         text,
    latitude         double,
    longitude         double,
    created           timestamp default CURRENT_TIMESTAMP,
    updated           timestamp default CURRENT_TIMESTAMP,
    constraint unique_photo_id unique (photo_id)
);

