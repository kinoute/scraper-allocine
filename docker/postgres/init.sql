CREATE TABLE public.movies (
    id int PRIMARY KEY,
    title varchar(255),
    release_date timestamp default NULL,
    duration integer,
    genres varchar(255),
    directors varchar(255),
    actors varchar(255),
    press_rating NUMERIC(5,2),
    spec_rating NUMERIC(5,2),
    summary text
);
