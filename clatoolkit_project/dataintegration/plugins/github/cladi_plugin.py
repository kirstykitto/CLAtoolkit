from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin
from dataintegration.core.socialmediarecipebuilder import *
from dataintegration.core.recipepermissions import *
import json
import dateutil.parser
from github import Github
# from dataintegration.plugins.github.githubLib import *
from django.contrib.auth.models import User
import os
from common.CLRecipe import CLRecipe
from common.ClaUserUtil import ClaUserUtil

class GithubPlugin(DIBasePlugin, DIPluginDashboardMixin):

    platform = CLRecipe.PLATFORM_GITHUB
    platform_url = "https://github.com/"

    # xapi_verbs = ['created', 'added', 'removed', 'updated', 'commented']
    # xapi_objects = ['Collection', 'file', 'comment']
    xapi_verbs = [CLRecipe.VERB_CREATED, CLRecipe.VERB_ADDED, CLRecipe.VERB_REMOVED, 
                CLRecipe.VERB_UPDATED, CLRecipe.VERB_COMMENTED, CLRecipe.VERB_CLOSED, CLRecipe.VERB_OPENED]
    xapi_objects = [CLRecipe.OBJECT_COLLECTION, CLRecipe.OBJECT_FILE, CLRecipe.OBJECT_NOTE]

    user_api_association_name = 'GitHub Username' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Repository URL' # eg hashtags or a group name

    # config_json_keys = ['token']
    # The number of data (records) in a page.
    parPage = 100

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = ['Collection', 'file', 'comment']
    xapi_verbs_to_includein_verbactivitywidget = ['created', 'added', 'removed', 'updated', 'commented']

    ### Activity type
    GITHUB_ACTIVITY_TYPE_COMMIT = 'Commit'

    ### Event types
    EVENT_TYPE_ISSUES = 'IssuesEvent'
    EVENT_TYPE_PR = 'PullRequestEvent'
    EVENT_TYPE_COMMIT_COMMENT = 'CommitCommentEvent'
    EVENT_TYPE_ISSUE_COMMENT = 'IssueCommentEvent'

    ### Issue event types
    # When someone was assigned to an issue
    ISSUE_EVENT_ASSIGNED = 'assigned'

    ### Issue status type
    ISSUE_STATUS_OPENED = 'opened'
    ISSUE_STATUS_REOPENED = 'reopened'
    ISSUE_STATUS_CLOSED = 'closed'

    ### File status
    FILE_STATUS_ADDED = 'added'
    FILE_STATUS_MODIFIED = 'modified'
    FILE_STATUS_REMOVED = 'removed'


    VERB_OBJECT_MAPPER = {}

    def __init__(self):
        pass


    def perform_import(self, retrieval_param, course_code):
        for details in retrieval_param:
            repo_name = details['repo_name']
            repo_url = self.platform_url + repo_name
            token = details['token']
            print "GitHub data import target repository: " + repo_url
            
            gh = Github(login_or_token = token, per_page = self.parPage)
            repo = gh.get_repo(repo_name)
            self.import_activities(course_code, repo_url, repo_name, repo)
            self.import_commits_from_all_branches(course_code, repo_url, repo_name, repo)

    def import_activities(self, course_code, repo_url, repo_name, repo):
        count = 0
        event_list = repo.get_events().get_page(count)
        issue_number_list = []
        while True:
            for event in event_list:
                # print 'Evet type === ' + event.type
                if event.type == self.EVENT_TYPE_ISSUES:
                    issue_number = self.import_issues(event, course_code, repo_url, repo_name)
                    issue_number_list.append(issue_number)
                elif event.type == self.EVENT_TYPE_PR:
                    self.import_pull_requests(event, course_code, repo_url, repo_name)
                elif event.type == self.EVENT_TYPE_COMMIT_COMMENT:
                    self.import_commit_comments(event, course_code, repo_url, repo_name, repo)
                elif event.type == self.EVENT_TYPE_ISSUE_COMMENT:
                    self.import_issue_comments(event, course_code, repo_url, repo_name)

            count = count + 1
            event_list = repo.get_events().get_page(count)
            temp = list(event_list)

            #If length is 0, it means that no commit data is left.
            if len(temp) == 0:
                #Break from while loop
                break;

        # End of while True:
        # Import assignees and assigners
        self.import_issue_activities(event, course_code, issue_number_list, repo_url, repo_name, repo)


    def import_issue_activities(self, event, course_code, issue_number_list, repo_url, repo_name, repo):
        for issue_number in issue_number_list:
            count = 0
            issue = repo.get_issue(issue_number)
            issue_events = issue.get_events().get_page(count)

            while True:
                for event in issue_events:
                    # Import assignees and assigner
                    if event.event == self.ISSUE_EVENT_ASSIGNED:
                        # Import assigner and assignees
                        self.import_assingee_assigner(event, course_code, issue, repo_url, repo_name)

                count = count + 1
                issue_events = issue.get_events().get_page(count)
                temp = list(issue_events)
                if len(temp) == 0:
                    #Break from while
                    break;


    ### Import assignees and assigner
    def import_assingee_assigner(self, event, course_code, issue, repo_url, repo_name):
        assignee = event.issue.assignee
        assigner = event.actor
        issue_url = issue.html_url
        issue_title = issue.title

        event_id = event.id
        assigner_id = str(assigner.id)
        assigner_name = str(assigner.login)
        assigner_url = assigner.html_url

        assignee_name = assignee.login
        assignee_url = assignee.html_url
        date = event.created_at
        object_type = CLRecipe.OBJECT_PERSON

        other_context_list = []
        # Import event type
        other_context_list.append(get_other_contextActivity(
            issue_url, 'Verb', event.event, 
            CLRecipe.get_verb_iri(CLRecipe.VERB_ADDED)))
        # Issue url and title
        other_context_list.append(get_other_contextActivity(
            issue_url, 'Object', issue_title, 
            CLRecipe.get_verb_iri(CLRecipe.VERB_ADDED)))
        # Repository url and name
        other_context_list.append(get_other_contextActivity(
            repo_url, 'Object', repo_name, 
            CLRecipe.get_verb_iri(CLRecipe.VERB_ADDED)))

        if username_exists(assigner_id, course_code, self.platform.lower()):
            usr_dict = ClaUserUtil.get_user_details_by_smid(assigner_id, self.platform)
            insert_added_object(usr_dict, issue_url, event_id, assignee_name, assigner_id, assigner_name, date,
                                course_code, self.platform, assigner_url, object_type,
                                shared_displayname = issue_url, other_contexts = other_context_list)


    ###################################################################
    # Import GitHub commit comments data.
    #   A library PyGithub is used to interact with GitHub API.
    #   See @ http://pygithub.readthedocs.org/en/stable/index.html
    ###################################################################
    # def import_commit_comments(self, course_code, url, repo):
    def import_commit_comments(self, event, course_code, repo_url, repo_name, repo):
        com_comment = event.payload['comment']
        actor = com_comment['user']

        author_homepage = actor['html_url']
        author_id = str(actor['id'])
        author_name = str(actor['login'])
        com_comment_url = com_comment['html_url']
        date = com_comment['updated_at']
        body = com_comment['body']
        if body is None:
            body = ""

        commit = repo.get_commit(sha = com_comment['commit_id'])
        commit_url = commit.html_url
        commit_message = commit.commit.message
        if commit_message is None:
            commit_message = ""

        other_context_list = []
        # Import event type
        other_context_list.append(get_other_contextActivity(
            com_comment_url, 'Verb', event.type, 
            CLRecipe.get_verb_iri(CLRecipe.VERB_COMMENTED)))
        # Commit url and message (title)
        other_context_list.append(get_other_contextActivity(
            commit_url, 'Object', commit_message, 
            CLRecipe.get_verb_iri(CLRecipe.VERB_COMMENTED)))
        # Repository url and name
        other_context_list.append(get_other_contextActivity(
            repo_url, 'Object', repo_name, 
            CLRecipe.get_verb_iri(CLRecipe.VERB_COMMENTED)))
        
        if username_exists(author_id, course_code, self.platform.lower()):
            usr_dict = ClaUserUtil.get_user_details_by_smid(author_id, self.platform)
            # cla_userame = get_username_fromsmid(author_id, self.platform.lower())
            insert_comment(usr_dict, commit_url, com_comment_url, 
                body, author_id, author_name, date, course_code, self.platform, author_homepage,
                shared_username = commit_message, shared_displayname = commit_message, 
                other_contexts = other_context_list)


    def import_issue_comments(self, event, course_code, repo_url, repo_name):
        iss_comment = event.payload['comment']
        issue = event.payload['issue']
        actor = iss_comment['user']

        author_homepage = actor['html_url']
        author_id = str(actor['id'])
        author_name = str(actor['login'])
        issue_url = issue['html_url']
        iss_comment_url = iss_comment['html_url']
        date = iss_comment['updated_at']

        issue_title = issue['title']
        body = iss_comment['body']
        if issue_title is None:
            issue_title = ""
        if body is None:
            body = ""

        other_context_list = []
        # Import event type
        other_context_list.append(get_other_contextActivity(
            iss_comment_url, 'Verb', event.type, 
            CLRecipe.get_verb_iri(CLRecipe.VERB_COMMENTED)))
        # Issue url and title
        other_context_list.append(get_other_contextActivity(
            issue_url, 'Object', issue_title, 
            CLRecipe.get_verb_iri(CLRecipe.VERB_COMMENTED)))
        # Repository url and name
        other_context_list.append(get_other_contextActivity(
            repo_url, 'Object', repo_name, 
            CLRecipe.get_verb_iri(CLRecipe.VERB_COMMENTED)))
        
        if username_exists(author_id, course_code, self.platform.lower()):
            usr_dict = ClaUserUtil.get_user_details_by_smid(author_id, self.platform)
            # cla_userame = get_username_fromsmid(author_id, self.platform.lower())
            insert_comment(usr_dict, issue_url, iss_comment_url, 
                body, author_id, author_name, date, course_code, self.platform, author_homepage,
                shared_username = issue_title, shared_displayname = issue_title, 
                other_contexts = other_context_list)


    def import_issues(self, event, course_code, repo_url, repo_name):
        issue = event.payload['issue']
        actor = issue['user']

        author_id = str(actor['id'])
        author_name = str(actor['login'])
        author_homepage = actor['html_url']
        issue_url = issue['html_url']
        date = issue['updated_at']
        title = issue['title']
        body = issue['body']
        if title is None:
            title = ''
        if body is None:
            body = ''

        # verb is opened when action is opened and reopened
        verb = CLRecipe.VERB_OPENED
        action = event.payload['action']
        if action == self.ISSUE_STATUS_CLOSED:
            verb = CLRecipe.VERB_CLOSED

        print 'action: %s ..... verb: %s' % (action, verb)

        other_context_list = []
        # Import event type
        other_context_list.append(get_other_contextActivity(
            issue_url, 'Verb', event.type, CLRecipe.get_verb_iri(verb)))
        # Repository url and name
        other_context_list.append(get_other_contextActivity(
            repo_url, 'Object', repo_name, CLRecipe.get_verb_iri(verb)))
        # Issue url and title 
        other_context_list.append(get_other_contextActivity(
            issue_url, 'Object', body, CLRecipe.get_verb_iri(verb)))

        if username_exists(author_id, course_code, self.platform.lower()):
            usr_dict = ClaUserUtil.get_user_details_by_smid(author_id, self.platform)
            # cla_userame = get_username_fromsmid(author_id, self.platform.lower())
            insert_issue(usr_dict, issue_url, verb, CLRecipe.OBJECT_NOTE, 
                CLRecipe.OBJECT_COLLECTION, title, author_name, author_id, date, 
                course_code, repo_url, self.platform, event.id, author_homepage,
                shared_displayname = repo_name, other_contexts = other_context_list)

        # Return the issue number for assignees & assigner data import
        return issue['number']


    def import_pull_requests(self, event, course_code, repo_url, repo_name):
        pull_req = event.payload['pull_request']
        actor = pull_req['user']

        author_homepage = actor['html_url']
        author_id = str(actor['id'])
        author_name = str(actor['login'])
        pr_url = pull_req['html_url']
        date = pull_req['updated_at']
        state = pull_req['state']

        # Should title and body concatenated?
        title = pull_req['title']
        if title is None:
            title = ''
        body = pull_req['body']
        if body is None:
            body = ""

        # Repository information 
        head_repo = pull_req['head']['repo']
        head_repo_name = head_repo['full_name']
        head_repo_url = head_repo['html_url']
        # base_repo = pull_req['base']['repo']
        # base_repo_name = base_repo['full_name']
        # base_repo_url = base_repo['html_url']

        # verb is opened when action is opened and reopened
        verb = CLRecipe.VERB_OPENED
        action = event.payload['action']
        if action == self.ISSUE_STATUS_CLOSED:
            verb = CLRecipe.VERB_CLOSED

        other_context_list = []
        # Import event type
        other_context_list.append(get_other_contextActivity(
            pr_url, 'Verb', event.type, CLRecipe.get_verb_iri(verb)))
        # Repository url and name
        other_context_list.append(get_other_contextActivity(
            repo_url, 'Object', repo_name, CLRecipe.get_verb_iri(verb)))
        # Import head repository
        other_context_list.append(get_other_contextActivity(
            head_repo_url, 'Object', head_repo_name, CLRecipe.get_verb_iri(verb)))
        # Import the pull rquest message body
        # Title is required when user create issue, but body (message) is optional, and thus it is imported as additional data
        other_context_list.append(get_other_contextActivity(
            pr_url, 'Object', body, CLRecipe.get_verb_iri(verb)))
        
        if username_exists(author_id, course_code, self.platform.lower()):
            usr_dict = ClaUserUtil.get_user_details_by_smid(author_id, self.platform)
            ###
            ### TODO: Select (or create) appropriate object type (review isn't quite appropriate to represent PR)
            ### 
            insert_issue(usr_dict, pr_url, verb, CLRecipe.OBJECT_REVIEW, 
                CLRecipe.OBJECT_COLLECTION, title, author_name, author_id, date, 
                course_code, repo_url, self.platform, event.id, author_homepage,
                shared_displayname = repo_name, other_contexts = other_context_list)


    ###################################################################
    # Import GitHub commit data.
    #   A library PyGithub is used to interact with GitHub API.
    #   See @ http://pygithub.readthedocs.org/en/stable/index.html
    ###################################################################
    def import_commits_from_all_branches(self, course_code, repo_url, repo_name, repo):
        print "Commit data import begins....."
        # Import data from all branches in the repository
        branches = repo.get_branches()
        for branch in branches:
            count = 0
            commit_list = repo.get_commits(sha = branch.name).get_page(count)

            # Retrieve commit data
            while True:
                for commit in commit_list:
                    # data regarding committed files are also imported in import_commits() method
                    self.import_commits(commit, course_code, repo_url, repo_name)

                # Pagination:
                # API response does not contain the number of pages left.
                # (It is included in HTTP header (link header).)
                # The content in next page needs to be retrieved
                # to know that there are still records to be imported.
                count = count + 1
                commit_list = repo.get_commits(sha = branch.name).get_page(count)
                temp = list(commit_list)
                #print "# of content in repo.get_commits().get_page(" + str(count) + ") = " + str(len(temp))
                #If length is 0, it means that no commit data is left.
                if len(temp) == 0:
                    #Break from while
                    break

        print "Commit data import done."

    def import_commits(self, commit, course_code, repo_url, repo_name):
        author_id = ''
        author_name = ''
        date = ''
        author_homepage = ''
        if commit.author is None or commit.author.id == '':
            # Note: What is the difference between author and committer?
            # 
            # The author is the person who originally wrote the work,
            # whereas the committer is the person who last applied the work. 
            # So, if you send in a patch to a project and one of the core members applies the patch, 
            # both of you get credit --- you as the author and the core member as the committer.
            print "commit.committer is null.url = " + commit.html_url
            #author = commit.author.name
            #email = commit.author.email
            author_id = commit.committer.id
            author_name = commit.committer.login
            author_homepage = commit.committer.html_url
            date = commit.commit.committer.date
        else:
            author_id = commit.author.id
            author_name = commit.author.login
            author_homepage = commit.author.html_url
            date = commit.commit.author.date

        # ID is all numbers, and thus needs to be converted to string
        author_id = str(author_id)
        # Rare case but committer name does not exist in some cases 
        if not username_exists(author_id, course_code, self.platform.lower()):
            # commit.commit.author does not have the element "login" or "id"
            author_id = commit.commit.author.name
            author_name = commit.commit.author.name
            date = commit.commit.author.date

        # ID is all numbers, and thus needs to be converted to string
        author_id = str(author_id)
        author_name = str(author_name)
        commit_title = commit.commit.message
        commit_url = commit.html_url
        # commit_sha = commit.sha

        # create other context activity value
        print 'Commit changes :%d, adds: %d, dels: %d' % (commit.stats.total, commit.stats.additions, commit.stats.deletions)
        total_list = []
        total_list.append(str(commit.stats.total))
        total_list.append(str(commit.stats.additions))
        total_list.append(str(commit.stats.deletions))
        filename_list = []
        additions_list = []
        deletions_list = []
        for file in commit.files:
            filename_list.append(file.filename)
            additions_list.append(str(file.additions))
            deletions_list.append(str(file.deletions))

        other_context_list = []
        # Import event type
        other_context_list.append(get_other_contextActivity(
            commit_url, 'Verb', self.GITHUB_ACTIVITY_TYPE_COMMIT, 
            CLRecipe.get_verb_iri(CLRecipe.VERB_CREATED)))
        # Repository url and name
        other_context_list.append(get_other_contextActivity(
            repo_url, 'Object', repo_name,
            CLRecipe.get_verb_iri(CLRecipe.VERB_CREATED)))
        # Commttied file names
        other_context_list.append(get_other_contextActivity(
            commit_url, 'Object', ','.join(filename_list),
            CLRecipe.get_verb_iri(CLRecipe.VERB_CREATED)))
        # Total number of changes, additions and deletions
        other_context_list.append(get_other_contextActivity(
            commit_url, 'Object', ','.join(total_list),
            CLRecipe.get_verb_iri(CLRecipe.VERB_CREATED)))
        # Additions of each file
        other_context_list.append(get_other_contextActivity(
            commit_url, 'Object', ','.join(additions_list),
            CLRecipe.get_verb_iri(CLRecipe.VERB_CREATED)))
        # Deletions of each file
        other_context_list.append(get_other_contextActivity(
            commit_url, 'Object', ','.join(deletions_list),
            CLRecipe.get_verb_iri(CLRecipe.VERB_CREATED)))

        # TODO: Add shared_username and shared_displayname? 
        if not username_exists(author_id, course_code, self.platform.lower()):
            return

        usr_dict = ClaUserUtil.get_user_details_by_smid(author_id, self.platform)
        # cla_userame = get_username_fromsmid(author_id, self.platform.lower())
        insert_commit(usr_dict, commit_url, commit_title, author_id, author_name,
            date, course_code, repo_url, self.platform, commit_url, author_id, author_homepage,
            other_contexts = other_context_list)

        author_details = {'author_id': author_id, 'author_name': author_name, 'author_homepage': author_homepage}
        commit_details = {'title': commit_title, 'url': commit_url}
        # All committed files are inserted into DB
        for file in commit.files:
            self.import_files(file, course_code, repo_url, repo_name, author_details, commit_details, date)



    def import_files(self, file, course_code, repo_url, repo_name, author_details, commit_details, commit_date):
        author_id = author_details['author_id']
        author_name = author_details['author_name']
        author_homepage = author_details['author_homepage']
        commit_title = commit_details['title']
        commit_url = commit_details['url']
        file_url = file.blob_url

        verb = CLRecipe.VERB_ADDED
        if file.status == self.FILE_STATUS_MODIFIED:
            verb = CLRecipe.VERB_UPDATED
        elif file.status == self.FILE_STATUS_REMOVED:
            verb = CLRecipe.VERB_REMOVED

        # Diffs between the current code and previous code
        patch = file.patch
        if file.patch is None:
            patch = ""

        other_context_list = []
        # Import file status
        other_context_list.append(get_other_contextActivity(
            file_url, 'Verb', file.status, CLRecipe.get_verb_iri(verb)))
        # Commit url and title
        other_context_list.append(get_other_contextActivity(
            commit_url, 'Object', commit_title, CLRecipe.get_verb_iri(verb)))
        # Repository url and name
        other_context_list.append(get_other_contextActivity(
            repo_url, 'Object', repo_name, CLRecipe.get_verb_iri(verb)))
        # File name
        other_context_list.append(get_other_contextActivity(
            file_url, 'Object', file.filename, CLRecipe.get_verb_iri(verb)))
        # Total number of lines changed 
        other_context_list.append(get_other_contextActivity(
            file_url, 'Object', str(file.changes), CLRecipe.get_verb_iri(verb)))
        # Additions
        other_context_list.append(get_other_contextActivity(
            file_url, 'Object', str(file.additions), CLRecipe.get_verb_iri(verb)))
        # Deletions
        other_context_list.append(get_other_contextActivity(
            file_url, 'Object', str(file.deletions), CLRecipe.get_verb_iri(verb)))

        if username_exists(author_id, course_code, self.platform.lower()):
            usr_dict = ClaUserUtil.get_user_details_by_smid(author_id, self.platform)
            # cla_userame = get_username_fromsmid(author_id, self.platform.lower())
            insert_file(usr_dict, file_url, patch, author_id, author_name,
                commit_date, course_code, commit_url, self.platform, file_url, 
                commit_url, verb, repo_url, author_id, author_homepage,
                other_contexts = other_context_list)


    def get_verbs(self):
        return self.xapi_verbs
            
    def get_objects(self):
        return self.xapi_objects

    def get_other_contextActivity_types(self, verbs = []):
        return sorted(verbs)

    def get_display_names(self, mapper):
        return mapper

    def get_results_from_rows(self, result):
        all_rows = []
        for row in result:
            verb, val = self.parse_contextActivities_json(row[1])
            if val is None:
                val = row[3]
            single_row = [row[0], verb, row[2], val]
            all_rows.append(single_row)

        return all_rows
        
    def parse_contextActivities_json(self, json):
        verb = CLRecipe.get_verb_by_iri(json['definition']['type'])
        val = json['definition']['name']['en-US']
        if verb == CLRecipe.VERB_COMMENTED:
            val = None
        
        return verb, val



registry.register(GithubPlugin)