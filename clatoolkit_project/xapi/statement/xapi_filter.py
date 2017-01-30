__author__ = 'Koji'



class xapi_filter(object):
	COUNT_TYPE_VERB = 'verb'
	COUNT_TYPE_PLATFORM = 'platform'
	COUNT_TYPE_USER_ID = 'user_id'

	since = None
	until = None
	platform = None
	course = None
	counttype = None
	timeseries_counttype = None
	statement_id = None
	limit = None

	def __init__(self):
		pass

	def to_dict(self):
		filters = {}
		# When statement ID is specified, anything else will not be used.
		if self.statement_id:
			filters['statementId'] = self.statement_id

		if self.limit:
			filters['limit'] = self.limit

		# until and since are checking data stored date, not date of activity occurred, so these are useless...
		# if self.until:
		# 	# Create a valid ISO8601 timestamp (e.g. 2017-07-16T19:20:30+01:00), or LRS will reject other timestamp formats
		# 	# End time is set to 23:59:59 to retrieve all data on the end day
		# 	filters['until'] = self.until + 'T23:59:59+00:00'

		# if self.since:
		# 	# Create a valid ISO8601 timestamp (e.g. 2017-07-16T19:20:30+01:00), or LRS will reject other timestamp formats
		# 	# Start time is set to 00:00:00 to retrieve all data on the start day
		# 	filters['since'] = self.since + 'T00:00:00+00:00'
			
		# if self.platform:
		# 	filters['platform'] = self.platform
		# if self.course:
		# 	filters['course'] = self.course
		
		return filters