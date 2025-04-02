<!DOCTYPE html>
<html>
<head>
    <title>Recept Generator</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <h1>Skriv in ingredienser</h1>
    <form action="/" method="post">
        <input type="text" name="ingredients" placeholder="t.ex. tomato, cheese, pasta" required>
        <button type="submit">Hitta recept</button>
    </form>

    % if recipes:
        <h2>Resultat:</h2>
        % for recipe in recipes:
            <div class="recipe">
                <img src="{{recipe['image']}}" width="100">
                <p><strong>{{recipe['title']}}</strong></p>
                <a href="https://spoonacular.com/recipes/{{recipe['title'].replace(' ', '-')}}-{{recipe['id']}}" target="_blank">Visa recept</a>
            </div>
        % end
    % end
</body>  
</html> 