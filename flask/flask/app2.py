# Let's write your code here!
from flask import Flask, abort
from flask_basicauth import BasicAuth
from flask import request
from collections import defaultdict
import math
import json
import pymysql
import os
from flask_swagger_ui import get_swaggerui_blueprint



app = Flask(__name__)
app.config.from_file("flask_config.json", load=json.load)
auth = BasicAuth(app)
# PAGE_SIZE = 100
MAX_PAGE_SIZE = 100






@app.route("/movies/<int:movie_id>")
# @auth.required
def movie(movie_id):
    db_conn = pymysql.connect(host="localhost", user="root"
                              ,password=os.getenv('kranta_sql_password')
                              , database="bechdel"
                              ,cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""SELECT
    M.movieId,
    M.originalTitle,
    M.primaryTitle AS englishTitle,
    B.rating AS bechdelScore,
    M.runtimeMinutes,
    M.startYear AS Year,
    M.movieType,
    M.isAdult
FROM Movies M
JOIN Bechdel B ON B.movieId = M.movieId 
WHERE M.movieId=%s""", (movie_id, ))
        movie = cursor.fetchone()
        if not movie:
            abort(404)
        movie = remove_null_fields(movie)

    
    with db_conn.cursor() as cursor:
        cursor.execute("""SELECT * FROM MoviesGenres WHERE movieId=%s""", (movie_id, ))
        genres = cursor.fetchall()
        movie['genres'] = [g['genre'] for g in genres]
        
    with db_conn.cursor() as cursor:
        cursor.execute("""
            SELECT
    P.personId,
    P.primaryName AS name,
    P.birthYear,
    P.deathYear,
    MP.job,
    MP.category AS role
FROM MoviesPeople MP
JOIN People P on P.personId = MP.personId
WHERE MP.movieId=%s
        """, (movie_id, ))
        people = cursor.fetchall()
        # movie['people'] = people
        movie['people'] = [remove_null_fields(p) for p in people]

    db_conn.close() 

    return movie 


def remove_null_fields(obj):

    return {k:v for k, v in obj.items() if v is not None}




# @app.route("/movies")
# def movies():
#     page = int(request.args.get('page', 1))
#     page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
#     page_size = min(page_size, MAX_PAGE_SIZE)
#     include_details = bool(int(request.args.get('include_details',0)))
    
#     db_conn = pymysql.connect(host="localhost"
#                               , user="root" 
#                               , password=os.getenv('kranta_sql_password') 
#                               , database="bechdel"
#                               ,cursorclass=pymysql.cursors.DictCursor)

#     with db_conn.cursor() as cursor:
#         cursor.execute("""                  
# SELECT 
#     M.movieId,
#     M.originalTitle,
#     M.primaryTitle AS englishTitle,
#     B.rating AS bechdelScore,
#     M.runtimeMinutes,
#     M.startYear AS Year,
#     M.movieType,
#     M.isAdult
#     FROM Movies M
#     JOIN Bechdel B ON B.movieId = M.movieId    
#     ORDER BY M.movieId
#     LIMIT %s
#     OFFSET %s"""
#     , (page_size, (page-1) * page_size))
#         movies = cursor.fetchall()
#         movieIDs =[movie['movieId'] for movie in movies] 
        
#         genre_list = defaultdict(list)
#         people_list = defaultdict(list)
        
        
# if include_details:

    
#     with db_conn.cursor() as cursor:
#         placeolder = ','.join(['%s'])
#         cursor.execute(f"""
#     SELECT 
#         MP.movieId 
#         MP.personID,
#         P.primaryName as name,
#         MP.job as role,
#     from moviespeople MP
#     JOIN people P on P.personID = MP.personID
#     WHERE MP.movieId IN {(("%s,") * len(movieIDs))[:-1]},movieIDs""")
#     people = cursor.fetchone()
#     people_list['people'].append(people)
     
#     with db_conn.cursor() as cursor:
#         cursor.execute(f"""
# SELECT 
#     MG.genre
# FROM Movies M
# JOIN moviesgenres MG ON MG.movieID = M.movieId 
# WHERE movieId IN  (("%s,") {* len(movieIDs))[:-1]},movieIDs"""
#         genre = cursor.fetchone()
#         genre_list['genre'].append(genre)
        
#     with db_conn.cursor() as cursor:
#         cursor.execute("SELECT COUNT(*) AS total FROM Movies")
#         total = cursor.fetchone()
#         last_page = math.ceil(total['total'] / page_size)
    

#     db_conn.close()
#     return {
#         'movies': movies,
#         'next_page': f'/movies?page={page+1}&page_size={page_size}',
#         'last_page': f'/movies?page={last_page}&page_size={page_size}',
#     }



@app.route("/movies")
@auth.required
def movies():
    # URL parameters
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
    page_size = min(page_size, MAX_PAGE_SIZE)
    include_details = bool(int(request.args.get('include_details', 0)))

    db_conn = pymysql.connect(host="localhost", user="root",password=os.getenv('kranta_sql_password') ,database="bechdel",
                              cursorclass=pymysql.cursors.DictCursor)
    # Get the movies
    with db_conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                M.movieId,
                M.originalTitle,
                M.primaryTitle AS englishTitle,
                B.rating AS bechdelScore,
                M.runtimeMinutes,
                M.startYear AS year,
                M.movieType,
                M.isAdult
            FROM Movies M
            JOIN Bechdel B ON B.movieId = M.movieId 
            ORDER BY movieId
            LIMIT %s
            OFFSET %s
        """, (page_size, (page-1) * page_size))
        movies = cursor.fetchall()
        movie_ids = [mov['movieId'] for mov in movies]
    
    if include_details:
        # Get genres
        with db_conn.cursor() as cursor:
            placeholder = ','.join(['%s'] * len(movie_ids))
            cursor.execute(f"SELECT * FROM MoviesGenres WHERE movieId IN ({placeholder})",
                        movie_ids)
            genres = cursor.fetchall()
        genres_dict = defaultdict(list)
        for obj in genres:
            genres_dict[obj['movieId']].append(obj['genre'])
        
        # Get people
        with db_conn.cursor() as cursor:
            placeholder = ','.join(['%s'] * len(movie_ids))
            cursor.execute(f"""
                SELECT
                    MP.movieId,
                    P.personId,
                    P.primaryName AS name,
                    P.birthYear,
                    P.deathYear,
                    MP.category AS role
                FROM MoviesPeople MP
                JOIN People P on P.personId = MP.personId
                WHERE movieId IN ({placeholder})
            """, movie_ids)
            people = cursor.fetchall()
        people_dict = defaultdict(list)
        for obj in people:
            movieId = obj['movieId']
            del obj['movieId']
            people_dict[movieId].append(obj)

        # Merge genres and people into movies
        for movie in movies:
            movieId = movie['movieId']
            movie['genres'] = genres_dict[movieId]
            movie['people'] = people_dict[movieId]

    # Get the total movies count
    with db_conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM Movies")
        total = cursor.fetchone()
        last_page = math.ceil(total['total'] / page_size)

    db_conn.close()
    return {
        'movies': movies,
        'next_page': f'/movies?page={page+1}&page_size={page_size}&include_details={int(include_details)}',
        'last_page': f'/movies?page={last_page}&page_size={page_size}&include_details={int(include_details)}',
    }
    
    
swaggerui_blueprint = get_swaggerui_blueprint(
    base_url='/docs',
    api_url='/static/openapi.yaml',
)
app.register_blueprint(swaggerui_blueprint)



@app.route("/people/<int:person_id>")
# @auth.required
def people(person_id):
    # page = int(request.args.get('page',0))
    db_conn = pymysql.connect(host="localhost", user="root"
                              ,password=os.getenv('kranta_sql_password')
                              , database="bechdel"
                              ,cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute(""" SELECT p.personID,category,job,primaryName,birthYear,deathYear FROM MoviesPeople MP
                         JOIN PEOPLE P ON P.PERSONid = MP.PERSONID
                         WHERE MP.personid=%s""",(person_id,) )
        person = cursor.fetchone()
        
    with db_conn.cursor() as cursor:
        cursor.execute("""       SELECT mp.characters, m.primarytitle, mp.personID
                        FROM MoviesPeople MP
                        join movies m on m.movieid = mp.movieID
                        WHERE MP.personid=%s""",(person_id,) )
        characters = cursor.fetchall()
        person['characters'] = characters 
    
    return {'person' : person}