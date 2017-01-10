__author__ = 'Koji'

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from clatoolkit.models import UnitOffering, UnitOfferingMembership
from xapi.oauth_consumer.operative import LRS_Auth


class xapi_getter(object):
	filters = None

	# verb filter. Use verb IRI
	verb = None

	def __init__(self):
		filters = None


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
			user = User.objects.get(id = uid)
			# Get statement IDs from learningrecord table
			# records = LearningRecord.objects.filter(user = user, unit = unit)
			# for row in records:
			#     # params = {'statementId': [row.statement_id]}
			#     params = {'verb': 'http://www.w3.org/ns/activitystreams#Create'}
			#     # print params
			#     # Access to LRS to retrieve xAPI 
			#     stmts = lrs_client.get_statement(uid, filters = params)
			#     statement_list.append(stmts)

			# Access to LRS to retrieve xAPI 
			stmts = lrs_client.get_statement(uid, filters = xapi_filters.to_dict())
			# print stmts
			statement_list = stmts['statements']

		# print statement_list
		return statement_list


	def get_object_counts(self, course_id, count_type, user_id = None):
		unit = UnitOffering.objects.get(id = course_id)
		lrs_client = LRS_Auth(provider_id = unit.get_lrs_id())

		count_list = []
		if user_id is None:
			# When user is admin or staff 
			memberships = UnitOfferingMembership.objects.filter(unit = unit)
			for ms in memberships:
				# Save all users' IDs in the unit
				count_list.append({'id': ms.user.id, 'username': ms.user.username})
		else:
			user = User.objects.get(id = user_id)
			count_list.append({'id': user.id, 'username': user.username})

		stmts = None
		filters = {'counttype': count_type}
		# count_list = {}
		for user in count_list:
			stmts = lrs_client.get_statement(user['id'], filters = filters)
			user[count_type] = stmts[count_type]

		return count_list
