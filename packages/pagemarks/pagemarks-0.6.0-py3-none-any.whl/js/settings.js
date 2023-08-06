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

const PM_SETTINGS_APITOKEN = 'pagemarks-api-token';  /* name of the localStorage item for the api token */


function updateBodyClass(tokenPresent)
{
    const cl = document.body.classList;
    if (tokenPresent && !cl.contains('pm-token-present')) {
        cl.add('pm-token-present');
    }
    else if (!tokenPresent && cl.contains('pm-token-present')) {
        cl.remove('pm-token-present');
    }
}


function toggleRemoveButton(buttonEnabled)
{
    const cl = $('#settingsApiTokenModal div.modal-footer > button').first().prop('classList');
    if (buttonEnabled && cl.contains('disabled')) {
        cl.remove('disabled');
    }
    else if (!buttonEnabled && !cl.contains('disabled')) {
        cl.add('disabled');
    }
}


function updateApiTokenMenuItem(tokenPresent)
{
    const cl = $('#apiTokenMenuItem > i').last().prop('classList');
    if (tokenPresent) {
        cl.remove('bi-x');
        cl.remove('text-danger');
        cl.add('bi-check');
        cl.add('text-success');
    } else {
        cl.remove('bi-check');
        cl.remove('text-success');
        cl.add('bi-x');
        cl.add('text-danger');
    }
    cl.remove('invisible')
}


function isNotEmpty(token)
{
    return typeof(token) === 'string' && token.trim().length > 0;
}


/**
 * Update the input box status.
 * @param valid `true`: success, `false`: error, `undefined`: neutral
 */
function updateInputBoxStatus(valid)
{
    const inputBox = document.getElementById('apiTokenInput');
    const inputMsg = inputBox.nextSibling.nextSibling;   // jump over a text node
    const div = inputBox.parentElement;
    if (typeof(valid) !== 'boolean') {
        div.classList.remove('has-danger');
        div.classList.remove('has-success');
        inputBox.classList.remove('is-invalid');
        inputBox.classList.remove('is-valid');
        inputMsg.classList.remove('d-block');
        if (!inputMsg.classList.contains('d-none')) {
            inputMsg.classList.add('d-none');
        }
    }
    else if (valid) {
        div.classList.remove('has-danger');
        if (!div.classList.contains('has-success')) {
            div.classList.add('has-success');
        }
        inputBox.classList.remove('is-invalid');
        if (!inputBox.classList.contains('is-valid')) {
            inputBox.classList.add('is-valid');
        }
        inputMsg.classList.remove('d-block');
        if (!inputMsg.classList.contains('d-none')) {
            inputMsg.classList.add('d-none');
        }
    }
    else {
        div.classList.remove('has-success');
        if (!div.classList.contains('has-danger')) {
            div.classList.add('has-danger');
        }
        inputBox.classList.remove('is-valid');
        if (!inputBox.classList.contains('is-invalid')) {
            inputBox.classList.add('is-invalid');
        }
        inputMsg.classList.remove('d-none');
        if (!inputMsg.classList.contains('d-block')) {
            inputMsg.classList.add('d-block');
        }
    }
}


function toggleAlert(alertVisible)
{
    const cl = $('#apiTokenAlertRow').prop('classList');
    if (alertVisible) {
        cl.add('d-block');
        cl.remove('d-none');
    } else {
        cl.add('d-none');
        cl.remove('d-block');
    }
}


function modifyPage(tokenPresent, tokenValid)
{
    updateBodyClass(tokenValid);
    toggleRemoveButton(tokenPresent);
    updateApiTokenMenuItem(tokenValid);
    updateInputBoxStatus(tokenPresent ? tokenValid : undefined);
    if (tokenValid) {
        toggleAlert(false);
    }
}


function handleKeyPress(event)
{
    event.preventDefault();
    if (event.keyCode == 13 || event.which == 13) {
        // enter was pressed -> Okay button
        exports.saveToken();
    }
    else if (event.keyCode == 27 || event.which == 27) {
        // escape was pressed -> Cancel button
        exports.apiTokenCancel();
    }
    else {
        updateInputBoxStatus(undefined);
    }
}


function revealToken(revealed)
{
    if (revealed) {
        document.getElementById('apiTokenInput').type = 'text'
    } else {
        document.getElementById('apiTokenInput').type = 'password'
    }
}


function hideModal()
{
    $('#apiTokenInput').off('keyup');
    $('#settingsApiTokenModal').modal('hide');
}


function responseContainsApiScope(response)
{
    var result = false;
    if (Array.isArray(response)) {
        for (var i = 0; i < response.length; i++) {
            const scopes = response[i].scopes;
            if (Array.isArray(scopes) && scopes.indexOf('api') >= 0) {
                result = true;   // At least one of the user's tokens has the right scope. S'all we can do.
                break;
            }
        }
    }
    return result;
}


function validateToken(token, closeModal, validCallback)
{
    var settings = {
        'cache': false,
        'async': true,
        'crossDomain': true,
        'dataType': 'json',
        'url': exports.api_url + '/personal_access_tokens',
        'method': 'GET',
        'headers': {
            'Accept': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Private-Token': token.trim()
        }
    };

    $.ajax(settings)
        .done(function(response, textStatus, jqXHR) {
            const valid = textStatus === 'success' && responseContainsApiScope(response);
            modifyPage(true, valid);
            if (valid) {
                if (validCallback) {
                    validCallback();
                }
                if (closeModal) {
                    hideModal();
                }
            } else {
                console.log(textStatus);
                console.log(response);
                if (!closeModal) {
                    toggleAlert(true);  // This is the 'init page' use case.
                }
            }
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus);
            console.log(errorThrown);
            modifyPage(true, false);
            if (!closeModal) {
                toggleAlert(true);  // This is the 'init page' use case.
            }
        });
}


exports.apiTokenInitPage = function()
{
    const token = localStorage.getItem(PM_SETTINGS_APITOKEN);
    if (isNotEmpty(token)) {
        validateToken(token, false);
    } else {
        modifyPage(false, false);
    }
}


exports.apiTokenShowModal = function()
{
    document.getElementById('apiTokenReveal').checked = false;
    revealToken(false);
    const token = localStorage.getItem(PM_SETTINGS_APITOKEN);
    $('#apiTokenInput').val(typeof(token) === 'string' ? token.trim() : '');
    $('#apiTokenInput').keyup(handleKeyPress);
    $('#settingsApiTokenModal').modal('show');
}


exports.removeToken = function(askRUSure)
{
    if (!askRUSure || window.confirm('Really remove the token?')) {
        localStorage.removeItem(PM_SETTINGS_APITOKEN);
        modifyPage(false, false);
        hideModal();
    }
}


exports.saveToken = function()
{
    setTimeout(() => {
        // execute asynchronously so that we are guaranteed to get input field updates properly (think: bs, enter)
        const token = document.getElementById('apiTokenInput').value;
        if (isNotEmpty(token)) {
            validateToken(token, true,   // will hide the modal if token is valid
                () => localStorage.setItem(PM_SETTINGS_APITOKEN, token.trim()));
        } else {
            exports.removeToken(false);  // will hide the modal
        }
    }, 0);
}


exports.apiTokenCancel = function()
{
    exports.apiTokenInitPage();  // revalidate
    hideModal();
}


exports.apiTokenReveal = function()
{
    revealToken(document.getElementById('apiTokenReveal').checked);
}
