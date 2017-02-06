__author__ = 'Koji'
import pytz

from common.util import Utility
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from clatoolkit.models import UnitOffering, UnitOfferingMembership
from xapi.oauth_consumer.operative import LRS_Auth
from xapi.statement.xapi_settings import xapi_settings


class xapi_getter(object):
	
	def __init__(self):
		pass

	def get_xapi_statements(self, course_id, user_id = None, xapi_filters = None, more_path = None):
		unit = UnitOffering.objects.get(id = course_id)
		lrs_client = LRS_Auth(provider_id = unit.get_lrs_id())

		user_list = []
		if user_id is None:
			# When user is admin or staff 
			memberships = UnitOfferingMembership.objects.filter(unit = unit)
			for ms in memberships:
				# Save all users' IDs in the unit
				user_list.append(ms.user.id)
		else:
			user_list.append(user_id)

		statement_list = []
		for uid in user_list:
			# Access to LRS to retrieve xAPI statements
			stmts = lrs_client.get_statement(uid, filters = xapi_filters.to_dict(), more_path = more_path)
			# print stmts
			if stmts is None:
				continue

			if 'statements' in stmts:
				statement_list += stmts['statements']
				# for stmt in stmts['statements']:
				# 	statement_list.append(stmt)
			else:
				statement_list.append(stmts)

			# print 'user %s - num of stmts = %s' % (uid, str(len(stmts['statements'])))
			
			# When there are more statements 
			if 'more' in stmts and stmts['more'] != '':
				# print 'Getting more xapi stmts for user id %s. more_path = %s' % (uid, stmts['more'])
				statement_list += self.get_xapi_statements(course_id, uid, xapi_filters, stmts['more'])

		# print statement_list
		return self.filter_result(statement_list, xapi_filters)


	def filter_result(self, statement_list, xapi_filters):
		# When statement ID is used as a filter, return as it is
		if xapi_filters.statement_id:
			return statement_list

		new_list = []
		for stmt in statement_list:

			if xapi_filters.platform and stmt['context']['platform'] != xapi_filters.platform:
				continue

			if xapi_filters.course:
				if stmt['context']['contextActivities']['grouping'][0]['definition']['name']['en-US'] != xapi_filters.course:
					continue

			if xapi_filters.since:
				timestamp = Utility.convert_to_datetime_object(stmt['timestamp'])
				if timestamp.tzinfo is None:
					# When timezone info is None, an error will occur (can't subtract offset-naive and offset-aware datetimes)
					# Add temporary timezone to avoid the error
					timestamp = Utility.convert_to_datetime_object(stmt['timestamp'] + '+00:00')
					
				# Create a valid ISO8601 timestamp (e.g. 2017-07-16T19:20:30+01:00), 
				# or LRS will reject other timestamp formats
				# Start time is set to 00:00:00 to retrieve all data on the start day
				since = Utility.convert_to_datetime_object(xapi_filters.since + 'T00:00:00+00:00')
				if timestamp < since:
					continue

			if xapi_filters.until:
				timestamp = Utility.convert_to_datetime_object(stmt['timestamp'])
				if timestamp.tzinfo is None:
					# When timezone info is None, an error will occur (can't subtract offset-naive and offset-aware datetimes)
					# Add temporary timezone to avoid the error
					timestamp = Utility.convert_to_datetime_object(stmt['timestamp'] + '+00:00')
				
				# Create a valid ISO8601 timestamp (e.g. 2017-07-16T19:20:30+01:00), 
				# or LRS will reject other timestamp formats
				# End time is set to 23:59:59 to retrieve all data on the end day
				until = Utility.convert_to_datetime_object(xapi_filters.until + 'T23:59:59+00:00')
				if timestamp > until:
					continue

			# If the statement matches all conditions, it's added to a new list
			new_list.append(stmt)

		return new_list
