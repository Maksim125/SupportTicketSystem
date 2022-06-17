/**
 * DELETE request to a ticket row.
 * @param {int} ticketID 
 */
function deleteTicket(ticketID) {
    fetch("/delete-ticket", {method : "DELETE", body : JSON.stringify({ ticketID: ticketID})}).then((_res) => {
        window.location = "/";
    });
}

/**
 * PATCH request: resolves ticket.
 *  1. POST new comment identifying resolver
 *  2. PATCH ticket to mark it as resolved.
 * @param {int} ticketID 
 * @param {int} userID 
 */
function resolveTicket(ticketID, userID) {
    postComment(userID, ticketID, true)
    fetch("/resolve-ticket", {method : "PATCH", body : JSON.stringify({ ticketID: ticketID})}).then((_res) => {
        document.location.reload(true);
    });
}

/**
 * Displays an individual ticket
 * @param {int} ticketID 
 */
function viewTicket(ticketID) {
    console.log(ticketID)
    window.location = "/view-ticket?id="+ticketID;
}

/**
 * DELETE request- remove a row from the user-group table
 * @param {int} userID 
 * @param {int} groupID 
 */
function kickFromGroup(userID, groupID) {
    fetch("/kick-user", {method : "DELETE", body : JSON.stringify({ userID: userID, groupID : groupID})}).then((_res) => {
        document.location.reload(true);
    });
}

/**
 * Send user a toast. Message is displayed, category determines color.
 * 
 * @param {str} message 
 * @param {str} category : 'error'-> red gradient, 'success'-> green gradient, all else -> blue gradient
 */
function flashToast(message, category) {
    let toast = Toastify({
        text: message,
        duration: 3000,
        newWindow: true,
        close: false,
        gravity: "top", // `top` or `bottom`
        position: "center", // `left`, `center` or `right`
        stopOnFocus: true, // Prevents dismissing of toast on hover
    })
    if (category == "error") {
        toast.options.style.background = "linear-gradient(to right, #A71D31, #3F0D12)";
        toast.showToast();
    }
    else if (category == "success") {
        toast.options.style.background = "linear-gradient(to right, #56ab2f, #a8e063)";
        toast.showToast();
    }
    else {
        toast.options.style.background = "linear-gradient(to right, #3a7bd5, #3737e0)";
        toast.showToast();
    }
}

/**
 * PATCH request- change this user's rank in this group
 * @param {int} userID 
 * @param {int} groupID 
 * @param {int} newRank 
 */
function rerankUser(userID, groupID, newRank){
    fetch("/rerank-user", {method : "PATCH", body : JSON.stringify({ userID: userID, groupID : groupID, newRank : newRank})}).then((_res) => {});
}

/**
 * DELETE request to leave group
 * @param {int} userID 
 * @param {int} groupID 
 */
function leaveGroup(userID, groupID) {
    //DELETE because leaving a group is the same as deleting an entry that relates a user to a group
    fetch("/leave-group", {method : "DELETE", body : JSON.stringify({ userID: userID, groupID : groupID})}).then((_res) => {
        document.location.reload(true);
    });
}

/**
 * POST new user-group entry tethering a user to a group
 * @param {int} userID 
 * @param {int} groupID 
 */
function joinGroup(userID, groupID) {
    //Post because joining a group creates a new entry that relates a user to a group
    fetch("/join-group", {method : "POST", body : JSON.stringify({ userID: userID, groupID : groupID})}).then((_res) => {
        document.location.reload(true);
    });
}

/**
 * POST new comment for a given ticket buy a given user
 * @param {int} userID 
 * @param {int} ticketID 
 * @param {boolean} resolving : if the comment should be a resolving request rather than the entry in the <text> tag
 */
function postComment(userID, ticketID, resolving = false) {
    newComment = document.getElementById("new-comment").value;
    if (newComment.length > 0 && !resolving) {
        fetch("/post-comment", {method : "POST", body : JSON.stringify({ userID : userID, ticketID: ticketID, commentContent : newComment})}).then((_res) => {
            document.location.reload(true);
        });
    }
    else if (resolving) {
        newComment = "I resolved this ticket"
        fetch("/post-comment", {method : "POST", body : JSON.stringify({ userID : userID, ticketID: ticketID, commentContent : newComment})}).then((_res) => {
            document.location.reload(true);
        });
    }
}

/**
 * DELETE the comment row.
 * @param {int} commentID 
 */
function deleteComment(commentID) {
    fetch("/delete-comment", {method : "DELETE", body : JSON.stringify({commentID : commentID})}).then((_res) => {
        document.location.reload(true);
    });
}

/**
 * Resize the given element to dynamically allocate the necessary space for all the text inside it.
 * @param {str} id 
 */
function resizeTextArea(id) {
    text_area = document.getElementById(id);
    text_area.style.height = ''; 
    text_area.style.height = text_area.scrollHeight +'px';
}

/**
 * Resizes all text area tags that exist in the document
 */
function resizeTextAreas() {
    let elements = document.getElementsByTagName("textarea");
    for (element of elements) {
        resizeTextArea(element.id)
    }
}

/**
 * Window resizing listener
 */
$(window).resize(function() {
    resizeTextAreas();
    
  });