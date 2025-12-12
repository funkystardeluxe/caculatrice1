from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

def preprocess_expression(expr: str) -> str:
    """
    Remplace les symboles usuels par des tokens Python/math acceptés par eval.
    - × -> *
    - ÷ -> /
    - ^ -> **
    - √ -> √
    - virgule -> point
    - supprime espaces inutiles
    """
    if not isinstance(expr, str):
        return ""

    # remplacements simples
    expr = expr.replace('×', '*')
    expr = expr.replace('÷', '/')
    expr = expr.replace('^', '**')
    expr = expr.replace('√', 'sqrt')
    expr = expr.replace(',', '.')   # si user utilise virgule
    expr = expr.replace('–', '-')   # tiret long
    expr = expr.replace('×', '*')
    expr = expr.strip()

    return expr

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcul', methods=['POST'])
def calcul():
    data = request.get_json() or {}
    expression = data.get('expression', '')
    expression = preprocess_expression(expression)

    try:
        # Fonctions autorisées (on construit explicitement la table)
        allowed_names = {}

        # importer fonctions math (exclure privées)
        for key in dir(math):
            if not key.startswith("__"):
                allowed_names[key] = getattr(math, key)

        # redéfinir sin/cos/tan pour prendre des arguments en DEGRÉS
        allowed_names['sin'] = lambda x: math.sin(math.radians(x))
        allowed_names['cos'] = lambda x: math.cos(math.radians(x))
        allowed_names['tan'] = lambda x: math.tan(math.radians(x))
        # alias utiles
        allowed_names['sqrt'] = math.sqrt
        allowed_names['pow'] = pow
        allowed_names['abs'] = abs
        allowed_names['round'] = round

        # Evaluation sécurisée (pas de builtins)
        result = eval(expression, {"__builtins__": {}}, allowed_names)

        # Formater résultat : afficher entier si c'est entier
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                # limiter à 10 décimales maxi pour lisibilité
                result = round(result, 10)
        return jsonify({'resultat': str(result)})
    except Exception as e:
        # renvoyer message d'erreur lisible
        return jsonify({'resultat': f"Opération invalide : {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
