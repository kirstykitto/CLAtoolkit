from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin, DIGoogleOAuth2WebServerFlowPluginMixin
from dataintegration.core.socialmediarecipebuilder import *
from dataintegration.core.recipepermissions import *
import json
import dateutil.parser
from dataintegration.googleLib import *
from dataintegration.models import Video, Comment
import os

class YoutubePlugin(DIBasePlugin, DIPluginDashboardMixin, DIGoogleOAuth2WebServerFlowPluginMixin):

    platform = "YouTube"
    platform_url = "http://www.youtube.com/"

    xapi_verbs = ['created', 'shared', 'liked', 'commented']
    xapi_objects = ['Video']

    user_api_association_name = 'Youtube Id' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Channel Id' # eg hashtags or a group name

    config_json_keys = ['CLIENT_ID', 'CLIENT_SECRET']

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = ['Video']
    xapi_verbs_to_includein_verbactivitywidget = ['created', 'shared', 'liked', 'commented']

    scope = 'https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtubepartner'

    def __init__(self):
        # Load api_config.json and convert to dict
        config_file = os.path.join(os.path.dirname(__file__), 'api_config.json')
        with open(config_file) as data_file:
            self.api_config_dict = json.load(data_file)

    def perform_import(self, retrieval_param, course_code, webserverflow_result):
        print "Youtube perform_import run"
        vList = []
        ytList = []
        channelCommList = self.injest_youtube_comment(course_code, retrieval_param, webserverflow_result)

        ytList.append(vList)
        ytList.append(channelCommList)
        return ytList

    def injest_youtube_comment(self, course_code, channelIds, http):

        channelCommList = self.injest_youtube_commentById(course_code, channelIds, http, False)
        print "Channel ID comment extraction result: " + str(len(channelCommList))
        #Don't think this code above works had to write another method to get the comment thread from a channel

        # Retrieve all video IDs in registered channels, and then retrieve all user's comments in the videos.
        channelIDList = channelIds.split('\r\n')
        videoIds,playlists = self.getAllVideoIDsInChannel(channelIDList, http)
        vidsinplaylist = self.getAllVideoIDsInPlaylist(playlists, http)
        videoIds.extend(vidsinplaylist)
        #channelcommentthreads = getChannelCommentThreads(channelIDList, http)
        videoCommList = self.injest_youtube_commentById(course_code, videoIds, http, True)
        channelCommList.extend(videoCommList)
        print "Video ID comment extraction result: " + str(len(channelCommList))
        return channelCommList

    #############################################################
    # Extract commented videos from YouTube and insert it into DB
    #############################################################
    def injest_youtube_commentById(self, course_code, allIds, http, isVideoIdSearch):
        isFirstTime = True
        nextPageToken = ""
        commList = []
        id_creator_dict = {}
        id_creator_displayname_dict = {}

        if not isinstance(allIds, list):
            ids = allIds.split(os.linesep)
        else:
            ids = allIds

        #Get all users in the unit(course)
        #usersInUnit = getAllUsersInCourseById(course_code) #course_id

        for singleId in ids:
            #Get comments by channel ID
            while isFirstTime or nextPageToken is not "":
                ret = self.extractCommentsById(singleId, nextPageToken, isVideoIdSearch, http)
                #Check the number of result
                if ret.get('nextPageToken'):
                    nextPageToken = ret['nextPageToken']
                else:
                    nextPageToken = ""

                # Retrieve comments from API response
                tempList, id_creator_dict_temp, id_creator_displayname_dict_temp = self.getCommentsFromResponse(ret, course_code)
                id_creator_dict.update(id_creator_dict_temp)
                id_creator_displayname_dict.update(id_creator_displayname_dict_temp)

                commList.extend(tempList)
                isFirstTime = False

            # Initialize the flag for next loop
            isFirstTime = True
            nextPageToken = ""

        for comment in commList:

            if comment.commId in id_creator_dict:
                if username_exists(comment.authorDispName, course_code, self.platform):
                    usr_dict = get_userdetails(comment.authorDispName, self.platform)
                    #userInfo = getUserDetailsByGoogleAccount(comment.authorDispName, usersInUnit)
                    #userInfo['googleAcName'] = get_username_fromsmid(id_creator_dict[comment.commId], "YouTube")
                    #usr_dict = {'googleAcName': userInfo['googleAcName'], 'email': userInfo['email']}

                    parentusername = ""
                    parentdisplayname = ""
                    postid = comment.commId
                    parentId = ""
                    username = get_username_fromsmid(comment.authorDispName, self.platform)
                    if (comment.isReply):

                        #there is an odd .xxxx in comments from YouTube

                        parentId = comment.parentId
                        if parentId in id_creator_displayname_dict:
                            #print "insert comment"
                            parentdisplayname = id_creator_displayname_dict[parentId]
                            parentusername = get_username_fromsmid(id_creator_dict[parentId], "YouTube")

                            insert_comment(usr_dict, parentId, postid,
                                            comment.text, comment.authorDispName, username,
                                            comment.updatedAt, course_code, self.platform, self.platform_url, parentusername, parentdisplayname)
                    else:
                        #print "insert post"
                        insert_post(usr_dict, postid, comment.text, comment.authorDispName, username, comment.updatedAt, course_code, self.platform, self.platform_url)

        return commList


    ##############################################
    # Get all video IDs in registered channels
    ##############################################
    def getAllVideoIDsInChannel(self, channelIds, http):
        ret = []
        playlists = []
        isFirstTime = True
        nextPageToken = ""

        #Create youtube API controller
        service = build('youtube', 'v3', http=http)
        idVal = "id"
        resultOrder = "date"
        maxResultsNum = 50

        for cid in channelIds:
            while isFirstTime or nextPageToken is not "":
                if nextPageToken is not "":
                    searchRet = service.search().list(
                        part = idVal,
                        maxResults = maxResultsNum,
                        order = resultOrder,
                        channelId = cid,
                        pageToken = nextPageToken
                    ).execute()
                else:
                    searchRet = service.search().list(
                        part = idVal,
                        maxResults = maxResultsNum,
                        order = resultOrder,
                        channelId = cid
                    ).execute()

                #When an error occurs
                if searchRet.get('error'):
                    print "An error has occured in getAllVideoIDsInChannel() method."
                    return ret

                if searchRet.get('nextPageToken'):
                    nextPageToken = str(searchRet['nextPageToken'])
                else:
                    nextPageToken = ""

                #Loop to get all items
                for item in searchRet['items']:
                    #print "Video Ids"
                    #print item['id']
                    info = item['id']
                    if info.get('videoId'):
                        ret.append(item['id']['videoId'])
                        #print item['id']['videoId']
                    elif info.get('kind')=='youtube#playlist':
                        playlists.append(info.get('playlistId'))

                isFirstTime = False

            # Initialize the flag for next loop
            isFirstTime = True
            nextPageToken = ""

        return ret,playlists


    ###################################################################################
    # Get comment threads directly linked to a channel (i.e., under the discussion tab)
    ###################################################################################
    def getChannelCommentThreads(self, channelIds, http):
        ret = []
        isFirstTime = True
        nextPageToken = ""

        #Create youtube API controller
        service = build('youtube', 'v3', http=http)
        idVal = "id"
        resultOrder = "time"
        maxResultsNum = 50

        for cid in channelIds:
            while isFirstTime or nextPageToken is not "":
                if nextPageToken is not "":
                    searchRet = service.commentThreads().list(
                        part = idVal,
                        maxResults = maxResultsNum,
                        order = resultOrder,
                        channelId = cid,
                        pageToken = nextPageToken
                    ).execute()
                else:
                    searchRet = service.commentThreads().list(
                        part = idVal,
                        maxResults = maxResultsNum,
                        order = resultOrder,
                        channelId = cid
                    ).execute()

                #When an error occurs
                if searchRet.get('error'):
                    print "An error has occured in getChannelCommentThreads() method."
                    return ret

                if searchRet.get('nextPageToken'):
                    nextPageToken = str(searchRet['nextPageToken'])
                else:
                    nextPageToken = ""

                #Loop to get all items
                for item in searchRet['items']:
                    #print "Video Ids"
                    #print item['id']
                    if item['id']:
                        ret.append(item['id'])

                isFirstTime = False

            # Initialize the flag for next loop
            isFirstTime = True
            nextPageToken = ""

        return ret


    ##############################################
    # Get all video IDs from a playlist
    ##############################################
    def getAllVideoIDsInPlaylist(self, playlistids, http):
        #print "getAllVideoIDsInPlaylist called"
        ret = []
        isFirstTime = True
        nextPageToken = ""

        #Create youtube API controller
        service = build('youtube', 'v3', http=http)
        maxResultsNum = 50

        for cid in playlistids:
            while isFirstTime or nextPageToken is not "":
                if nextPageToken is not "":
                    searchRet = service.playlistItems().list(
                        part = 'contentDetails',
                        maxResults = maxResultsNum,
                        playlistId = cid,
                        pageToken = nextPageToken
                    ).execute()
                else:
                    searchRet = service.playlistItems().list(
                        part = 'contentDetails',
                        maxResults = maxResultsNum,
                        playlistId = cid
                    ).execute()

                #When an error occurs
                if searchRet.get('error'):
                    print "An error has occured in getAllVideoIDsInPlaylist() method."
                    return ret

                if searchRet.get('nextPageToken'):
                    nextPageToken = str(searchRet['nextPageToken'])
                else:
                    nextPageToken = ""

                #Loop to get all items
                for item in searchRet['items']:
                    #print "Video Ids"
                    #print "vid in playlist", item['contentDetails']['videoId']
                    if item['contentDetails']['videoId']:
                        ret.append(item['contentDetails']['videoId'])

                isFirstTime = False

            # Initialize the flag for next loop
            isFirstTime = True
            nextPageToken = ""

        return ret

    ################################################################
    # Extract comments by either channel ID or video ID from YouTube
    ################################################################
    def extractCommentsById(self, singleId, nextPageToken, isVideoIdSearch, http):
        #Create youtube API controller
        service = build('youtube', 'v3', http=http)
        idVal = "id,snippet,replies"
        resultOrder = "time"
        maxResultsNum = 100
        ret = []

        if isVideoIdSearch:
            # Extract data from social media by video ID
            if nextPageToken is not "":
                ret = service.commentThreads().list(
                    part = idVal,
                    maxResults = maxResultsNum,
                    order = resultOrder,
                    videoId = singleId,
                    pageToken = nextPageToken
                ).execute()
            else:
                ret = service.commentThreads().list(
                    part = idVal,
                    maxResults = maxResultsNum,
                    order = resultOrder,
                    videoId = singleId
                ).execute()
        else:
            # Extract data from social media by channel ID
            if nextPageToken is not "":
                ret = service.commentThreads().list(
                    part = idVal,
                    maxResults = maxResultsNum,
                    order = resultOrder,
                    channelId = singleId,
                    pageToken = nextPageToken
                ).execute()
            else:
                ret = service.commentThreads().list(
                    part = idVal,
                    maxResults = maxResultsNum,
                    order = resultOrder,
                    channelId = singleId
                ).execute()

        return ret


    #############################################################
    # Retrieve comments from YouTube API response
    #############################################################
    def getCommentsFromResponse(self, apiResponse, course_code):
        commList = []
        id_creator_dict = {}
        id_creator_displayname_dict = {}

        #When an error occurs
        if apiResponse.get('error'):
            return commList

        #Loop to get all items
        for item in apiResponse['items']:
            #Check if the comment is already in DB
            replies = None
            if u'replies' in item:
                replies = item[u'replies']
            else:
                print "No replies"

            author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            authorChannelUrl = item['snippet']['topLevelComment']['snippet']['authorChannelUrl']

            comm = Comment()
            comm.commId = item['id']
            # Top level comment's parent ID is the same as ID
            comm.parentId = item['id'] # Todo - This is incorrect and should not be assigned here
            comm.authorDispName = authorChannelUrl #author

            comm.isReply = False

            snippet = item['snippet']
            secondSnippet = item['snippet']['topLevelComment']['snippet']
            if secondSnippet.get('textOriginal'):
                comm.text = secondSnippet['textOriginal']
            else:
                comm.text = secondSnippet['textDisplay']

            if snippet.get('videoId'):
                comm.videoId = snippet['videoId']
                comm.videoUrl = STR_YT_VIDEO_BASE_URL + comm.videoId
            if snippet.get('channelId'):
                comm.channelId = snippet['channelId']
                comm.channelUrl = STR_YT_CHANNEL_BASE_URL + comm.channelId

            # Timestamp that the comment was published.
            # UpdatedAt is the same as publishedAt when the comment isn't updated.
            comm.updatedAt = secondSnippet['updatedAt']
            commList.append(comm)
            id_creator_dict[item['id']] = authorChannelUrl
            id_creator_displayname_dict[item['id']] = author

            #Check if replies exist

            if replies is not None:

                for reply in replies[u'comments']:

                    author = reply['snippet']['authorDisplayName']
                    authorChannelUrl = reply['snippet']['authorChannelUrl']

                    replyComm = Comment()
                    replyComm.isReply = True
                    replyComm.commId = reply['id']
                    snippet = reply['snippet']
                    replyComm.authorDispName = snippet['authorChannelUrl'] #snippet['authorDisplayName']
                    id_creator_dict[reply['id']] = snippet['authorChannelUrl']
                    id_creator_displayname_dict[reply['id']] = author

                    replyComm.parentId = snippet['parentId'] #snippet['parentId']

                    if snippet.get('textOriginal'):
                        replyComm.text = snippet['textOriginal']
                    else:
                        replyComm.text = snippet['textDisplay']

                    if snippet.get('videoId'):
                        replyComm.videoId = snippet['videoId']
                        replyComm.videoUrl = STR_YT_VIDEO_BASE_URL + replyComm.videoId
                    if snippet.get('channelId'):
                        replyComm.channelId = snippet['channelId']
                        replyComm.channelUrl = STR_YT_CHANNEL_BASE_URL + replyComm.channelId

                    replyComm.updatedAt = snippet['updatedAt']

                    commList.append(replyComm)

        return commList,id_creator_dict,id_creator_displayname_dict

registry.register(YoutubePlugin)
