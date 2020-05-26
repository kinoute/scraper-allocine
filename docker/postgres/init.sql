CREATE TABLE public.movies (
    id int PRIMARY KEY,
    title varchar(255),
    release_date varchar(255),
    duration varchar(255),
    genres varchar(255),
    directors varchar(255),
    actors varchar(255),
    press_rating NUMERIC(5,2),
    spec_rating NUMERIC(5,2),
    summary text
);
