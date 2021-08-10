import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.exceptions import NotFound, UnprocessableEntity

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_short_drinks():
    try:
        result = Drink.query.all()

        if len(result) == 0:
            abort(404)

        drinks = []
        for drink in result:
            drinks.append(drink.short())

        return jsonify({
            "success": True,
            "drinks": drinks
        })

    except NotFound:
        abort(404)

    except Exception:
        abort(500)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drink-details')
def get_long_drinks():
    try:
        result = Drink.query.all()

        if len(result) == 0:
            abort(404)

        drinks = []
        for drink in result:
            drinks.append(drink.long())

        return jsonify({
            "success": True,
            "drinks": drinks
        })

    except NotFound:
        abort(404)

    except Exception:
        abort(500)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        if (title is None or recipe is None):
            abort(422)

        drink = Drink(title=title, recipe=json.dumps([recipe]))
        drink.insert()
        return jsonify({
            "success": True,
            "drinks": list(drink.long())
        }), 200

    except UnprocessableEntity:
        abort(422)

    except Exception:
        abort(500)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id):
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        if (title is None and recipe is None):
            abort(422)

        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        if title:
            drink.title = title
        if recipe:
            drink.recipe = recipe
        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200

    except UnprocessableEntity:
        abort(422)

    except NotFound:
        abort(404)

    except Exception:
        abort(500)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        }), 200

    except NotFound:
        abort(404)

    except Exception:
        abort(500)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def autherror(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
