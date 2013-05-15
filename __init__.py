import urllib
import socket
import base64
import json
import requests
import time
from datetime import datetime

class MP(object):
  RESERVED = {
		'first_name': '$first_name',
		'last_name': '$last_name',
		'email': '$email',
		'ignore_time': '$ignore_time',
		'created': '$created',
		'username': '$username',
		'user_id': '$distinct_id',
		'ip': '$ip'
	}
	def __init__(self, token, host='http://api.mixpanel.com', http_timeout=2, logging=False, api_key=None, api_secret=None):
		self._id = None
		self._token = token
		self._host = host
		self._http_timeout = http_timeout
		self._logging = logging
		self._apikey = api_key
		self._apisecret = api_secret

	def identify(self, id):
		self._id = id

	def track(self, event, props=None, time=None):
		self.check_id_token()

		if props is None:
			props = {}
		
		if time is not None:
			props['time'] = self.timestamp(time)
		
		props["token"] = self._token
		props["distinct_id"] = self._id
		props["ip"] = 0


		return self.request('track', {'event': event, 'properties': props})


	def alias(self, alias, original):
		self.check_id_token()
		if alias == original or alias == self._id:
			raise Exception, "Alias cannot be the same as the original"
	
		result = self.track('$create_alias', {'alias': alias, 'original': original})
		
		self.identify(alias)
		
		return result
	
	def track_import(self, event, props, time):
		self.check_id_token()
		self.check_api_key()
		
		return self.request('import', {'event': event, 'properties': props}, include_apikey=True)

	def engage(self, action, props, ignore_time=False):
		self.check_id_token()

		if ignore_time and isinstance(props, dict):
			props['$ignore_time'] = True

		params = {
			"$token": self._token,
			"$distinct_id": self._id,
		}

		if isinstance(props, dict):
			props = dict((self.RESERVED.get(k, k),(v.isoformat() if isinstance(v, datetime) else v)) for k, v in props.items())
		
		params.update({action: props})
		return self.request('engage', params)

	def set(self, *args, **kwargs):
		return self.engage('$set', *args, **kwargs)

	def set_once(self, *args, **kwargs):
		return self.engage('$set_once', *args, **kwargs)

	def add(self, prop, by=1, *args, **kwargs):
		if isinstance(prop, dict):
			props = dict((k,int(v)) for k,v in prop.items() if k not in self.RESERVED)
		else:
			props = {prop: by}
		return self.engage('$add', props, *args, **kwargs)

	def append(self, list_name, value=None, *args, **kwargs):
		if isinstance(list_name, dict):
			props = dict((k,int(v)) for k,v in list_name.items() if k not in self.RESERVED and v is not None)
		else:
			if value is None:
				raise Exception, "Vakue cannot be null" 
			props = {list_name: value}
		return self.engage('$append', props, *args, **kwargs)

	def track_charge(self, amount, properties=None, time=None, *args, **kwargs):
		try:
			amount = float(amount)
		except:
			raise Exception, "Amount must be a number"
		props = {'$amount': amount}
		if time is not None:
			props['$time'] = time.isoformat()
		props.update(properties)
		return self.append('$transactions', value=props, *args, **kwargs)

	def clear_charges(self, *args, **kwargs):
		return self.set('$transactions', value=[], *args, **kwargs)

	def delete_user(self, *args, **kwargs):
		return self.engage('$delete', self._id, *args, **kwargs)

	def log_file(self):
		return '/tmp/mixpanel_error.log'

	def reset(self):
		self._id = None
		self._token = None
		self._apikey = None
		self._apisecret = None

	def check_api_key(self):
		if self._apikey is None:
			raise Exception, "Need to initialize first with the apikey (MP.init <your_token>, api_key = <your_api_key>, api_secret = <your_api_secret>)"

	def check_identify(self):
		if self._id is None:
			raise Exception, "Need to identify first (MP.identify <user>)"

	def check_init(self):
		if self._token is None:
			raise Exception, "Need to initialize first (MP.init <your_token>)"

	def timestamp(dt=None):
		if dt is None:
			return time.time()
		else:
			return time.mktime(dt.timetuple()) 

	def now(self):
		return datetime.utcnow()

	def check_id_token(self):
		self.check_init()
		self.check_identify()

	def logm(self, msg):
		if not self._logging:
			return
		msg = self.now().strftime('<%c> ') + msg
		try:
			fh = open(self.log_file(), 'a')
			fh.write(msg)
			fh.close()
		except IOError:
			pass #just discard at this point

	def request(self, type, params, include_apikey=False):
		query = []
		
		try:
			url = self._host + '/%s/?data=%s' % (type, base64.b64encode(json.dumps(params)))
			if include_apikey:
				if self._apikey is not None:
					url += "&api_key=" + self._apikey
			r = requests.get(url, timeout=self._http_timeout)
		except Exception, e:
			print e
			self.logm("Could not transmit to " + self._host)

