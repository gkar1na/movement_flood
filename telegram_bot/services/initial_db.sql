SET TIME ZONE 'Europe/Moscow';
ALTER DATABASE movement SET datestyle TO GERMAN;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE IF NOT EXISTS user_data (
    uid uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    tg_chat_id numeric unique NOT NULL,
    tg_username varchar unique NOT NULL,
    b_date date,
    is_admin bool DEFAULT false,
    congratulated bool DEFAULT false
);
