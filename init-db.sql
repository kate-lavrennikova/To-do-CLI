CREATE TABLE app_user(
    id serial primary key,
    user_name varchar(50) not null unique,
    user_password varchar(20) not null
);

CREATE TABLE task(
    id serial primary key,
    task_description varchar(150) not null,
    task_date date not null,
    done boolean,
    important boolean,
    user_id serial,
    CONSTRAINT fk_user
      FOREIGN KEY(user_id) 
        REFERENCES app_user(id)
);