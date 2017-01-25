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
		return statement_list


	def get_verb_count(self, course_id, count_type, user_id = None, xapi_filters = None):
		obj_counts = self.get_object_counts(course_id, count_type, user_id, xapi_filters)

		obj = {}
		total_dict = obj_counts['total']
		for key, value in total_dict.iteritems():
			# Convert verb IRI into verb
			obj[xapi_settings.get_verb_by_iri(key)] = value

		obj_counts['total'] = obj
		return obj_counts


	def get_object_count_with_date(self, course_id, ts_count_type, user_id = None, xapi_filters = None):
		obj_counts = self.get_object_counts(course_id, ts_count_type, user_id, xapi_filters)

		date_dict = {}
		for user in obj_counts['users']:
			for count_type_obj in user['verb']:
				# When date exists in date_dict
				if count_type_obj['date'] in date_dict:
					# date_dict[date] has a dict: {'verb': <verb count>}
					# Check out if the verb already exists in date_dict[date]
					date = count_type_obj['date']
					if count_type_obj[ts_count_type] in date_dict[date]:
						# If it does, add up
						date_dict[date][count_type_obj[ts_count_type]] = \
							int(date_dict[date][count_type_obj[ts_count_type]]) + int(count_type_obj['count'])
					else:
						# If not, insert the value to date_dict[date][verb]
						date_dict[date][count_type_obj[ts_count_type]] = int(count_type_obj['count'])

				else:
					# When the date does not exist in date_dict
					date_dict[count_type_obj['date']] = {count_type_obj[ts_count_type]: int(count_type_obj['count'])}

		# sorted() method returns an array object
		return sorted(date_dict.items())



	def get_object_counts(self, course_id, count_type, user_id = None, xapi_filters = None):
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

		# Test code
		# count_list.append({'id': 43, 'username': 'clatoolkitdev2'})
		stmts = None
		for user in count_list:
			stmts = lrs_client.get_statement(user['id'], filters = xapi_filters.to_dict())
			user[count_type] = [] if stmts is None else stmts[count_type]

		new_obj = {}
		for c in count_list:
			objs = c[count_type]
			for obj in objs:
				if obj[count_type] in new_obj:
					new_obj[obj[count_type]] = int(new_obj[obj[count_type]]) + int(obj['count'])
				else:
					new_obj[obj[count_type]] = int(obj['count'])

		return_obj = {'total': new_obj, 'users': count_list}
		return return_obj

