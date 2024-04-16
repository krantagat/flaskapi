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

def remove_null_fields(obj):

    return {k:v for k, v in obj.items() if v is not None}


#  show all countries
@app.route("/foodwastes/")
@auth.required
def foodwastes():
    db_conn = pymysql.connect(host="localhost", user="root"
                              ,password=os.getenv('kranta_sql_password')
                              , database="api_foodwaste"
                              ,cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""
                        SELECT 
                       
                        country,region,`combined_figures_(kg/capita/year)`,
                        `household_estimate_(kg/capita/year)`,`retail_estimate_(kg/capita/year)`,
                        `food_service_estimate_(kg/capita/year)`
                        FROM foodwaste 
                       
                            """)
        foodwastes = cursor.fetchall()

    db_conn.close() 

    return foodwastes

# Per country search by country name if no country enter show all countries
# in the country_name input conver space " " to %20
@app.route("/foodwastes/<country_name>")
@auth.required
def foodwaste(country_name):
    db_conn = pymysql.connect(host="localhost", user="root"
                              ,password=os.getenv('kranta_sql_password')
                              , database="api_foodwaste"
                              ,cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""
SELECT
                       
country,region,`combined_figures_(kg/capita/year)`,`household_estimate_(kg/capita/year)`,`retail_estimate_(kg/capita/year)`,`food_service_estimate_(kg/capita/year)`
                            FROM foodwaste 
                         
                            WHERE country =%s
                            """,(country_name,))
        foodwaste = cursor.fetchone()

        if not foodwaste:
            abort(404)
        foodwaste = remove_null_fields(foodwaste)
    db_conn.close() 

    return foodwaste



# Per country search by country name if no country enter show all countries
# in the country_name input conver space " " to %20
@app.route("/foodwastes/by_fruit/<fruit_name>")
@auth.required
def foodwaste_fruit(fruit_name):
    db_conn = pymysql.connect(host="localhost", user="root"
                              ,password=os.getenv('kranta_sql_password')
                              , database="api_foodwaste"
                              ,cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""select * from foodwaste 
join fruit on fruit.country = foodwaste.country
where fruit.common_name = %s
                            """,(fruit_name,))
        foodwaste_fruit = cursor.fetchone()

        if not foodwaste_fruit:
            abort(404)
        foodwaste_fruit = remove_null_fields(foodwaste_fruit)
    db_conn.close() 

    return foodwaste_fruit



