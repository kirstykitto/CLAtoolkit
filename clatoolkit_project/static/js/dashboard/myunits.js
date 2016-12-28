
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
    attachGitHubLinkClickEventHandler();
});

function getGitHubAttachedRepo() {
    if($(".getReposList").length == 0) return;
    var courseId = $(".getReposList")[0].id;
    $("#reposList").html("Loading.....");
    $.ajax({
        url: "/dashboard/api/getGitHubAttachedRepo?course_id=" + courseId,
        type: 'GET',
        success: function (data) {
            if(data["result"] != "success") {
                // $("#get_repo_list").show();
                $("#reposList").hide();
                return;
            }
            var htmlStr = "<a target='_blank' href='" + data["url"] + "'><img class='repo_icon'>" + data["name"] + "</a>";
            htmlStr += " | <a href='#' onclick='javascript:removeAttachedRepo(\"" + courseId + "\");'>Remove</a>"

            $("#get_repo_list").hide();
            $("#reposList").html(htmlStr);
        }
    });
    attachGitHubLinkClickEventHandler();
}

function attachGitHubLinkClickEventHandler() {
    if($("#get_repo_list").length == 0) return;
    $("#get_repo_list").click(function() {
        $("#reposList").show();
        $("#reposList").html("Loading.....");
        $.ajax({
            url: "/dashboard/api/getAllRepos",
            type: 'GET',
            success: function (data) {
                createRepoList(data);
            }
        });
    });
}

function createRepoList(data) {
    var htmlStr = "";
    if(data["repos"].length == 0) {
        htmlStr = "No repositories found.";
        $("#reposList").html(htmlStr);
        return;
    }
    
    $.each(data["repos"], function(key, repo) {
        htmlStr += "<li><a href='#' onclick='javascript:addRepository(\"" + repo["name"] + "\");'>" + repo["name"] + "</a>";
        htmlStr += "&nbsp;&nbsp;<a target='_blank' href='" + repo["url"] + "'><img class='jump_to_repo'></a>";
        htmlStr += "&nbsp;&nbsp;- <span class='github_owner_span'>";
        htmlStr += "Owner: <a target='_blank' href='" + repo["owner"]["url"] + "'>" 
                +  "<img class='github_avatar' src='" + repo["owner"]["avatar_url"] + "'> "
                +   repo["owner"]["name"] + "</a>";
        htmlStr += "</span></li>";
    });
    htmlStr = "<ul class='repo_list'>" + htmlStr + "</ul>";
    htmlStr = '<p>Click a repository name to attach.</p>' + htmlStr;
    $("#reposList").html(htmlStr);
}

function addRepository(repoName) {
    var course_id = $(".getReposList")[0].id;
    $.ajax({
        url: "/dashboard/api/addRepoToCourse?repo=" + repoName + "&course_id=" + course_id,
        type: 'GET',
        success: function (data) {
            if(data["result"] == "success") {
                var htmlStr = "Repository successfully added to course - <a href='/dashboard/myunits/'>Reload</a>"
                $("#reposList").html(htmlStr);
                $("#get_repo_list").hide();
            } else {
                $("#reposList").html(data["message"]);
            }
        }
    });
}

function removeAttachedRepo(courseId) {
    $.ajax({
        url: "/dashboard/api/removeAttachedRepo?course_id=" + courseId,
        type: 'GET',
        success: function (data) {
            if(data["result"] == "success") {
                $("#reposList").hide();
                $("#get_repo_list").show();
            } else {
                $("#get_repo_list").hide();
                $("#reposList").html(data["message"]);
            }
        }
    });
}