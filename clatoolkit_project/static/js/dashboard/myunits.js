
function get_and_link_board(course_id) {
    $.ajax({
        url: "/dashboard/getBoards?course_id=" + course_id,
        type: 'GET',
        success: function (response) {
            document.getElementById('trello_board_display').innerHTML = response;
        }
    });
}
function add_board(course_id, id, platform) {
    $.ajax({
        url: "/dashboard/addboardtocourse?course_id=" + course_id + "&id=" + id,
        type: 'GET',
        success: function (response) {
            document.getElementById('trello_board_display').innerHTML = response;
        }
    });
}
$(document).ready(function (e) {
    var boards = document.getElementsByClassName("trello_board");
    // console.log(boards);
    for (var i = 0; i < boards.length; i++) {
        boards[i].innerHTML = "Loading Trello board...";
        $.ajax({
            url: "/dashboard/getAttachedBoard?course_id=" + boards[i].id,
            type: 'GET',
            success: function (resp) {
                resp_data = resp.data;
                resp_cc = resp.course_id;
                // console.log(resp_cc);
                document.getElementById(resp_cc).innerHTML = resp_data;
            }
        });
    }
    // Set click event on a link to attach a GitHub repository
    getGitHubAttachedRepo();
    // Slack
    getAttachedSlackTeam();
});

function getAttachedSlackTeam() {
    if($(".getSlackTeamList").length == 0) return;
    // Loop till all units' links are processed
    var courseIds = $(".getSlackTeamList");
    for(var i = 0; i < courseIds.length; i++) {

        var courseId = courseIds[i].id;
        var teamListName = "#teamList" + courseId;
        var slack_team_list = "#slack_team_list" + courseId;
        $(teamListName).html("Loading.....");
        $.ajax({
            url: "/dashboard/api/getAttachedSlackTeam?course_id=" + courseId,
            type: 'GET',
            success: function (data) {
                // Create html ID using course code sent included in the response data
                teamListName = "#teamList" + data["course_id"];
                slack_team_list = "#slack_team_list" + data["course_id"];

                if(data["result"] != "success") {
                    $(teamListName).hide();
                    return;
                }
                var htmlStr = "<a target='_blank' href='" + data["url"] + "'><img class='slack_icon'>" + data["name"] + "</a>";
                htmlStr += " | <a href='#' onclick='javascript:removeAttachedSlackTeam(\"" + data["course_id"] + "\");'>Remove</a>"

                $(slack_team_list).hide();
                $(teamListName).html(htmlStr);

            }
        });
        attachSlackTeamLinkClickEventHandler(courseId);
    }
}

function getGitHubAttachedRepo() {
    if($(".getReposList").length == 0) return;
    // Loop till all units' links are processed
    var courseIds = $(".getReposList");
    for(var i = 0; i < courseIds.length; i++) {

        var courseId = courseIds[i].id;
        var reposListName = "#reposList" + courseId;
        var get_repo_listName = "#get_repo_list" + courseId;
        $(reposListName).html("Loading.....");
        $.ajax({
            url: "/dashboard/api/getGitHubAttachedRepo?course_id=" + courseId,
            type: 'GET',
            success: function (data) {
                // Create html ID using course code sent included in the response data
                reposListName = "#reposList" + data["course_id"];
                get_repo_listName = "#get_repo_list" + data["course_id"];

                if(data["result"] != "success") {
                    // $("#get_repo_list").show();
                    $(reposListName).hide();
                    return;
                }
                var htmlStr = "<a target='_blank' href='" + data["url"] + "'><img class='repo_icon'>" + data["name"] + "</a>";
                htmlStr += " | <a href='#' onclick='javascript:removeAttachedRepo(\"" + data["course_id"] + "\");'>Remove</a>"

                $(get_repo_listName).hide();
                $(reposListName).html(htmlStr);
            }
        });
        attachGitHubLinkClickEventHandler(courseId);
    }
}

function attachSlackTeamLinkClickEventHandler(courseId) {
    var teamListName = "#teamList" + courseId;
    var slack_team_listName = "#slack_team_list" + courseId;

    if($(slack_team_listName).length == 0) return;
    // $.ajax({
    //     url: "/dashboard/api/getSlackTeamUrl?course_id=" + courseId,
    //     type: 'GET',
    //     success: function (data) {
    //         // Slack team url
    //         $('#slack_team_url').html('<a href="' + data["url"] + '">' + data["domain"] + '</a>')
    //     }
    // });

    $(slack_team_listName).click(function() {
        addSlackTeam(courseId);
    });
}

function attachGitHubLinkClickEventHandler(courseId) {
    var reposListName = "#reposList" + courseId;
    var get_repo_listName = "#get_repo_list" + courseId;

    if($(get_repo_listName).length == 0) return;
    $(get_repo_listName).click(function() {
        $(reposListName).show();
        $(reposListName).html("Loading.....");
        $.ajax({
            url: "/dashboard/api/getAllRepos?course_id=" + courseId,
            type: 'GET',
            success: function (data) {
                createRepoList(data);
            }
        });
    });
}

function createRepoList(data) {
    var htmlStr = "";
    var reposListName = "#reposList" + data["course_id"];
    if(data["repos"].length == 0) {
        htmlStr = "No repositories found.";
        $(reposListName).html(htmlStr);
        return;
    }
    
    $.each(data["repos"], function(key, repo) {
        htmlStr += "<li><a href='#' onclick='javascript:addRepository(\"" + repo["name"] + "\", \"" + data["course_id"] + "\");'>" + repo["name"] + "</a>";
        htmlStr += "&nbsp;&nbsp;<a target='_blank' href='" + repo["url"] + "'><img class='jump_to_repo'></a>";
        htmlStr += "&nbsp;&nbsp;- <span class='github_owner_span'>";
        htmlStr += "Owner: <a target='_blank' href='" + repo["owner"]["url"] + "'>" 
                +  "<img class='github_avatar' src='" + repo["owner"]["avatar_url"] + "'> "
                +   repo["owner"]["name"] + "</a>";
        htmlStr += "</span></li>";
    });
    htmlStr = "<ul class='repo_list'>" + htmlStr + "</ul>";
    htmlStr = '<p>Click a repository name to attach.</p>' + htmlStr;
    $(reposListName).html(htmlStr);
}

function addSlackTeam(courseId) {
    // var course_id = $(".getReposList")[0].id;
    var teamListName = "#teamList" + courseId;
    var slack_team_listName = "#slack_team_list" + courseId;
    
    $.ajax({
        url: "/dashboard/api/addSlackTeamToCourse?course_id=" + courseId,
        type: 'GET',
        success: function (data) {
            if(data["result"] == "success") {
                var htmlStr = "Team successfully added to course - <a href='/dashboard/myunits/'>Reload</a>"
                $(teamListName).html(htmlStr);
                $(slack_team_listName).hide();
            } else {
                $(teamListName).html(data["message"]);
            }
            $(teamListName).show();
        }
    });
}

function addRepository(repoName, courseId) {
    // var course_id = $(".getReposList")[0].id;
    var reposListName = "#reposList" + courseId;
    var get_repo_listName = "#get_repo_list" + courseId;
    
    $.ajax({
        url: "/dashboard/api/addRepoToCourse?repo=" + repoName + "&course_id=" + courseId,
        type: 'GET',
        success: function (data) {
            if(data["result"] == "success") {
                var htmlStr = "Repository successfully added to course - <a href='/dashboard/myunits/'>Reload</a>"
                $(reposListName).html(htmlStr);
                $(get_repo_listName).hide();
            } else {
                $(reposListName).html(data["message"]);
            }
        }
    });
}

function removeAttachedSlackTeam(courseId) {
    var reposListName = "#teamList" + courseId;
    var slack_team_listName = "#slack_team_list" + courseId;
    $.ajax({
        url: "/dashboard/api/removeAttachedSlackTeam?course_id=" + courseId,
        type: 'GET',
        success: function (data) {
            if(data["result"] == "success") {
                $(reposListName).hide();
                $(slack_team_listName).show();
            } else {
                $(slack_team_listName).hide();
                $(reposListName).html(data["message"]);
            }
        }
    });
}

function removeAttachedRepo(courseId) {
    var reposListName = "#reposList" + courseId;
    var get_repo_listName = "#get_repo_list" + courseId;
    $.ajax({
        url: "/dashboard/api/removeAttachedRepo?course_id=" + courseId,
        type: 'GET',
        success: function (data) {
            if(data["result"] == "success") {
                $(reposListName).hide();
                $(get_repo_listName).show();
            } else {
                $(get_repo_listName).hide();
                $(reposListName).html(data["message"]);
            }
        }
    });
}