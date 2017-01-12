__author__ = 'Koji'



class xapi_filter(object):
	COUNT_TYPE_VERB = 'verb'
	COUNT_TYPE_PLATFORM = 'platform'

	since = None
	until = None
	platform = None
	course = None
	counttype = None

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
		if self.course:
			filters['course'] = self.course
		if self.counttype:
			filters['counttype'] = self.counttype
		
		return filters