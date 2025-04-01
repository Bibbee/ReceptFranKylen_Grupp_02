<!DOCTYPE html>
<html>
<head>
    <title>Recept Generator</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>

    <nav class="navbar">
        <ul>
            <li><a href="/">🏠 Hem</a></li>
            <li><a href="/saved">💾 Sparade recept</a></li>
            <li><a href="/shoppinglist">🛒 Inköpslista</a></li>
            <li><a href="/filter">🔍 Filtrera</a></li>
            <li><a href="/login">🔐 Logga in</a></li>
            <li><a href="javascript:history.back()">🔙 Tillbaka</a></li>
        </ul>
    </nav>

    <h1>Skriv in ingredienser</h1>
    <form action="/" method="post">
        <input type="text" name="ingredients" placeholder="t.ex. tomat, ost, pasta" required>
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