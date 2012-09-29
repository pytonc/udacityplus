// Used by inbox/outbox - refactoring needed

function getPreviousMessages() {
    var url, from, to, m, temp;
    url = document.URL;
    if(url.search("from=") == -1) {
        url = url + "&from=10&to=20"; // default difference              
    } else {
        m = url.match(/(.+)from=(\d+)&to=(\d+)/);
        from = parseInt(m[2], 10);
        to = parseInt(m[3], 10);
        temp = to;
        to = 2 * to - from;
        from = temp;
        
        if(from >= 0 && to > 0 && to > from) {
            url = m[1] + "from=" + from + "&to=" + to;
        }
    }
    window.location.href = url
};

function getNewerMessages() {
    var url, from, to, m, temp;
    url = document.URL;
    m = url.match(/(.+)from=(\d+)&to=(\d+)/);
    from = parseInt(m[2], 10);
    to = parseInt(m[3], 10);
    temp = from;
    from = 2 * from - to;
    to = temp;

    if(from >= 0 && to > 0 && to > from) {
        url = m[1] + "from=" + from + "&to=" + to;
        window.location.href = url
    }
}


// Used on sign up page to validate username, email and password

function writeErrorMessage(id, message) {
    document.getElementById(id).innerHTML = message;
}

function validUsername(username) {
    var valid = true;

    if (username.length < 3) {
        writeErrorMessage("username_error", "Username has to be at least 3 characters long");
        valid = false;
    } else if (username.length > 15) {
        writeErrorMessage("username_error", "Username too long (15 characters max)");
        valid = false;
    } else {
        writeErrorMessage("username_error", "");
    }
    return valid;
}

function validEmail(email) {
    // regex from: http://stackoverflow.com/questions/2783672/email-validation-javascript
    var valid = true;

    if (!email.match("^[-0-9A-Za-z!#$%&'*+/=?^_`{|}~.]+@[-0-9A-Za-z!#$%&'*+/=?^_`{|}~.]+")) {
        writeErrorMessage("email_error", "Invalid email");
        valid = false;
    } else {
        writeErrorMessage("email_error", "");
    }
    return valid;
}

function validPassword(password) {
    var valid = true;

    if (password.length < 6) {
        writeErrorMessage("password_error", "Password has to be at least 6 characters long");
        valid = false;
    } else if (password.length > 40) {
        writeErrorMessage("password_error", "Password too long (40 characters max)");
        valid = false;      
    } else {
        writeErrorMessage("password_error", "");
    }
    return valid;
}

function validateSignUpForm() {
    var useraname = document.getElementById("username");
    var email = document.getElementById("email");
    var password = document.getElementById("password");

    var vUser = validUsername(username.value);
    var vEmail = validEmail(email.value);
    var vPass = validPassword(password.value);

    return vUser && vEmail && vPass;
}