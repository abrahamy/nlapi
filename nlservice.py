from bs4 import BeautifulSoup
import json
import re
import requests
import time

def chunks(lst, n):
    """ Yield successive n-sized chunks from lst """
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

class NlService(object):
    """A class for crawling Nairaland forum"""

    BASE_URI = 'http://www.nairaland.com'
    SLEEP_SECONDS = 60 # i.e. 1 minute
    _last_requested_uri = None
    _last_request_time = 0
    _cached_result = None

    def __init__(self):
        super(NlService, self).__init__()

    def get_html(self, uri):
        uri = self.absolute_uri(uri)
        same_uri = self._last_requested_uri == uri
        too_many_requests = time.time() - self._last_request_time < self.SLEEP_SECONDS

        if too_many_requests and same_uri:
            return self._cached_result

        try:
            self._cached_result = requests.get(uri).text
            self._last_request_time = time.time()
            self._last_requested_uri = uri
        except Exception as e:
            return '<doctype html><html><head><title>(Empty)</title></head><body></body></html>'

        return self._cached_result

    def absolute_uri(self, uri):
        if uri.startswith('/'):
            return ''.join([self.BASE_URI, uri])

        if not uri.startswith(self.BASE_URI):
            return ''.join([self.BASE_URI, '/', uri])

        return uri

    def get_id_from_uri(self, uri):
        uri = uri.replace(self.BASE_URI, '')
        if uri.startswith('/'):
            uri = uri[1:]

        id_ = uri.split('/')[0]
        return id_ if re.compile('^\d+$').search(id_) else None

    def strip_leading_slash(self, uri):
        if uri.startswith('/'):
            return uri[1:]

        return uri

    def get_forums(self):
        soup = BeautifulSoup(self.get_html(self.BASE_URI))
        forums = []

        table = soup.find('table', class_='boards')
        if table:
            for row in table.find_all('td'):
                for index, tag in enumerate(row.find_all('a'), start=1):
                    uri = self.strip_leading_slash(tag['href'])
                    forum = dict(id=index, name=tag.text, title=tag['title'], uri=uri)
                    forums.append(forum)

        regex = re.compile('class=g')
        forums = [forum for forum in forums if not regex.search(forum['title'])]

        return json.dumps(forums, indent=2, ensure_ascii=False)

    def get_featured_topics(self):
        soup = BeautifulSoup(self.get_html(self.BASE_URI))
        topics = []

        container = soup.select('td.featured')[0]
        for link in container.find_all('a'):
            href = link['href']
            id_=self.get_id_from_uri(href)
            uri=self.absolute_uri(href)

            topics.append(dict(id=id_, title=link.text, uri=uri))

        topics = [topic for topic in topics if topic['id']]

        return json.dumps(topics, indent=2, ensure_ascii=False)

    def get_forum(self, uri):
        soup = BeautifulSoup(self.get_html(uri))
        forum = {
            'title': uri.capitalize(),
            'uri': uri,
            'topics': []
        }

        for row in soup.find_all('td', id=re.compile('top\d+')):
            try:
                link = row.find('a', href=re.compile('^/\d+/\w+'))
                data = self.parse_topic_data([b.text for b in row.find('span', class_='s').find_all('b')])

                author, posts, views, create_at, last_comment_by = data
                topic = dict(
                    id=self.get_id_from_uri(link['href']),
                    title=link.text, uri=self.absolute_uri(link['href']),
                    author=author, posts=posts, views=views, created_at=create_at,
                    last_comment_by=last_comment_by)

                forum['topics'].append(topic)
            except Exception as e:
                continue

        return json.dumps(forum, indent=2, ensure_ascii=False)

    def get_topic(self, uri):
        soup = BeautifulSoup(self.get_html(uri))
        topic = {
          'title': soup.title.text.split('-')[0].strip(),
          'comments': []
        }

        message_ids = filter(
          lambda item: item is not None,
          map(
            lambda tag: tag.get('name', None),
            soup.find_all('a', attrs={'name': re.compile('^msg\d+$')})
          )
        )
        message_ids = [i.replace('msg', '') for i in message_ids]

        for m_id in message_ids:
          header = soup.find('a', attrs={'name': 'msg%s' % m_id}).parent
          body_tag = soup.find(id='pb%s' % m_id)
          body = body_tag.find('div', class_='narrow').text

          likes_tag = body_tag.find(id='lpt%s' % m_id)
          likes = likes_tag.text.replace('Likes', '').replace('Like', '').strip() if likes_tag else '0'

          user_tag = header.find('a', class_='user')
          username = user_tag.text
          location = user_tag.get('title', 'n/a').replace('Location: ', '')
          gender = 'M' if header.find('span', class_='m') else 'F'
          created_at = header.find('span', class_='s').text

          comment = {
           'author': {
             'username': username,
             'gender': gender,
             'location': location
           },
           'body': body,
           'likes': likes,
           'created_at': created_at
          }

          topic['comments'].append(comment)

        return json.dumps(topic, indent=2, ensure_ascii=False, sort_keys=True)

    def parse_topic_data(self, lst):
        if len(lst)==5: return lst

        if len(lst)==6:
            author, posts, views, c_time, c_date, last_comment = lst
            return author, posts, views, '%s at %s' % (c_date, c_time), last_comment

        author, posts, views, c_time, c_date, c_year, last_comment = lst
        return author, posts, views, '%s, %s at %s' % (c_date, c_year, c_time), last_comment
