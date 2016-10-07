from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin
from dataintegration.core.socialmediarecipebuilder import *
from dataintegration.core.recipepermissions import *
from github import Github
import os


class GithubPlugin(DIBasePlugin, DIPluginDashboardMixin):

    platform = "GitHub"
    platform_url = "https://github.com/"

    xapi_verbs = ['created', 'added', 'removed', 'updated', 'commented']
    xapi_objects = ['Collection', 'file', 'comment']

    user_api_association_name = 'GitHub Username' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Repository URL' # eg hashtags or a group name

    config_json_keys = ['token']
    # The number of data (records) in a page.
    parPage = 100

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = ['Collection', 'file', 'comment']
    xapi_verbs_to_includein_verbactivitywidget = ['created', 'added', 'removed', 'updated', 'commented']

    def __init__(self):
        pass

    def perform_import(self, retrieval_param, unit):

        # Setup GitHub token
        token = os.environ.get("GITHUB_TOKEN")
        urls = retrieval_param.split(os.linesep)

        for url in urls:
            # Instantiate PyGithub object
            repo_name = url[len(self.platform_url):]
            gh = Github(login_or_token = token, per_page = self.parPage)

            repo = gh.get_repo(repo_name.rstrip())
            self.import_commits(unit, url, repo)
            self.import_issues(unit, url, repo, gh)
            self.import_commit_comments(unit, url, repo)
            self.import_issue_comments(unit, url, repo)


    ###################################################################
    # Import GitHub commit comments data.
    #   A library PyGithub is used to interact with GitHub API.
    #   See @ http://pygithub.readthedocs.org/en/stable/index.html
    ###################################################################
    def import_commit_comments(self, unit, url, repo):
        count = 0
        commit_comments = repo.get_comments().get_page(count)

        # Retrieve issue data
        while True:
            for comment in commit_comments:
                author_homepage = comment.user.html_url
                author = comment.user.login
                comment_url = comment.html_url
                date = comment.updated_at
                body = comment.body
                if body is None:
                    body = ""
                commit = repo.get_commit(comment.commit_id)
                commit_url = commit.html_url
                parent_username = commit.committer.login

                if username_exists(author, unit, self.platform.lower()):
                    user = get_user_from_screen_name(author, self.platform)

                    if username_exists(parent_username, unit, self.platform.lower()):
                        parent_user = get_user_from_screen_name(parent_username, self.platform.lower())
                        parent_user_external = None
                    else:
                        parent_user = None
                        parent_user_external = parent_username

                    insert_comment(user, commit_url, comment_url, body, date, unit, self.platform, author_homepage,
                                   parent_user, parent_user_external)

            count += 1
            commit_comments = repo.get_comments().get_page(count)
            temp = list(commit_comments)
            if len(temp) == 0:
                break
        

    ###################################################################
    # Import GitHub issue comments data.
    #   A library PyGithub is used to interact with GitHub API.
    #   See @ http://pygithub.readthedocs.org/en/stable/index.html
    ###################################################################
    def import_issue_comments(self, unit, url, repo):
        count = 0
        issue_comments = repo.get_issues_comments().get_page(count)

        # Retrieve issue data
        while True:
            for comment in issue_comments:
                author_homepage = comment.user.html_url
                author = comment.user.login
                issue_url = comment.issue_url
                comment_url = comment.html_url
                date = comment.updated_at
                body = comment.body
                if body is None:
                    body = ""

                issue_url_parts = issue_url.split("/")
                issue_num = issue_url_parts[len(issue_url_parts) - 1]

                issue = repo.get_issue(issue_num)
                parent_username = issue.user.login

                if username_exists(author, unit, self.platform.lower()):
                    user = get_user_from_screen_name(author, self.platform)

                    if username_exists(parent_username, unit, self.platform.lower()):
                        parent_user = get_user_from_screen_name(parent_username, self.platform.lower())
                        parent_user_external = None
                    else:
                        parent_user = None
                        parent_user_external = parent_username

                    insert_comment(user, issue_url, comment_url, body, date, unit, self.platform, author_homepage,
                                   parent_user, parent_user_external)

            count += 1
            issue_comments = repo.get_issues_comments().get_page(count)
            temp = list(issue_comments)
            if len(temp) == 0:
                break

    ###################################################################
    # Import GitHub all issues.
    # Note that issues include pull requests.
    # 
    #   A library PyGithub is used to interact with GitHub API.
    #   See @ http://pygithub.readthedocs.org/en/stable/index.html
    ###################################################################
    def import_issues(self, unit, repo_url, repo, githubObj):
        # Search issues including pull requests using search method
        count = 0

        repo_name = repo_url[len(self.platform_url):]
        query = 'repo:' + repo_name
        issue_list = githubObj.search_issues(query, order='asc').get_page(count)

        # Retrieve issue data
        while True:
            for issue in issue_list:
                user_homepage = issue.user.html_url
                username = issue.user.login
                issue_url = issue.html_url
                date = issue.updated_at

                body = issue.body
                if body is None or body == "":
                    body = issue.title

                # TODO:
                # When pull request data is imported, verb needs to be shared (or sth better one).
                # 
                # Pull request data is retrieved only when it is open. 
                #  Closed pull requests are not included in the get_issues() method.
                #if issue.pull_request:
                #    # Verb for a pull request
                #    verb = 'shared'

                #TODO:
                # Tag object should ideally be passed to insert_issue() medthod,
                # if someone is mentioned (e.g. @kojiagile is working on this issue...)
                # 
                if username_exists(username, unit, self.platform.lower()):
                    user = get_user_from_screen_name(username, self.platform.lower())
                    insert_issue(user, repo_url, issue_url, body, date, unit, self.platform)

            count += 1
            issue_list = githubObj.search_issues(query, order = 'asc').get_page(count)
            temp = list(issue_list)
            #print "# of content in githubObj.search_issues.get_page(count) = " + str(len(temp))
            #If length is 0, it means that no commit data is left.
            if len(temp) == 0:
                break


    ###################################################################
    # Import GitHub commit data.
    #   A library PyGithub is used to interact with GitHub API.
    #   See @ http://pygithub.readthedocs.org/en/stable/index.html
    ###################################################################
    def import_commits(self, unit, repo_url, repo):
        count = 0
        commit_list = repo.get_commits().get_page(count)

        # Retrieve commit data
        while True:
            for commit in commit_list:
                author = commit.author.login
                try:
                    committer = commit.committer.login
                except AttributeError:
                    committer = None

                message = commit.commit.message
                commit_url = commit.html_url
                date = commit.commit.author.date

                if username_exists(author, unit, self.platform.lower()):
                    user = get_user_from_screen_name(author, self.platform.lower())

                    committer_user = get_user_from_screen_name(committer, self.platform.lower()) if username_exists(
                        committer, unit, self.platform.lower()) else None

                    insert_commit(user, repo_url, commit_url, message, date, unit, self.platform, committer_user)

                    # All committed files are inserted into DB
                    for f in commit.files:
                        verb = "added"
                        if f.status == "modified":
                            verb = "updated"
                        elif f.status == "removed":
                            verb = "removed"

                        patch = f.patch
                        if f.patch is None:
                            patch = ""

                        insert_file(user, commit_url, f.blob_url, patch, date, unit, self.platform, verb)

            # End of for commit in commit_list:

            # Pagination:
            # API response does not contain the number of pages left.
            # (It is included in HTTP header (link header).)
            # The content in next page needs to be retrieved
            # to know that there are still records to be imported.
            count += 1
            commit_list = repo.get_commits().get_page(count)
            temp = list(commit_list)

            if len(temp) == 0:
                break

    def get_verbs(self):
        return self.xapi_verbs
            
    def get_objects(self):
        return self.xapi_objects


registry.register(GithubPlugin)
