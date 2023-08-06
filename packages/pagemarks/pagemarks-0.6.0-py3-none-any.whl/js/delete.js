/*
 * pagemarks - Free, git-backed, self-hosted bookmarks
 * Copyright (c) 2019-2021 the pagemarks contributors
 *
 * This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
 * License, version 3, as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with this program.
 * If not, see <https://www.gnu.org/licenses/gpl.html>.
 */

'use strict';


function is_demo()
{
    return typeof(exports.git_branch) === 'string' && exports.git_branch === '(demo)';
}


function git_write_access()
{
    const token = localStorage.getItem(PM_SETTINGS_APITOKEN);
    return typeof(exports.git_branch) === 'string'
        && !is_demo()
        && exports.gitlab_id > 0
        && document.body.classList.contains('pm-token-present')
        && typeof(token) === 'string';
}


function id2path(bookmarkId)
{
    return '%2F' + bookmarkId.replace('-', '%2F') + '%2Ejson';
}


function get_bookmark_url(bookmarkId)
{
    const jqElem = $('#' + bookmarkId + ' .card-body a').first();
    if (typeof(jqElem.attr('href')) === 'string') {
        return jqElem.attr('href');
    }
    return jqElem.attr('href-save');  /* if the bookmark has been deleted, and the link disabled */
}


function git_delete_bookmark(bookmarkId, successCallback, errorCallback)
{
    const token = localStorage.getItem(PM_SETTINGS_APITOKEN);
    const bookmark_url = get_bookmark_url(bookmarkId);
    const settings = {
        "async": true,
        "cache": false,
        "crossDomain": true,
        "url": exports.api_url + "/projects/" + exports.gitlab_id + "/repository/files/"
            + exports.collection_name + id2path(bookmarkId),
        "method": "DELETE",
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Private-Token": token
        },
        "processData": false,
        "data": JSON.stringify({
            "branch": exports.git_branch,
            "commit_message": "Remove " + bookmark_url + " [pagemarks]"
        })
    };

    $.ajax(settings)
        .done(function(response, textStatus, jqXHR) {
            console.log('git_delete_bookmark(): HTTP return code = ' + jqXHR.status);
            if (jqXHR.status === 204) {
                successCallback(bookmarkId, true);
            } else {
                console.log('ERROR: ' + jqXHR.status + ' ' + textStatus)
                errorCallback(bookmarkId, true);
            }
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            window.alert('Error ' + jqXHR.status + '\nBookmark removal failed.');
            errorCallback(bookmarkId, true);
        });
}


function git_fetch_bookmark(bookmarkId, successCallback, errorCallback)
{
    const token = localStorage.getItem(PM_SETTINGS_APITOKEN);
    const bookmark_url = get_bookmark_url(bookmarkId);
    const settings = {
        "async": true,
        "cache": false,
        "crossDomain": true,
        "url": exports.api_url + "/projects/" + exports.gitlab_id + "/repository/files/"
            + exports.collection_name + id2path(bookmarkId),
        "method": "GET",
        "headers": {
            "Accept": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache",
            "Private-Token": token
        },
        "processData": true,
        "data": {
            "ref": exports.git_branch
        }
    };

    $.ajax(settings)
        .done(function(response, textStatus, jqXHR) {
            console.log('git_fetch_bookmark(): HTTP return code = ' + jqXHR.status);
            if (jqXHR.status === 200 && response.encoding === 'base64') {
                successCallback(response.content);
            } else {
                console.log('ERROR: ' + jqXHR.status + ' / ' + response.encoding)
                errorCallback(bookmarkId, true);
            }
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            // TODO better alerting mechanism, e.g. with a banner at the top of the page
            window.alert('Error ' + jqXHR.status + '\nFailed to communicate with backend server.');
            errorCallback(bookmarkId, true);
        });
}


function git_create_bookmark(bookmarkId, base64Content, successCallback, errorCallback)
{
    const token = localStorage.getItem(PM_SETTINGS_APITOKEN);
    const bookmark_url = get_bookmark_url(bookmarkId);
    const settings = {
        "async": true,
        "cache": false,
        "crossDomain": true,
        "url": exports.api_url + "/projects/" + exports.gitlab_id + "/repository/files/"
            + exports.collection_name + id2path(bookmarkId),
        "method": "POST",
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Private-Token": token
        },
        "processData": false,
        "data": JSON.stringify({
            "branch": exports.git_branch,
            "encoding": "base64",
            "content": base64Content,
            "commit_message": "Undo removal of " + bookmark_url + " [pagemarks]"
        })
    };

    $.ajax(settings)
        .done(function(response, textStatus, jqXHR) {
            console.log('git_create_bookmark(): HTTP return code = ' + jqXHR.status);
            if (jqXHR.status === 201) {
                successCallback(bookmarkId, false);
            } else {
                console.log('ERROR: ' + jqXHR.status + ' ' + textStatus)
                errorCallback(bookmarkId, false);
            }
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            window.alert('Error ' + jqXHR.status + '\nFailed to communicate with backend server.');
            errorCallback(bookmarkId, false);
        });
}


function getThemeType() {
    var cl = document.body.classList;
    return cl.contains('pm-themetype-dark') ? 'dark' : 'light';
}


function removeClasses(classList, prefix)
{
    classList.remove.apply(classList, Array.from(classList).filter(v => v.startsWith(prefix)));
}


function renameAttribute(jqElem, attrNameOld, attrNameNew)
{
    const oldVal = jqElem.attr(attrNameOld);
    jqElem.attr(attrNameNew, oldVal);
    jqElem.removeAttr(attrNameOld);
}


function toggleUndoLink(bookmarkId, isDeleted)
{
    const cl = $('#' + bookmarkId + ' .card-toolbox a.pm-undo').prop('classList');
    if (isDeleted) {
        cl.remove('d-none');
    } else {
        cl.add('d-none');
    }
}


function toggleToolboxIcons(bookmarkId, isDeleted)
{
    $('#' + bookmarkId + ' .card-toolbox i').each(function() {
        const cl = $(this).prop('classList');
        if (isDeleted) {
            cl.add('d-none');
        } else {
            cl.remove('d-none');
        }
    });
}


function markCardDeleted(bookmarkId, isDeleted)
{
    var cl = $('#' + bookmarkId + ' .card').prop('classList');
    removeClasses(cl, 'border-');
    if (isDeleted) {
        cl.add('border-' + getThemeType());
        cl.add('pm-deleted');
    } else {
        cl.add('border-primary');
        cl.remove('pm-deleted');
    }

    if (!isDeleted) {
        toggleUndoLink(bookmarkId, false);
    } else {
        toggleToolboxIcons(bookmarkId, true);
    }

    $('#' + bookmarkId + ' .card-body a').each(function() {
        cl = $(this).prop('classList');
        if (isDeleted) {
            cl.add('disabled');
            renameAttribute($(this), 'href', 'href-save');
        } else {
            cl.remove('disabled');
            renameAttribute($(this), 'href-save', 'href');
        }
    });

    const toolbox = $('#' + bookmarkId + ' .card > .card-toolbox');
    if (isDeleted) {
        renameAttribute(toolbox, 'onclick', 'onclick-save');
    } else {
        /* Use small delay so that the click event does not immediately trigger a new deletion: */
        setTimeout(() => renameAttribute(toolbox, 'onclick-save', 'onclick'), 100);
    }
}


/**
 * Error handler for the remote calls. When a remote call fails, we must restore the card to its previous state.
 * @param bookmarkId the bookmark ID
 * @param isDeleted `true` if we were trying to delete the bookmark (we didn't, because it failed, but we tried),
 *          so `true` --> card should be normal, `false` --> card should be grayed out
 */
function errorHandler(bookmarkId, isDeleted)
{
    markCardDeleted(bookmarkId, !isDeleted);
    toggleUndoLink(bookmarkId, !isDeleted);
    toggleToolboxIcons(bookmarkId, !isDeleted);
}


exports.deleteBookmark = function(bookmarkId)
{
    const bookmark_url = get_bookmark_url(bookmarkId);
    if (is_demo()) {
        window.alert('This site is in demo mode, so real write operations are not enabled. 😊');
        markCardDeleted(bookmarkId, true);
        toggleUndoLink(bookmarkId, true);
        return false;
    }
    if (!git_write_access()) {    // TODO abstract these things into a remote gitlab api layer
        console.log('deleteBookmark(): Write access to the server is not enabled.\n' +
            'It shouldn\'t even have been possible to invoke this function ...');
        return false;
    }
    markCardDeleted(bookmarkId, true);
    git_fetch_bookmark(bookmarkId, function(original64) {
        $('#' + bookmarkId).attr('data-original64', original64);
        git_delete_bookmark(bookmarkId, toggleUndoLink, errorHandler);
    }, errorHandler);
}


exports.undoDeleteBookmark = function(bookmarkId)
{
    if (is_demo()) {
        window.alert('This site is in demo mode, so real write operations are not enabled. 😊');
        markCardDeleted(bookmarkId, false);
        toggleToolboxIcons(bookmarkId, false);
        return false;
    }
    if (!git_write_access()) {
        console.log('undoDeleteBookmark(): Write access to the server is not enabled.\n' +
            'It shouldn\'t even have been possible to invoke this function ...');
        return false;
    }
    markCardDeleted(bookmarkId, false);
    git_create_bookmark(bookmarkId, $('#' + bookmarkId).attr('data-original64'), toggleToolboxIcons, errorHandler);
}
