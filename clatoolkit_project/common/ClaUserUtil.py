__author__ = 'Koji Nishimoto'
__date__ = '30/09/2016'
from django.contrib.auth.models import User
from clatoolkit.models import UnitOffering, UserProfile


class ClaUserUtil(object):
    @classmethod
    def get_smids_by_uid(self, userid):
        if userid is None:
            return None

        user = User.objects.get(pk=userid)
        return self.get_smids(user)

    @classmethod
    def get_smids_by_username(self, username):
        if username is None:
            return None

        user = User.objects.get(username=username)
        return self.get_smids(user)

    @classmethod
    def get_smids(self, user_obj):
        ret = {}
        if user_obj is None:
            return None

        # TODO: Platform name should not be hard-coded...
        ret['twitter'] = user_obj.userprofile.twitter_id
        ret['fb'] = user_obj.userprofile.fb_id
        ret['forum'] = user_obj.userprofile.forum_id
        ret['google'] = user_obj.userprofile.google_account_name
        ret['github'] = user_obj.userprofile.github_account_name
        ret['trello'] = user_obj.userprofile.trello_account_name
        ret['diigo'] = user_obj.userprofile.diigo_username
        return ret

    @classmethod
    def get_alluser_smids_in_course(self, course_code):
        # Get all trello account from clatoolkit_userprofile table
        # Firstly, get (CLA toolkit) username that registered in the course.
        rows = UnitOffering.objects.get(code=course_code)
        ret = []
        for user in rows.users.all():
            obj = {}
            obj['id'] = user.id
            obj['username'] = user.username
            obj['smids'] = self.get_smids(user)
            ret.append(obj)

        return ret

    @classmethod
    def get_user_details_by_smid(self, smid, platform):
        platform_param_name = self.get_platform_column_name_filter_string(platform)
        try:
            kwargs = {platform_param_name: smid}
            users = UserProfile.objects.filter(**kwargs)
            user = users[0]
            if len(users) > 1:
                print """Warning: Multiple user data were retrieved
				in get_user_details_by_smid(). Params: smid = %s, platform = %s""" % (smid, platform)

        except UserProfile.DoesNotExist:
            print """Warning: UserProfile.DoesNotExist exception has occurred
					in get_user_details_by_smid(). Params: smid = %s, platform = %s""" % (smid, platform)
            return None

        details = {}
        if user is not None:
            details['id'] = user.user.id
            details['username'] = user.user.username
            details['first_name'] = user.user.first_name
            details['last_name'] = user.user.last_name
            details['email'] = user.user.email
            # details['is_staff'] = user.user.is_staff # Necessary?
            details['smids'] = self.get_smids_by_uid(user.user.id)

        return details

    @classmethod
    def get_platform_column_name_filter_string(self, platform):
        platform = platform.lower()

        # TODO: Platform name should not be hard-coded...
        if platform == 'youtube':
            platform_param_name = "google_account_name"
        elif platform == 'github':
            platform_param_name = "github_account_name"
        elif platform == 'facebook':
            platform_param_name = "fb_id"
        elif platform == 'trello':
            platform_param_name = "trello_account_name"
        elif platform == 'twitter':
            platform_param_name = "twitter_id"
        elif platform == 'forum':
            platform_param_name = "forum_id"
        elif platform == 'diigo':
            platform_param_name = "diigo_username"
        else:
            platform_param_name = "%s_id" % (platform.lower())

        return platform_param_name + "__iexact"
