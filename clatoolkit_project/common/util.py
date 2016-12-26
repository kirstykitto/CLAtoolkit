from django.http import HttpResponse

class Utility(object):
	@classmethod
	def get_site_url(self, request):
	    protocol = 'https' if request.is_secure() else 'http'
	    url = '%s://%s' % (protocol, request.get_host())
	    return url
