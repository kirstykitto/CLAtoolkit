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

class GithubPlugin(DIBasePlugin, DIPluginDashboardMixin):

    platform = "GitHub"
    platform_url = "https://github.com/"

    # xapi_verbs = ['created', 'added', 'removed', 'updated', 'commented']
    # xapi_objects = ['Collection', 'file', 'comment']
    xapi_verbs = [CLRecipe.VERB_CREATED, CLRecipe.VERB_ADDED, CLRecipe.VERB_REMOVED, 
                CLRecipe.VERB_UPDATED, CLRecipe.VERB_COMMENTED, CLRecipe.VERB_CLOSED, CLRecipe.VERB_OPENED]
    xapi_objects = [CLRecipe.OBJECT_COLLECTION, CLRecipe.OBJECT_FILE, CLRecipe.OBJECT_NOTE]

    user_api_association_name = 'GitHub Username' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Repository URL' # eg hashtags or a group name

    config_json_keys = ['token']
    # The number of data (records) in a page.
    parPage = 100

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = ['Collection', 'file', 'comment']
    xapi_verbs_to_includein_verbactivitywidget = ['created', 'added', 'removed', 'updated', 'commented']

    EVENT_TYPE_ISSUES = 'IssuesEvent'
    EVENT_TYPE_PR = 'PullRequestEvent'

    VERB_OBJECT_MAPPER = {}

    def __init__(self):
        pass


    def perform_import(self, retrieval_param, course_code):

        # Setup GitHub token
        token = os.environ.get("GITHUB_TOKEN")
        # token = "bc6fb01eb7e80fb69cc761fe3a3cbf7534354a90"
        # urls = retrieval_param.split(os.linesep)

        for details in retrieval_param:
            repo_name = details['repo_name']
            url = self.platform_url + repo_name
            token = details['token']
            print "GitHub data extraction URL: " + url
            # Instanciate PyGithub object
            # repo_name = url[len(self.platform_url):]
            gh = Github(login_or_token = token, per_page = self.parPage)

            repo = gh.get_repo(repo_name)
            self.import_commits(course_code, url, token, repo)
            self.import_issues(course_code, url, token, repo)
            self.import_commit_comments(course_code, url, token, repo)
            self.import_issue_comments(course_code, url, token, repo)


    ###################################################################
    # Import GitHub commit comments data.
    #   A library PyGithub is used to interact with GitHub API.
    #   See @ http://pygithub.readthedocs.org/en/stable/index.html
    ###################################################################
    def import_commit_comments(self, course_code, url, token, repo):
        count = 0
        commit_comments = repo.get_comments().get_page(count)

        # Retrieve issue data
        while True:
            for com_comment in commit_comments:
                author_homepage = com_comment.user.html_url
                author = com_comment.user.login
                com_comment_url = com_comment.html_url
                date = com_comment.updated_at
                comment_text = com_comment.body
                if comment_text is None:
                    comment_text = ""
                commit = repo.get_commit(com_comment.commit_id)
                commit_url = commit.html_url

                other_context_list = get_other_contextActivity(
                    com_comment_url, 'Verb', comment_text, 
                    CLRecipe.get_verb_iri(CLRecipe.VERB_COMMENTED))
                other_context_list = [other_context_list]

                if username_exists(author, course_code, self.platform.lower()):
                    usr_dict = get_userdetails(author, self.platform.lower())
                    cla_userame = get_username_fromsmid(author, self.platform)
                    insert_comment(usr_dict, commit_url, com_comment_url, 
                        comment_text, author, cla_userame,
                        date, course_code, self.platform, author_homepage,
                        author, author)

            count = count + 1
            commit_comments = repo.get_comments().get_page(count)
            temp = list(commit_comments)
            if len(temp) == 0:
                #Break from while
                break;
        

    ###################################################################
    # Import GitHub issue comments data.
    #   A library PyGithub is used to interact with GitHub API.
    #   See @ http://pygithub.readthedocs.org/en/stable/index.html
    ###################################################################
    def import_issue_comments(self, course_code, url, token, repo):
        count = 0
        issue_comments = repo.get_issues_comments().get_page(count)

        # Retrieve issue data
        while True:
            for iss_comment in issue_comments:
                author_homepage = iss_comment.user.html_url
                author = iss_comment.user.login
                issue_url = iss_comment.issue_url
                iss_comment_url = iss_comment.html_url
                date = iss_comment.updated_at
                body = iss_comment.body
                if body is None:
                    body = ""

                other_context_list = get_other_contextActivity(
                    iss_comment_url, 'Verb', body, 
                    CLRecipe.get_verb_iri(CLRecipe.VERB_COMMENTED))
                other_context_list = [other_context_list]

                if username_exists(author, course_code, self.platform.lower()):
                    usr_dict = get_userdetails(author, self.platform.lower())
                    cla_userame = get_username_fromsmid(author, self.platform)
                    insert_comment(usr_dict, issue_url, iss_comment_url, 
                        body, author, cla_userame,
                        date, course_code, self.platform, author_homepage,
                        author, author, other_contexts = other_context_list)

            count = count + 1
            issue_comments = repo.get_issues_comments().get_page(count)
            temp = list(issue_comments)
            if len(temp) == 0:
                #Break from while
                break;

    ###################################################################
    # Import GitHub all issues including pull request
    # Note that issues include pull requests.
    # 
    #   A library PyGithub is used to interact with GitHub API.
    #   See @ http://pygithub.readthedocs.org/en/stable/index.html
    ###################################################################
    def import_issues(self, course_code, repoUrl, token, repo):
        count = 0
        event_list = repo.get_events().get_page(count)

        while True:
            for event in event_list:
                # print 'Evet type === ' + event.type
                if event.type == self.EVENT_TYPE_ISSUES:

                    issue = event.payload['issue']

                    action = event.payload['action']
                    author = issue['user']['login']
                    author_homepage = issue['user']['html_url']
                    issue_url = issue['html_url']
                    title = issue['title']
                    body = issue['body']
                    if title is None:
                        title = ''
                    if body is None:
                        body = ''
                    body = title + '\n' + body
                    if body == '\n':
                        body = ''

                    verb = CLRecipe.VERB_CREATED
                    date = issue['created_at']
                    if action == 'reopened':
                        verb = CLRecipe.VERB_OPENED
                        date = issue['updated_at']
                    elif action == 'closed':
                        verb = CLRecipe.VERB_CLOSED
                        date = issue['updated_at']

                    other_context_list = get_other_contextActivity(
                        issue_url, 'Verb', body, 
                        CLRecipe.get_verb_iri(verb))
                    other_context_list = [other_context_list]

                    if username_exists(author, course_code, self.platform.lower()):
                        usr_dict = get_userdetails(author, self.platform.lower())
                        cla_userame = get_username_fromsmid(author, self.platform)
                        insert_issue(usr_dict, issue_url, verb, CLRecipe.OBJECT_NOTE, 
                            CLRecipe.OBJECT_COLLECTION, body, author, cla_userame, date, 
                            course_code, repoUrl, self.platform, event.id, author, author_homepage,
                            other_contexts = other_context_list)


            count = count + 1
            event_list = repo.get_events().get_page(count)
            temp = list(event_list)
            #print "# of content in repo.get_events.get_page(count) = " + str(len(temp))
            #If length is 0, it means that no commit data is left.
            if len(temp) == 0:
                #Break from while loop
                break;







        # # Search issues including pull requests using search method
        # count = 0

        # repo_name = repoUrl[len(self.platform_url):]
        # query = 'repo:' + repo_name
        # issueList = githubObj.search_issues(query, order = 'asc').get_page(count)

        # # Retrieve issue data
        # while True:
        #     for issue in issueList:
        #         assigneeHomepage = issue.user.html_url
        #         assignee = issue.user.login
        #         issueURL = issue.html_url
        #         date = issue.updated_at

        #         body = issue.body
        #         if body is None or body == "":
        #             body = issue.title

        #         # TODO:
        #         # When pull request data is imported, verb needs to be shared (or sth better one).
        #         # 
        #         # Pull request data is retrieved only when it is open. 
        #         #  Closed pull requests are not included in the get_issues() method.
        #         #if issue.pull_request:
        #         #    # Verb for a pull request
        #         #    verb = 'shared'

        #         #TODO:
        #         # Tag object should ideally be passed to insert_issue() medthod,
        #         # if someone is mentioned (e.g. @kojiagile is working on this issue...)
        #         # 
        #         if username_exists(assignee, courseCode, self.platform.lower()):
        #             usr_dict = get_userdetails(assignee, self.platform.lower())
        #             claUserName = get_username_fromsmid(assignee, self.platform)
        #             insert_issue(usr_dict, issueURL, body, assignee, claUserName,
        #                 date, courseCode, repoUrl, self.platform, issueURL, 
        #                 assignee, assigneeHomepage)

        #     count = count + 1
        #     issueList = githubObj.search_issues(query, order = 'asc').get_page(count)
        #     temp = list(issueList)
        #     #print "# of content in githubObj.search_issues.get_page(count) = " + str(len(temp))
        #     #If length is 0, it means that no commit data is left.
        #     if len(temp) == 0:
        #         #Break from while loop
        #         break;



    ###################################################################
    # Import GitHub commit data.
    #   A library PyGithub is used to interact with GitHub API.
    #   See @ http://pygithub.readthedocs.org/en/stable/index.html
    ###################################################################
    def import_commits(self, course_code, repoUrl, token, repo):
        count = 0
        commitList = repo.get_commits().get_page(count)

        # Retrieve commit data
        while True:
            for commit in commitList:
                author = ""
                email = ""
                if commit.author is None or commit.author.login == "":
                    # Note: What is the difference between author and committer?
                    # 
                    # The author is the person who originally wrote the work,
                    # whereas the committer is the person who last applied the work. 
                    # So, if you send in a patch to a project and one of the core members applies the patch, 
                    # both of you get credit --- you as the author and the core member as the committer.
                    print "commit.committer is null. url = " + commit.html_url
                    #author = commit.author.name
                    #email = commit.author.email
                    author = commit.committer.login
                    email = commit.commit.committer.email
                    date = commit.commit.committer.date
                    continue
                else:
                    author = commit.author.login
                    email = commit.commit.author.email
                    date = commit.commit.author.date

                # Rare case but committer name does not exist in some cases 
                if not username_exists(author, course_code, self.platform.lower()):
                    author = commit.commit.author.name
                    email = commit.commit.author.email
                    date = commit.commit.author.date

                commit_title = commit.commit.message
                commit_html_url = commit.html_url
                date = commit.commit.author.date
                # commit.committer.html_url isn't always correct. So, don't use it.
                # author_homepage = commit.committer.html_url
                author_homepage = self.platform_url + author

                # Import commit data
                usr_dict = None
                cla_userame = None
                # create other context activity value
                file_details_val = ''
                for file in commit.files:
                    val = '%s:%s:%s' % (file.filename, str(file.additions), str(file.deletions))
                    if file_details_val != '':
                        file_details_val = file_details_val + ','
                    file_details_val = file_details_val + val
                
                stats = commit.stats
                other_context_val = 'total:%s,additions:%s,deletions:%s' % (stats.total, str(stats.additions), str(stats.deletions))
                other_context_val = other_context_val + '&' + file_details_val
                other_context_list = get_other_contextActivity(
                    commit_html_url, 'Verb', other_context_val, 
                    CLRecipe.get_verb_iri(CLRecipe.VERB_CREATED))
                other_context_list = [other_context_list]

                if username_exists(author, course_code, self.platform.lower()):
                    usr_dict = get_userdetails(author, self.platform.lower())
                    cla_userame = get_username_fromsmid(author, self.platform.lower())
                    insert_commit(usr_dict, commit_html_url, commit_title, author, cla_userame,
                        date, course_code, repoUrl, self.platform, commit_html_url, author, author_homepage,
                        other_contexts = other_context_list)
                else:
                    #If a user does not exist, ignore the commit data
                    continue

                # All committed files are inserted into DB
                for file in commit.files:
                    verb = CLRecipe.VERB_ADDED
                    if file.status == "modified":
                        verb = CLRecipe.VERB_UPDATED
                    elif file.status == "removed":
                        verb = CLRecipe.VERB_REMOVED

                    patch = file.patch
                    if file.patch is None:
                        patch = ""

                    file_details_val = 'name:%s,total:%s,additions:%s,deletions:%s' % (
                        file.filename, str(file.changes), str(file.additions), str(file.deletions))
                    other_context_list = get_other_contextActivity(
                        commit_html_url, 'Verb', file_details_val, 
                        CLRecipe.get_verb_iri(verb))
                    other_context_list = [other_context_list]
                    if username_exists(author, course_code, self.platform.lower()):
                        insert_file(usr_dict, file.blob_url, patch, author, cla_userame,
                            date, course_code, commit_html_url, self.platform, file.blob_url, 
                            # commit_html_url, verb, repoUrl, file.additions, file.deletions, author)
                            commit_html_url, verb, repoUrl, author, author_homepage,
                            other_contexts = other_context_list)

            # End of for commit in commitList:

            # Pagination:
            # API response does not contain the number of pages left.
            # (It is included in HTTP header (link header).)
            # The content in next page needs to be retrieved
            # to know that there are still records to be imported.
            count = count + 1
            commitList = repo.get_commits().get_page(count)
            temp = list(commitList)
            #print "# of content in repo.get_commits().get_page(" + str(count) + ") = " + str(len(temp))
            #If length is 0, it means that no commit data is left.
            if len(temp) == 0:
                #Break from while
                break


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