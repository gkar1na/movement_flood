SET TIME ZONE 'Europe/Moscow';
ALTER DATABASE movement SET datestyle TO GERMAN;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE IF NOT EXISTS user_data (
    uid uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    tg_chat_id numeric unique,
    tg_username varchar unique NOT NULL,
    b_date date,
    is_admin bool DEFAULT false,
    congratulated bool DEFAULT false
);
CREATE TABLE IF NOT EXISTS group_chat (
    uid uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    chat_id numeric unique NOT NULL,
    chat_name varchar NOT NULL,
    is_verified bool DEFAULT false
);
CREATE TABLE IF NOT EXISTS congratulation (
    uid uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    text text NOT NULL,
    used bool DEFAULT false
);
