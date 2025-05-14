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

# Retrieve API credentials from environment variables for secure access
API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')


def get_db_connection():
    """
    Create and return a new database connection.

    Uses environment variables for host, port, dbname, user, and password.
    The cursor_factory is set to RealDictCursor for dict-like fetches.

    Returns: psycopg2 connection object
    """
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor
    )


def get_user_id_from_cookie():
    """
    Retrieve the user ID from a signed cookie.

    Returns:
        str or None: User ID if present and valid, otherwise None.
    """
    return request.get_cookie('user_id', secret=SECRET_KEY)


def get_username_by_id(user_id):
    """
    Fetch the username associated with a given user ID from the database.

    Args:
        user_id (str): The user's ID.

    Returns:
        str or None: Username if found, otherwise None.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if row:
                return row['username']
    return None


@route('/')
def index():
    """
    Handle GET request to render the home page.

    Responsibilities:
    - Check for login/logout query parameters to control alert display.
    - Attempt to identify logged-in user via cookie and database lookup.
    - Render the index template with appropriate data.

    Query Parameters:
        login=1   -> display welcome message
        logout=1  -> display logout confirmation

    Returns:
        str: Rendered HTML content of the index page.
    """
    # No recipes are shown on initial GET request
    recipes = []

    # Detect whether to show login/logout alerts
    login_success = request.query.login == '1'
    logout_success = request.query.logout == '1'

    # Try to get user information from cookie and database
    user_id = get_user_id_from_cookie()
    username = get_username_by_id(user_id) if user_id else None

    # Render and return the index page with relevant context
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

def fetch_recipes_from_api(ingredients, diet):
    """Send request to Spoonacular API with ingredients and diet parameters."""
    url = 'https://api.spoonacular.com/recipes/complexSearch'
    params = {
        'apiKey': API_KEY,
        'number': 20,
        'addRecipeInformation': True,
        'fillIngredients': True
    }
    if ingredients:
        params['query'] = ingredients
    if diet:
        params['diet'] = diet

    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return []

    data = resp.json()
    return data.get('results', [])

def is_recipe_valid(info, diet):
    """Determine if a recipe matches the selected diet."""
    title = info.get('title', '').lower()
    ingredients = [i['name'].lower() for i in info.get('extendedIngredients', [])]

    meat = ['chicken', 'beef', 'pork', 'bacon', 'turkey', 'ham', 'lamb']
    dairy_egg = ['cheese', 'egg', 'milk', 'butter', 'yogurt', 'cream', 'honey']

    if diet == "vegetarian":
        return not any(w in title or any(w in ing for ing in ingredients) for w in meat)
    if diet == "vegan":
        return not any(w in title or any(w in ing for ing in ingredients) for w in meat + dairy_egg)
    return True

def get_detailed_recipe(recipe_id):
    """Fetch detailed recipe info including nutrition and steps."""
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {'apiKey': API_KEY, 'includeNutrition': True}

    resp = requests.get(url, params=params)
    return resp.json() if resp.status_code == 200 else None


def extract_recipe_data(summary, info):
    """Build the recipe dictionary used by the frontend."""
    nutrition = info.get('nutrition', {}).get('nutrients', [])
    kcal = next((n for n in nutrition if n['name'] == 'Calories'), None)
    kcal_str = f"{kcal['amount']} {kcal['unit']}" if kcal else 'Information missing'

    time = info.get('readyInMinutes', 0)
    difficulty = 'Easy' if time < 30 else 'Mid' if time < 60 else 'Hard'

    steps = info.get('analyzedInstructions', [])
    if steps and steps[0].get('steps'):
        instructions = "<ol>" + "".join(f"<li>{step['step']}</li>" for step in steps[0]['steps']) + "</ol>"
    else:
        instructions = info.get('instructions', 'No instructions provided.')

    return {
        'id': summary['id'],
        'title': summary['title'],
        'image': summary['image'],
        'readyInMinutes': time,
        'servings': info.get('servings', 'Unknown'),
        'nutrition': kcal_str,
        'difficulty': difficulty,
        'instructions': instructions
    }

@route('/', method='POST')
def get_recipes():
    """
    Handle recipe search POST request using ingredients and diet input.
    
    This function:
    - Retrieves form input from the user
    - Queries Spoonacular API for matching recipes
    - Applies manual filtering for vegetarian/vegan diets
    - Fetches and formats detailed recipe data
    - Displays results or an appropriate message if no recipes are found

    Returns:
        str: Rendered HTML of the index page
    """
    ingredients = request.forms.get('ingredients', '').strip()
    diet = request.forms.get('diet', '').strip().lower()

    raw_results = fetch_recipes_from_api(ingredients, diet)
    recipes = []

    for r in raw_results:
        info = get_detailed_recipe(r['id'])
        if not info:
            continue
        if not is_recipe_valid(info, diet):
            continue
        recipes.append(extract_recipe_data(r, info))

    no_results = len(recipes) == 0

    # Build user feedback message for no results
    if no_results:
        if ingredients and diet:
            msg = f"No recipes found containing '{ingredients}' and matching '{diet}' diet."
        elif ingredients:
            msg = f"No recipes found with ingredient '{ingredients}'."
        elif diet:
            msg = f"No recipes found for the '{diet}' diet."
        else:
            msg = "No recipes found."
    else:
        msg = ""

    # Check for logged-in user
    user_id = get_user_id_from_cookie()
    username = get_username_by_id(user_id) if user_id else None

    # Render index template
    return template(
        'index',
        recipes=recipes,
        login_success=False,
        logout_success=False,
        login_error=None,
        username=username,
        no_results=no_results,
        no_results_message=msg,
        email=None
    )

@route('/register', method=['GET', 'POST'])
def register():
    """
    Register a new user or show registration form.

    GET:  render the registration form.
    POST: process form data, validate input, hash password,
          insert new user into database.

    Returns: rendered register template with status message
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

    Returns: redirect or rendered template on failure
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
    Returns: JSON {'ok': True/False} or HTTP error.
    """
    user_id = request.get_cookie('user_id', secret=SECRET_KEY)
    if not user_id:
        return HTTPResponse(
            status=401, body=json.dumps({'ok': False, 'error': 'Not logged in'})
        )

    #Fetch all data from the form
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
