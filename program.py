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

def fetch_recipes_from_api(ingredients, diet, max_calories=None, max_ready_time=None):
    """Send request to Spoonacular API with ingredients, diet and optional filters."""
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
    if max_calories:
        params['maxCalories'] = max_calories
    if max_ready_time:
        params['maxReadyTime'] = max_ready_time

    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return []
    return resp.json().get('results', [])


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

def parse_search_filters(forms):
    """
    Parse search-related filters from request forms.

    Returns a dict with keys:
      - ingredients (str)
      - diet (str)
      - max_calories (int or None)
      - max_time (int or None)
      - difficulty (str or None)
    """
    ingredients = forms.get('ingredients', '').strip()
    diet = forms.get('diet', '').strip().lower()

    max_calories_input = forms.get('max_calories', '').strip()
    max_time_input = forms.get('max_time', '').strip()
    difficulty_input = forms.get('difficulty', '').strip().capitalize()

    max_calories = int(max_calories_input) if max_calories_input.isdigit() else None
    max_time = int(max_time_input)     if max_time_input.isdigit()     else None
    difficulty = difficulty_input if difficulty_input in ('Easy', 'Mid', 'Hard') else None

    return {
        'ingredients': ingredients,
        'diet': diet,
        'max_calories': max_calories,
        'max_time': max_time,
        'difficulty': difficulty
    }


def should_include_recipe(info, diet, max_calories, max_time, difficulty):
    """
    Determine if a detailed recipe should be included based on all filters.
    """
    # Calorie and time extraction
    nutrition = info.get('nutrition', {}).get('nutrients', [])
    kcal_data = next((n for n in nutrition if n['name'] == 'Calories'), None)
    calories = kcal_data['amount'] if kcal_data else None
    ready_in = info.get('readyInMinutes', 0)

    # Difficulty classification
    current_difficulty = 'Easy' if ready_in < 30 else 'Mid' if ready_in < 60 else 'Hard'

    # Apply filters
    if max_calories is not None and calories is not None and calories > max_calories:
        return False
    if max_time is not None and ready_in > max_time:
        return False
    if difficulty is not None and current_difficulty != difficulty:
        return False
    if not is_recipe_valid(info, diet):
        return False

    return True


def build_no_results_message(filters):
    """
    Build a feedback message when no recipes match the given filters.
    """
    criteria = []
    if filters['ingredients']:
        criteria.append(f"ingredient '{filters['ingredients']}'")
    if filters['diet']:
        criteria.append(f"diet '{filters['diet']}'")
    if filters['max_calories'] is not None:
        criteria.append(f"max {filters['max_calories']} kcal")
    if filters['max_time'] is not None:
        criteria.append(f"max {filters['max_time']} min")
    if filters['difficulty'] is not None:
        criteria.append(f"difficulty '{filters['difficulty']}'")

    if criteria:
        return "No recipes found matching " + ", ".join(criteria) + "."
    return "No recipes found."


# --- Refactored route handler ---
@route('/', method='POST')
def get_recipes():
    """
    Handle recipe search with single-responsibility breakdown.
    """
    # 1) Parse filters
    filters = parse_search_filters(request.forms)

    # 2) Fetch raw list from API
    raw_results = fetch_recipes_from_api(
        filters['ingredients'],
        filters['diet'],
        filters['max_calories'],
        filters['max_time']
    )

    # 3) Filter and format results
    recipes = []
    for summary in raw_results:
        info = get_detailed_recipe(summary['id'])
        if not info:
            continue
        if should_include_recipe(
            info,
            filters['diet'],
            filters['max_calories'],
            filters['max_time'],
            filters['difficulty']
        ):
            recipes.append(extract_recipe_data(summary, info))

    # 4) Determine outcome message
    no_results = len(recipes) == 0
    no_results_message = build_no_results_message(filters) if no_results else ''

    # 5) Render template
    user_id = get_user_id_from_cookie()
    username = get_username_by_id(user_id) if user_id else None

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
