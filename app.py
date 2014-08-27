from flask import Flask, Response, request, abort
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
				'description': 'Get this api specification.'
			},
			{
				'uri': '/api/getFeaturedTopics',
				'methods': ['get'],
				'description': 'Get featured topics listed on nairaland.com\'s front page.'
			},
			{
				'uri': '/api/listForums',
				'methods': ['get'],
				'description': 'Get list of forums on nairaland.com.'
			},
			{
				'uri': '/api/getForum?forum-id=:id',
				'methods': ['get'],
				'description': 'Get topics for forum with the id :id.'
			},
			{
				'uri': '/api/getTopic?topic-id=:id',
				'methods': ['get'],
				'description': 'Get topic with all comments for the given topic id (:id)'
			}
		]
	}

	data = json.dumps(urls, indent=2, ensure_ascii=False)
	response = Response(data, mimetype='application/json')
	response.headers['Access-Control-Allow-Origin'] = '*'

	return response


@app.route('/api/<action>', methods=['GET'])
def request_handler(action):
	global service
	action = action.lower()

	if action == 'listforums':
		data = service.get_forums()
	elif action == 'getfeaturedtopics':
		data = service.get_featured_topics()
	elif action == 'getforum':
		forum_id = request.args.get('forum-id', None)
		if not forum_id:
			abort(400)
		data = service.get_forum(forum_id)
	elif action == 'gettopic':
		topic_id = request.args.get('topic-id', None)
		try:
			topic_id = int(topic_id)
		except (TypeError, ValueError) as e:
			abort(400)
		data = service.get_topic('%d' % topic_id)
	else:
		abort(404)

	response = Response(data, mimetype='application/json')
	response.headers['Access-Control-Allow-Origin'] = '*'

	return response


if __name__ == '__main__':
	import os
	port = os.environ.get('PORT', None)
	debug = True if port else False

	app.run(host='0.0.0.0', port=port, debug=debug)
