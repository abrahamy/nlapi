from flask import Flask, Response
from nlservice import NlService


app = Flask(__name__)
service = NlService()


@app.route('/')
def index():
	return 'Hello'


@app.route('/boards')
def get_boards():
	global service

	res = service.get_boards()
	return Response(res, mimetype='application/json')


@app.route('/featured')
def get_featured_topics():
	global service

	res = service.get_featured()
	return Response(res, mimetype='application/json')


@app.route('/topics/<board_id>')
def get_topics(board_id):
	global service

	res = service.get_topics(board_id)
	return Response(res, mimetype='application/json')


@app.route('/posts/<int:topic_id>')
def get_posts(topic_id):
	global service

	res = service.get_posts(topic_id)
	return Response(res, mimetype='application/json')


if __name__ == '__main__':
	app.run()