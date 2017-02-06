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

	@classmethod
	def format_date(self, date_str, splitter, connector, isMonthSubtract):
		ret = ''
		if date_str is None or date_str == '':
			return ret

		# If isMonthSubtract is True, then subtract 1 from month (to avoid calculation in JavaScript)
		# isMonthSubtract = True is recommended
		month_subtract = 1 if isMonthSubtract else 0
		dateAry = date_str.split(splitter)
		return dateAry[0] + connector + str(int(dateAry[1]) - month_subtract).zfill(2) + connector + dateAry[2]