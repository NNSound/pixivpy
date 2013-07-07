# Pixiv API
# modify from tweepy (https://github.com/tweepy/tweepy/)

import re
import gzip
import urllib
import httplib

def convert_to_utf8_str(arg):
	# written by Michael Norton (http://docondev.blogspot.com/)
	if isinstance(arg, unicode):
		arg = arg.encode('utf-8')
	elif not isinstance(arg, str):
		arg = str(arg)
	return arg

def bind_api(**config):
	class APIMethod(object):
		path = config['path']
		method = config.get('method', 'GET')
		allowed_param = config.get('allowed_param', [])
		parser = config.get('parser', None)
		require_auth = config.get('require_auth', False)
		save_session = config.get('save_session', False)
		payload_list = config.get('payload_list', False)

		def __init__(self, api, args, kargs):
			if self.require_auth and not api.session:
				raise Exception('Authentication required!')

			self.api = api
			self.api_root = api.api_root
			self.headers = kargs.pop('headers', {
					'Referer': 'http://spapi.pixiv.net/',
					'User-Agent': 'pixiv-ios-app(ver4.0.0)',
				})
			self.post_data = kargs.pop('post_data', None)
			self.build_parameters(args)

			self.headers['Host'] = api.host

		def build_parameters(self, args):
			self.parameters = []
			if (self.require_auth):
				self.parameters.append(("PHPSESSID", self.api.session))
			for idx, arg in enumerate(args):
				if arg is None:
					continue

				try:
					self.parameters.append((self.allowed_param[idx], convert_to_utf8_str(arg)))
				except IndexError:
					raise Exception('Too many parameters supplied!')


		def execute(self):
			# Build the request URL
			url = self.api_root + self.path
			if len(self.parameters):
				url = '%s?%s' % (url, urllib.urlencode(self.parameters))

			conn = httplib.HTTPConnection(self.api.host, self.api.port, timeout=self.api.timeout)

			# Request compression if configured
			if self.api.compression:
				self.headers['Accept-encoding'] = 'gzip'

			# Execute request
			try:
				conn.request(self.method, url, headers=self.headers, body=self.post_data)
				resp = conn.getresponse()
			except Exception, e:
				raise Exception('Failed to send request: %s' % e)

			# handle login 302 and get PHPSESSID
			if resp.status in (301,302,) and (self.save_session):
				redirect_url = resp.getheader('location', '')
				self.api.session = redirect_url[redirect_url.rfind("PHPSESSID")+len("PHPSESSID")+1:]
				return self.api.session

			if resp.status != 200:
				raise Exception(resp.read())

			# Parse the response payload
			body = resp.read()
			if resp.getheader('Content-Encoding', '') == 'gzip':
				try:
					zipper = gzip.GzipFile(fileobj=StringIO(body))
					body = zipper.read()
				except Exception, e:
					raise Exception('Failed to decompress data: %s' % e)

			if (self.parser):
				if (self.payload_list):
					result = self.parser.parse_list(body)
				else:
					result = self.parser.parse(body)
			else:
				result = body		# parser not define, return raw string

			conn.close()

			return result


	def _call(api, *args, **kargs):
		method = APIMethod(api, args, kargs)
		return method.execute()

	return _call