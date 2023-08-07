create schema user_info;

create table if not exists user_info.user  (
    id bigint,
    first_name varchar(70),
    last_name varchar(70),
    full_name varchar(140),
    email varchar(140),
    gender varchar(70),
    ip_address varchar(16)
);
