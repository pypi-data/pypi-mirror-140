from flask import Flask, jsonify, render_template, request
from qrunner.utils.mysql_util import ApiDB

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


@app.route('/api', methods=['GET', 'POST'])
def api():
    data = request.args
    path = data.get('path')
    data = ApiDB().get_by_path(path)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
