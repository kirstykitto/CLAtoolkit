
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
});

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