__author__ = 'Koji'

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from clatoolkit.models import UnitOffering, UnitOfferingMembership
from xapi.oauth_consumer.operative import LRS_Auth
from xapi.statement.xapi_settings import xapi_settings


class xapi_getter(object):
	
	def __init__(self):
		pass

	def get_xapi_statements(self, course_id, user_id = None, xapi_filters = None):
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
			stmts = lrs_client.get_statement(uid, filters = xapi_filters.to_dict())
			# print stmts
			if stmts is None:
				continue

			# 
			# TODO: get more data if "more" element exist in stmts dict.
			# 
			# print '-------------------------'
			# for key, value in stmts.iteritems():
			# 	print key
			# print stmts['more']
			if 'statements' in stmts:
				for stmt in stmts['statements']:
					statement_list.append(stmt)
			else:
				statement_list.append(stmts)

		# print statement_list
		return self.filter_result(statement_list, xapi_filters)


	def filter_result(self, statement_list, xapi_filters):
		# When statement ID is used as a filter, ignore any other filter properties
		if xapi_filters.statement_id:
			return

		# print '========== num of elem in statement_list: %s ' % str(len(statement_list))
		print xapi_filters.platform
		print xapi_filters.course
		# print 'filtering...........'

		new_list = []
		for stmt in statement_list:
			# print '---'
			# print stmt['context']['platform']
			# print stmt['context']['contextActivities']['grouping'][0]['definition']['name']['en-US']

			if xapi_filters.platform and stmt['context']['platform'] != xapi_filters.platform:
				# del statement_list[i]
				# print 'platform filter delete.'
				continue

			if xapi_filters.course:
				if stmt['context']['contextActivities']['grouping'][0]['definition']['name']['en-US'] != xapi_filters.course:
					# del statement_list[i]
					# print 'course filter delete.'
					continue

			new_list.append(stmt)

		# print '========== num of elem in statement_list after filtering: %s ' % str(len(new_list))
		return new_list