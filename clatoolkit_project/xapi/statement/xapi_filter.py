__author__ = 'Koji'



class xapi_filter(object):
	since = None
	until = None
	platform = None
	course = None

	def __init__(self):
		pass

	def to_dict(self):
		filters = {}
		if self.until:
			filters['until'] = self.until
		if self.since:
			filters['since'] = self.since
		if self.platform:
			filters['platform'] = self.platform
		print self.course
		if self.course:
			filters['course'] = self.course
		
		return filters