"""
Main application for the "Recept från kylen" web service.

Provides user registration, authentication, recipe search via Spoonacular API,
and management of user favorites using a PostgreSQL backend.
"""

import os

# Standard library imports
from dotenv import load_dotenv

# Third-party imports
from bottle import (
    route, run, template, request, static_file,
    response, redirect, HTTPResponse, TEMPLATE_PATH
)
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import errors
import bcrypt
import requests
import json

# Load environment variables and configure templates
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_PATH.insert(0, os.path.join(BASE_DIR, 'views'))
load_dotenv()

API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')


def get_db_connection():
    """
    Create and return a new database connection.

    Uses environment variables for host, port, dbname, user, and password.
    The cursor_factory is set to RealDictCursor for dict-like fetches.

    :return: psycopg2 connection object
    """
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor
    )


@route('/')
def index():
    """
    Render the home page.

    Query parameters:
        login=1   -> show welcome alert
        logout=1  -> show logout confirmation

    If user is logged in (cookie present), look up username.

    :return: rendered index template
    """
    recipes = []  # no search results on GET
    login_success = request.query.login == '1'
    logout_success = request.query.logout == '1'

    user_id = request.get_cookie('user_id', secret=SECRET_KEY)
    username = None
    if user_id:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT username FROM users WHERE id = %s", (user_id,)
                )
                row = cur.fetchone()
                if row:
                    username = row['username']

    return template(
    'index',
    recipes=recipes,
    login_success=login_success,
    logout_success=logout_success,
    login_error=None,
    username=username,
    no_results=False,
    email=None
    )

@route('/', method='POST')
def get_recipes():
    """
    Handle recipe search form submission using diet + ingredients.
    Fetches recipes from Spoonacular API and filters based on diet manually.
    """
    ingredients = request.forms.get('ingredients', '').strip()
    diet = request.forms.get('diet', '').strip().lower()

    # Base API URL
    url = 'https://api.spoonacular.com/recipes/complexSearch'
    params = {
        'apiKey': API_KEY,
        'number': 20,
        'addRecipeInformation': True,
        'fillIngredients': True
    }

    # Optional query parameters
    if ingredients:
        params['query'] = ingredients
    if diet:
        params['diet'] = diet

    # Fetch basic recipe list
    resp = requests.get(url, params=params)
    print("STATUSKOD:", resp.status_code)
    print("SVAR:", resp.text)

    data = resp.json() if resp.status_code == 200 else {}
    results = data.get('results', [])

    recipes = []

    # Define keywords for dietary filtering
    meat_words = ['chicken', 'beef', 'pork', 'bacon', 'turkey', 'ham', 'lamb']
    dairy_egg_words = ['cheese', 'egg', 'milk', 'butter', 'yogurt', 'cream', 'honey']

    for r in results:
        # Make a detailed API call for each recipe to get nutrition and steps
        info_url = f"https://api.spoonacular.com/recipes/{r['id']}/information"
        info_params = {'apiKey': API_KEY, 'includeNutrition': True}
        info_resp = requests.get(info_url, params=info_params)

        if info_resp.status_code != 200:
            continue

        info = info_resp.json()

        # Extract ingredients list and title
        title = r['title'].lower()
        ingredients_list = [i['name'].lower() for i in info.get('extendedIngredients', [])]

        # Filter recipes based on diet manually
        if diet == "vegetarian" and any(word in title or any(word in ing for ing in ingredients_list) for word in meat_words):
            continue
        if diet == "vegan" and any(word in title or any(word in ing for ing in ingredients_list) for word in meat_words + dairy_egg_words):
            continue

        # Extract calories
        nutrition = info.get('nutrition', {}).get('nutrients', [])
        kcal = next((n for n in nutrition if n['name'] == 'Calories'), None)
        kcal_str = f"{kcal['amount']} {kcal['unit']}" if kcal else 'Information saknas'

        # Determine difficulty based on time
        time = info.get('readyInMinutes', 0)
        difficulty = 'Lätt' if time < 30 else 'Medel' if time < 60 else 'Svår'

        # Fetch step-by-step instructions
        steps = info.get('analyzedInstructions', [])
        if steps and steps[0].get('steps'):
            instructions = "<ol>" + "".join(f"<li>{step['step']}</li>" for step in steps[0]['steps']) + "</ol>"
        else:
            instructions = info.get('instructions', 'Instruktioner saknas.')

        # Add recipe to final list
        recipes.append({
            'id': r['id'],
            'title': r['title'],
            'image': r['image'],
            'readyInMinutes': time,
            'servings': info.get('servings', 'Okänt'),
            'nutrition': kcal_str,
            'difficulty': difficulty,
            'instructions': instructions
        })

    # No results message
    no_results = len(recipes) == 0
    no_results_message = ""
    if no_results:
        if ingredients and diet:
            no_results_message = f"Inga recept hittades som både innehåller '{ingredients}' och är '{diet}'."
        elif ingredients:
            no_results_message = f"Inga recept hittades med ingrediensen '{ingredients}'."
        elif diet:
            no_results_message = f"Inga recept hittades för dieten '{diet}'."
        else:
            no_results_message = "Inga recept hittades."

    # Check login status
    user_id = request.get_cookie('user_id', secret=SECRET_KEY)
    username = None
    if user_id:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                if row:
                    username = row['username']

    # Render index template
    return template(
        'index',
        recipes=recipes,
        login_success=False,
        logout_success=False,
        login_error=None,
        username=username,
        no_results=no_results,
        no_results_message=no_results_message,
        email=None
    )



@route('/register', method=['GET', 'POST'])
def register():
    """
    Register a new user or show registration form.

    GET:  render the registration form.
    POST: process form data, validate input, hash password,
          insert new user into database.

    :return: rendered register template with status message
    """
    error = None
    success = None

    if request.method == 'POST':
        username = request.forms.get('username', '').strip()
        email = request.forms.get('email', '').strip().lower()
        password = request.forms.get('password', '')

        if not email or '@' not in email:
            error = 'Invalid email address.'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters.'
        else:
            pw_hash = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO users (username, email, password_hash)
                            VALUES (%s, %s, %s)
                            """,
                            (username, email, pw_hash)
                        )
                        conn.commit()
                        success = 'Registration successful! You can now log in.'
            except errors.UniqueViolation as e:
                constraint = e.diag.constraint_name or ''
                if 'email' in constraint:
                    error = 'Email is already registered.'
                else:
                    error = 'Username is already taken.'
            except Exception as exc:
                error = f'An unexpected error occurred: {exc}'

    return template('register', error=error, success=success)


@route('/login', method='POST')
def login():
    """
    Authenticate user with email and password.

    Sets cookie and redirects to home with login confirmation.

    :return: redirect or rendered template on failure
    """
    email = request.forms.get('email', '').strip().lower()
    password_raw = request.forms.get('password', '').encode('utf-8')

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, password_hash FROM users WHERE email = %s",
                (email,)
            )
            user = cur.fetchone()

    valid = bool(user and bcrypt.checkpw(
        password_raw, user['password_hash'].encode('utf-8')
    ))

    if valid:
        response.set_cookie('user_id', str(user['id']), secret=SECRET_KEY, path='/')
        return redirect('/?login=1')

    # Login failed – return template with required variables
    return template(
        'index',
        recipes=[],
        login_error='Invalid email or password.',
        login_success=False,
        logout_success=False,
        username=None,
        email=email,  # skickas med till HTML
        no_results=False
    )



@route('/logout')
def logout():
    """
    Log out current user by deleting their session cookie.

    :return: redirect to home with logout confirmation
    """
    response.delete_cookie('user_id', path='/')
    return redirect('/?logout=1')


@route('/favorite', method='POST')
def add_favorite():
    """
    Add a recipe to the user's favorites.

    Expects recipe_id, title, and image in form data.
    Returns JSON {'ok': True/False} or HTTP error.
    """
    user_id = request.get_cookie('user_id', secret=SECRET_KEY)
    if not user_id:
        return HTTPResponse(
            status=401, body=json.dumps({'ok': False, 'error': 'Not logged in'})
        )

    #Hämta all data från formuläret
    recipe_id = request.forms.get('recipe_id')
    title = request.forms.get('title')
    image = request.forms.get('image')
    difficulty = request.forms.get('difficulty')
    ready_in_minutes = request.forms.get('ready_in_minutes')
    servings = request.forms.get('servings')
    nutrition = request.forms.get('nutrition')
    instructions = request.forms.get('instructions')

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO favorites (
                        user_id, recipe_id, title, image, difficulty,
                        ready_in_minutes, servings, nutrition, instructions
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        user_id, recipe_id, title, image, difficulty,
                        ready_in_minutes, servings, nutrition, instructions
                    )
                )

                if cur.rowcount == 0:
                    return {'ok': False}

                conn.commit()
                return {'ok': True}
    except Exception as exc:
        return HTTPResponse(
            status=500, body=json.dumps({'ok': False, 'error': str(exc)})
        )


@route('/favorites')
def show_favorites():
    """
    Display all recipes favorited by the current user.

    Redirects to home if not logged in.
    """
    user_id = request.get_cookie('user_id', secret=SECRET_KEY)
    if not user_id:
        return redirect('/')

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
    """
    SELECT
        recipe_id,
        title,
        image,
        difficulty,
        ready_in_minutes,
        servings,
        nutrition,
        instructions
    FROM favorites
    WHERE user_id = %s
    """,
    (user_id,)
)
            favorites = cur.fetchall()

    return template('favorites', favorites=favorites)


@route('/remove-favorite', method='POST')
def remove_favorite():
    """
    Remove a recipe from the user's favorites.

    Expects recipe_id in form data. Redirects back to favorites list.
    """
    user_id = request.get_cookie('user_id', secret=SECRET_KEY)
    recipe_id = request.forms.get('recipe_id')

    if not user_id or not recipe_id:
        return redirect('/favorites')

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM favorites WHERE user_id = %s AND recipe_id = %s",
                    (user_id, recipe_id)
                )
                conn.commit()
    except Exception as exc:
        print(f"Error removing favorite: {exc}")

    return redirect('/favorites')


@route('/static/<filepath:path>')
def serve_static(filepath):
    """
    Serve static assets from the ./static directory.

    :param filepath: path of the requested static file
    :return: File response
    """
    return static_file(filepath, root='./static')


if __name__ == '__main__':
    # Start development server on localhost:8080
    run(host='localhost', port=8080, debug=True)
