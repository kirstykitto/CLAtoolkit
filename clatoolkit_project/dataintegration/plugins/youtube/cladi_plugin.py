from dataintegration.core.plugins import registry
from dataintegration.core.plugins.base import DIBasePlugin, DIPluginDashboardMixin, DIGoogleOAuth2WebServerFlowPluginMixin

from dataintegration.core.importer import *
from dataintegration.core.di_utils import * #Formerly dataintegration.core.recipepermissions
from xapi.statement.builder import * #Formerly dataintegration.core.socialmediabuilder

import json
import dateutil.parser
from dataintegration.googleLib import *
# from dataintegration.models import Video, Comment
import os
from xapi.statement.xapi_settings import xapi_settings


class YoutubePlugin(DIBasePlugin, DIPluginDashboardMixin, DIGoogleOAuth2WebServerFlowPluginMixin):

    platform = xapi_settings.PLATFORM_YOUTUBE
    platform_url = "https://www.youtube.com/"

    xapi_verbs = [xapi_settings.VERB_CREATED, xapi_settings.VERB_SHARED, 
                  xapi_settings.VERB_LIKED, xapi_settings.VERB_COMMENTED]

    xapi_objects = [xapi_settings.OBJECT_VIDEO]

    user_api_association_name = 'Youtube Id' # eg the username for a signed up user that will appear in data extracted via a social API
    unit_api_association_name = 'Channel Id' # eg hashtags or a group name

    config_json_keys = ['YOUTUBE_CLIENT_ID', 'YOUTUBE_CLIENT_SECRET']

    #from DIPluginDashboardMixin
    xapi_objects_to_includein_platformactivitywidget = [xapi_settings.OBJECT_VIDEO]
    xapi_verbs_to_includein_verbactivitywidget = [xapi_settings.VERB_CREATED, xapi_settings.VERB_SHARED, 
                                                  xapi_settings.VERB_LIKED, xapi_settings.VERB_COMMENTED]

    scope = 'https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtubepartner'

    def __init__(self):
        pass


    def perform_import(self, retrieval_param, unit, webserverflow_result):
        print "Start YouTube data import....."
        vList = []
        ytList = []
        self.import_comments(unit, retrieval_param, webserverflow_result)



    def import_comments(self, unit, channel_ids, http):
        self.import_comment_from_channel_discussion(unit, channel_ids, http)
        # print "Channel ID comment extraction result: " + str(len(channelCommList))
        #Don't think this code above works had to write another method to get the comment thread from a channel

        # Retrieve all video IDs in registered channels, and then retrieve all user's comments in the videos.
        # channelIDList = channel_ids.split('\r\n')
        video_ids, playlists = self.get_all_video_ids_in_channel(channel_ids, http)
        vidsinplaylist = self.get_all_video_ids_in_playlist(playlists, http)
        video_ids.extend(vidsinplaylist)
        #channelcommentthreads = getChannelCommentThreads(channelIDList, http)
        print 'video ids in channel ids'
        print video_ids

        self.import_comment_from_video(unit, video_ids, http)



    def import_comment_from_channel_discussion(self, unit, channel_ids, http):
        is_first = True
        next_page_token = ""
        retrieved_from_video = False

        channel_id_list = channel_ids.split(',')
        for cid in channel_id_list:
            #Get comments by channel ID
            while is_first or next_page_token is not "":
                api_response = self.get_api_response(cid, next_page_token, retrieved_from_video, http)
                #Check the number of result
                if api_response.get('nextPageToken'):
                    next_page_token = api_response['nextPageToken']
                else:
                    next_page_token = ""

                #When an error occurs
                if api_response.get('error'):
                    break

                self.insert_comments(unit, cid, api_response, retrieved_from_video)

                # commList.extend(tempList)
                is_first = False

            # Initialize the flag for next loop
            is_first = True
            next_page_token = ""



    def import_comment_from_video(self, unit, video_id_list, http):
        is_first = True
        next_page_token = ""
        retrieved_from_video = True

        for vid in video_id_list:
            #Get comments by channel ID
            while is_first or next_page_token is not "":
                api_response = self.get_api_response(vid, next_page_token, retrieved_from_video, http)
                #Check the number of result
                if api_response.get('nextPageToken'):
                    next_page_token = api_response['nextPageToken']
                else:
                    next_page_token = ""

                #When an error occurs
                if api_response.get('error'):
                    break

                self.insert_comments(unit, vid, api_response, retrieved_from_video)

                # commList.extend(tempList)
                is_first = False

            # Initialize the flag for next loop
            is_first = True
            next_page_token = ""



    # If retrieved_from_video is False, comments were retrieved from discussion tab in a channel
    def insert_comments(self, unit, object_id, api_response, retrieved_from_video):
        #Loop to get all items
        for item in api_response['items']:

            # comment_id = STR_YT_CHANNEL_BASE_URL + object_id + '/' + item['id']
            comment_id = self.create_url_by_search_type(object_id, item['id'], retrieved_from_video)
            comment_author_channel_url = item['snippet']['topLevelComment']['snippet']['authorChannelUrl']

            snippet = item['snippet']
            secondSnippet = item['snippet']['topLevelComment']['snippet']
            comment_text = ''
            if secondSnippet.get('textOriginal'):
                comment_text = secondSnippet['textOriginal']
            else:
                comment_text = secondSnippet['textDisplay']

            parent_id = STR_YT_CHANNEL_BASE_URL + object_id

            # Timestamp that the comment was published.
            # UpdatedAt is the same as publishedAt when the comment isn't updated.
            comment_date = secondSnippet['updatedAt']

            user = None
            if username_exists(comment_author_channel_url, unit, self.platform):
                user = get_user_from_screen_name(comment_author_channel_url, self.platform)

                insert_comment(user, parent_id, comment_id, comment_text, comment_date, unit, 
                               self.platform, self.platform_url)

            # Import replies on the comment
            self.insert_replies(unit, object_id, comment_id, item, user, retrieved_from_video)



    # If retrieved_from_video is False, comments were retrieved from discussion tab in a channel
    def insert_replies(self, unit, object_id, comment_id, item, parent_user, retrieved_from_video):
        replies = None
        if u'replies' in item:
            replies = item[u'replies']
        else:
            return

        for reply in replies[u'comments']:
            # reply_id = STR_YT_CHANNEL_BASE_URL + object_id + reply['id']
            reply_id = self.create_url_by_search_type(object_id, reply['id'], retrieved_from_video)

            snippet = reply['snippet']
            reply_author_channel_url = snippet['authorChannelUrl']

            reply_text = ''
            if snippet.get('textOriginal'):
                reply_text = snippet['textOriginal']
            else:
                reply_text = snippet['textDisplay']

            parent_id = comment_id
            reply_date = snippet['updatedAt']

            if username_exists(reply_author_channel_url, unit, self.platform):
                user = get_user_from_screen_name(reply_author_channel_url, self.platform)

                insert_comment(user, parent_id, reply_id, reply_text, reply_date, unit, 
                               self.platform, self.platform_url, parent_user = parent_user)


    def create_url_by_search_type(self, object_id, comment_id, is_video_url):
        url = STR_YT_VIDEO_BASE_URL + object_id + '/' + comment_id
        if not is_video_url:
            url = STR_YT_CHANNEL_BASE_URL + object_id + '/discussion/' + comment_id

        return url


    ##############################################
    # Get all video IDs in registered channels
    ##############################################
    def get_all_video_ids_in_channel(self, channel_ids, http):
        ret = []
        playlists = []
        is_first_time = True
        next_page_token = ""

        #Create youtube API controller
        service = build('youtube', 'v3', http=http)
        idVal = "id"
        resultOrder = "date"
        maxResultsNum = 50

        cids = channel_ids.split('\r\n')
        for cid in cids:
            while is_first_time or next_page_token is not "":
                if next_page_token is not "":
                    searchRet = service.search().list(
                        part = idVal,
                        maxResults = maxResultsNum,
                        order = resultOrder,
                        channelId = cid,
                        pageToken = next_page_token
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
                    print "An error has occured in get_all_video_ids_in_channel() method."
                    return ret

                if searchRet.get('nextPageToken'):
                    next_page_token = str(searchRet['nextPageToken'])
                else:
                    next_page_token = ""

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

                is_first_time = False

            # Initialize the flag for next loop
            is_first_time = True
            next_page_token = ""

        return ret,playlists


    # ###################################################################################
    # # Get comment threads directly linked to a channel (i.e., under the discussion tab)
    # ###################################################################################
    # def getChannelCommentThreads(self, channelIds, http):
    #     ret = []
    #     is_first_time = True
    #     nextPageToken = ""

    #     #Create youtube API controller
    #     service = build('youtube', 'v3', http=http)
    #     idVal = "id"
    #     resultOrder = "time"
    #     maxResultsNum = 50

    #     for cid in channelIds:
    #         while is_first_time or nextPageToken is not "":
    #             if nextPageToken is not "":
    #                 searchRet = service.commentThreads().list(
    #                     part = idVal,
    #                     maxResults = maxResultsNum,
    #                     order = resultOrder,
    #                     channelId = cid,
    #                     pageToken = nextPageToken
    #                 ).execute()
    #             else:
    #                 searchRet = service.commentThreads().list(
    #                     part = idVal,
    #                     maxResults = maxResultsNum,
    #                     order = resultOrder,
    #                     channelId = cid
    #                 ).execute()

    #             #When an error occurs
    #             if searchRet.get('error'):
    #                 print "An error has occured in getChannelCommentThreads() method."
    #                 return ret

    #             if searchRet.get('nextPageToken'):
    #                 nextPageToken = str(searchRet['nextPageToken'])
    #             else:
    #                 nextPageToken = ""

    #             #Loop to get all items
    #             for item in searchRet['items']:
    #                 #print "Video Ids"
    #                 #print item['id']
    #                 if item['id']:
    #                     ret.append(item['id'])

    #             is_first_time = False

    #         # Initialize the flag for next loop
    #         is_first_time = True
    #         nextPageToken = ""

    #     return ret


    ##############################################
    # Get all video IDs from a playlist
    ##############################################
    def get_all_video_ids_in_playlist(self, playlistids, http):
        #print "getAllVideoIDsInPlaylist called"
        ret = []
        is_first_time = True
        next_page_token = ""

        #Create youtube API controller
        service = build('youtube', 'v3', http=http)
        maxResultsNum = 50

        for cid in playlistids:
            while is_first_time or next_page_token is not "":
                if next_page_token is not "":
                    searchRet = service.playlistItems().list(
                        part = 'contentDetails',
                        maxResults = maxResultsNum,
                        playlistId = cid,
                        pageToken = next_page_token
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
                    next_page_token = str(searchRet['nextPageToken'])
                else:
                    next_page_token = ""

                #Loop to get all items
                for item in searchRet['items']:
                    #print "Video Ids"
                    #print "vid in playlist", item['contentDetails']['videoId']
                    if item['contentDetails']['videoId']:
                        ret.append(item['contentDetails']['videoId'])

                is_first_time = False

            # Initialize the flag for next loop
            is_first_time = True
            next_page_token = ""

        return ret

    ################################################################
    # Extract comments by either channel ID or video ID from YouTube
    ################################################################
    def get_api_response(self, channel_id, next_page_token, is_videoid_search, http):
        #Create youtube API controller
        service = build('youtube', 'v3', http=http)
        id_val = "id,snippet,replies"
        result_order = "time"
        max_result_num = 100
        ret = []

        if is_videoid_search:
            # Extract data from social media by video ID
            if next_page_token is not "":
                ret = service.commentThreads().list(
                    part = id_val,
                    maxResults = max_result_num,
                    order = result_order,
                    videoId = channel_id,
                    pageToken = next_page_token
                ).execute()
            else:
                ret = service.commentThreads().list(
                    part = id_val,
                    maxResults = max_result_num,
                    order = result_order,
                    videoId = channel_id
                ).execute()
        else:
            # Extract data from social media by channel ID
            if next_page_token is not "":
                ret = service.commentThreads().list(
                    part = id_val,
                    maxResults = max_result_num,
                    order = result_order,
                    channelId = channel_id,
                    pageToken = next_page_token
                ).execute()
            else:
                ret = service.commentThreads().list(
                    part = id_val,
                    maxResults = max_result_num,
                    order = result_order,
                    channelId = channel_id
                ).execute()

        return ret


    #############################################################
    # Retrieve comments from YouTube API response
    #############################################################
    def getCommentsFromResponse(self, api_response, unit):
        commList = []
        id_creator_dict = {}
        id_creator_displayname_dict = {}

        #When an error occurs
        if api_response.get('error'):
            return commList

        #Loop to get all items
        for item in api_response['items']:
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
