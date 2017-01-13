__author__ = 'Koji'



class xapi_filter(object):
	COUNT_TYPE_VERB = 'verb'
	COUNT_TYPE_PLATFORM = 'platform'

	since = None
	until = None
	platform = None
	course = None
	counttype = None
	statement_id = None

	def __init__(self):
		pass

	def to_dict(self):
		filters = {}
		# When statement ID is specified, anything else will not be used.
		if self.statement_id:
			filters['statementId'] = self.statement_id

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