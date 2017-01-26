from django.http import HttpResponse
from isodate.isodatetime import parse_datetime

class Utility(object):
	@classmethod
	def get_site_url(self, request):
		protocol = 'https' if request.is_secure() else 'http'
		url = '%s://%s' % (protocol, request.get_host())
		return url

	@classmethod
	def convert_to_datetime_object(self, timestr):
		try:
			date_object = parse_datetime(timestr)
		except ValueError as e:
			raise ParamError("An error has occurred. Time format does not match. %s -- Error: %s" % (timestr, e.message))

		return date_object