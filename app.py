from flask import Flask, Response
from nlservice import NlService
import json


app = Flask(__name__)
service = NlService()


@app.route('/', methods=['GET'])
def index():
	urls = {
		'urls': [
			{
				'uri': '/',
				'methods': ['get'],
				'description': 'Get list of all api resources.'
			},
			{
				'uri': '/featured',
				'methods': ['get'],
				'description': 'Get featured topics listed on nairaland.com\'s front page.'
			},
			{
				'uri': '/forums',
				'methods': ['get'],
				'description': 'Get list of forums on nairaland.com.'
			},
			{
				'uri': '/forums/:forum',
				'methods': ['get'],
				'description': 'Get topics for forum named :forum.'
			},
			{
				'uri': '/forums/:forum/:topic',
				'methods': ['get'],
				'description': 'Get all comments for the topic with id :topic and belonging to forum named :forum.'
			}
		]
	}

	data = json.dumps(urls, indent=2)

	return Response(data, mimetype='application/json')


@app.route('/forums', methods=['GET'])
def get_forums():
	global service

	res = service.get_forums()
	return Response(res, mimetype='application/json')


@app.route('/featured', methods=['GET'])
def get_featured_topics():
	global service

	res = service.get_featured_topics()
	return Response(res, mimetype='application/json')


@app.route('/forums/<forum>', methods=['GET'])
def get_forum_topics(forum):
	global service

	res = service.get_forum_topics(forum)
	return Response(res, mimetype='application/json')


@app.route('/forums/<forum>/<int:topic>', methods=['GET'])
def get_topic_comments(forum, topic):
	global service

	res = service.get_topic_comments('%d' % topic)
	return Response(res, mimetype='application/json')


if __name__ == '__main__':
	import os
	port = os.environ.get('PORT', 5000)
	debug = True if port == 5000 else False

	app.run(host='0.0.0.0', port=port, debug=debug)