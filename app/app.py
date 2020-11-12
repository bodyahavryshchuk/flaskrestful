import flask
from flask import Flask
import json
import requests
import sqlite3
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


@app.errorhandler(404)
def http_404_handler(error):
    return flask.jsonify(status=404)


@app.route('/takedata', methods=['GET'])
def takedata():
    """Function takes data and saves in database"""
    users = requests.get('https://randomuser.me/api/?results=100&gender=male').json()
    users = users['results']
    try:
        conn = sqlite3.connect('flaskrestful.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id VARCHAR(20) PRIMARY KEY, data JSON)")
        for user in users:
            cursor.execute("INSERT INTO users VALUES (?, ?)", [user['email'], json.dumps(user, ensure_ascii=False)])
        conn.commit()
    except sqlite3.Error as e:
        return flask.jsonify(status=500, errors=e.args[0])
    except Exception:
        flask.jsonify(errors='Something else failed')
    finally:
        conn.close()
    return flask.jsonify(users)


class UsersList(Resource):
    """Gets a list of users"""
    def get(self):
        try:
            conn = sqlite3.connect('flaskrestful.db')
            cursor = conn.cursor()
            response = cursor.execute("SELECT data FROM users").fetchall()
        except sqlite3.Error as e:
            return flask.jsonify(status=500, errors=e.args[0])
        except Exception:
            return flask.jsonify(errors='Something else failed')
        finally:
            conn.close()
        return response


class UserDetail(Resource):
    """Gets and deletes one specified user"""
    def get(self, email):
        try:
            conn = sqlite3.connect('flaskrestful.db')
            cursor = conn.cursor()
            response = cursor.execute("SELECT data FROM users WHERE id='%s'" % email).fetchall()
        except sqlite3.Error as e:
            return flask.jsonify(status=500, errors=e.args[0])
        except Exception:
            return flask.jsonify(errors='Something else failed')
        finally:
            conn.close()
        return response

    def delete(self, email):
        try:
            conn = sqlite3.connect('flaskrestful.db')
            cursor = conn.cursor()
            response = cursor.execute("DELETE FROM users WHERE id='%s'" % email).fetchall()
            conn.commit()
        except sqlite3.Error as e:
            return flask.jsonify(status=500, errors=e.args[0])
        except Exception:
            return flask.jsonify(errors='Something else failed')
        finally:
            conn.close()
        return response


api.add_resource(UsersList, '/users')
api.add_resource(UserDetail, '/user/<string:email>')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
