SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));
use bechdel;
-- select * from 
-- movies
-- where primaryTitle ='WALL·E';

-- select * from bechdel
-- where movieID = 910970;


-- What is the bechdel rating for the Wall-E movie?

SELECT * FROM movies JOIN bechdel 
ON movies.movieId = bechdel.movieId
where primaryTitle like '%WALL·E%';
-- Which actor has played in a most different genres of the movies?
SELECT *
FROM movies 
left JOIN  movies.movieId ON movies.movieId = moviesgenres.movieId
left join movies.movieId on movies.movieId =  moviespeople.movieId;

SELECT COUNT(*) AS total FROM Movies;



-- select * from people
-- where personID = 79677
-- group by personID
-- order by count(*) desc;

-- SELECT * FROM Movies
-- WHERE movieId IN "%1%"
-- ORDER BY movieId
-- LIMIT 
-- OFFSET

-- ORDER BY movieId
-- LIMIT %s
-- OFFSET %s
  --   P.personId,
--     P.primaryName AS name,
--     P.birthYear,
--     P.deathYear,
--     MP.job,
--     MP.category AS role,
--     
-- JOIN FFFFF ON FFFFF ON  DDDDDD
-- JOIN People P on P.personId = MP.personId
-- ;

SELECT 
    M.movieId,
    M.originalTitle,
    M.primaryTitle AS englishTitle,
    B.rating AS bechdelScore,
    M.runtimeMinutes,
    M.startYear AS Year,
    M.movieType,
    M.isAdult,
    MG.movieGenreId,
    MG.genre,
    MP.personID,
    P.primaryName as name,
    MP.job as role
FROM Movies M
JOIN Bechdel B ON B.movieId = M.movieId    
JOIN moviesgenres MG ON MG.movieID = M.movieId 
JOIN moviespeople MP ON MP.movieID = M.movieId 
JOIN people P on P.personID = MP.personID
ORDER BY movieId;


SELECT 
    M.movieId,
    MG.genre
FROM Movies M
JOIN moviesgenres MG ON MG.movieID = M.movieId 
ORDER BY movieId;



SELECT 
    M.movieId,
	MP.personID,
    P.primaryName as name,
    MP.job as role
from movies M
JOIN moviespeople MP ON MP.movieID = M.movieId 
JOIN people P on P.personID = MP.personID

ORDER BY movieId;

SELECT p.personID,category,job,primaryName,birthYear,deathYear FROM MoviesPeople MP
                         JOIN PEOPLE P ON P.PERSONid = MP.PERSONID
                         join movies m on m.movieid = mp.movieID
                         WHERE MP.personid=1
                         group by p.personID     ;         
SELECT mp.characters, m.primarytitle, mp.personID
 FROM MoviesPeople MP
 join movies m on m.movieid = mp.movieID
        WHERE MP.personid=1
                      