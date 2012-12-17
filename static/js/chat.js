$(document).ready(function() {
    // Clear the chattextbox if it is clicked into and default text is in it
    $("#chatinput").focus(function(event) {
        if ($(this).hasClass("virgin-textinput")) {
            $(this).removeClass("virgin-textinput");
            $(this).val("");
        }
    });

    function chatScrollBottom() {
        var height = $("div#chatarea").outerHeight(); // Height of the div
        var totalheight = $("div#chatarea")[0].scrollHeight; // Total height of content
        var scrolltop = $("div#chatarea").scrollTop(); // Top of the scrolled part (varies by scrolling)
        /* When at the bottom, totalheight = height+scrolltop */
        return totalheight <= height+scrolltop;
        //return scrollheight == height;
    }


    var channels = { }; // Channels the user is in
    // Format: {"channelname": {
    // "text": text, "user": [user1, user2], "tab": jQueryTab
    // } }
    var users = { }; // Users the user is in communication with
    // Format: {"username": text}
    var activeEntity = server; // Could be #channel or @user

// Suite of test code:
    /*
     username = "Spez";
     server = "!Server";
     addChannel(server);
     onMessage({data:"PRIVMSG Jimmy Hi mate"});
     onMessage({data:"CHANNELMSG #randomChannel TestSender You've been randomly added to this channel to see if it works"});
     addChannel("#testChannel");
     onMessage({data:"USERS #testChannel Billy Jimmy ThisUserShouldBeGone Tommy"});
     onMessage({data:"CHANNELMSG #randomChannel TestSender You've been randomly added to this channel to see if it works"});
     onMessage({data:"CHANNELMSG #testChannel Jimmy Oh look, it's "+username});
     onMessage({data:"NOTICE Server had something to say to you"});
     onMessage({data:"JOINED NewUser #randomChannel"});
     onMessage({data:"JOINED Quitter #randomChannel"});
     onMessage({data:"JOINED Quitter #testChannel"});
     onMessage({data:"PRIVMSG Quitter I am going now, lol"});
     onMessage({data:"LEFT ThisUserShouldBeGone #testChannel"});
     onMessage({data:"PRIVMSG Paulo I AM AWESOME"});
     onMessage({data:"QUIT Quitter"});*/
// End test code

    // Opens a Google API Channel to receive messages from the server
    function openChannel() {
        //channel seems ambiguous here.maybe change a name?
        var channel = new goog.appengine.Channel(token);
        var handler = {
            "onopen": onOpen,
            "onmessage": onMessage,
            "onerror": onError,
            "onclose": onClose
        };
        var socket = channel.open(handler);
        socket.onopen = onOpen;
        socket.onmessage = onMessage;
        socket.onerror = onError;
        socket.onclose = onClose;
        //onMessage({data:"NOTICE token in openChannel "+token})
    }
    setTimeout(openChannel, 100);

    function onOpen() {
        if (!(server in channels)){
            addChannel(server);
        }
        onMessage({data: "NOTICE Connected to server"});
    }

    window.onbeforeunload = onExit;

    function onExit() {
        // If user leaves page, try to send a quit message
        // Just in case the /_ah/channel/disconnected/ page isn't hit
        sendMessage("QUIT");
    }

    function onMessage(message) {
        message = message.data;
        // Received a message from the server
        var command = message.split(' ')[0];
        var arg = message.substring(message.indexOf(' ')+1);
        switch(command) {
            case "PRIVMSG":
                // Message from another @user;recipient side
                // Format: PRIVMSG SENDER message text
                var sender = arg.split(' ')[0];
                // Retrieve the message
                arg = arg.substring(arg.indexOf(' ')+1);
                var content = createTimestamp()+" <"+sender+"> "+arg;
                addUserContent(sender, content);
                break;
            case "SENTMSG":
                // A message sent by this user (server confirmation or error message);sender side
                // Format: SENTMSG RECIPIENT message text
                var recipient = arg.split(' ')[0];
                arg = arg.substring(arg.indexOf(' ')+1);
                var content = createTimestamp()+" <"+username+"> "+arg;
                addUserContent(recipient, content);
                break;
            case "CHANNELMSG":
                // Message sent to a #channel which user is in
                // Format: CHANNELMSG CHANNEL SENDER message text
                var channel = arg.split(' ')[0];
                var sender = arg.split(' ')[1];
                // Retrieve the message
                arg = arg.substring(arg.indexOf(' ',
                    arg.indexOf(' ')+1)+1);
                var content = createTimestamp()+" <"+sender+"> "+arg;
                addChannelContent(channel, content);
                break;
            case "NOTICEINDENT":
                // Not sure if we want to support this, seems gimicky
                addChannelContent(server, createTimestamp()+"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"+arg, true);
                break;
            case "NOTICE":
                // Message from server
                // Format: NOTICE notice text
                addChannelContent(server, createTimestamp()+" "+arg);
                break;
            case "USERS":
                // Format: USERS channel username1 username2 username3
                var channel = arg.split(' ')[0];
                if (!(channel in channels)) {
                    addChannel(channel);
                }
                var usersInChannel = arg.substring(arg.indexOf(' ')+1).split(' ')
                for (var u in usersInChannel) {
                    addUsernameToChannel(usersInChannel[u], channel);
                }
                break;
            case "JOINED":
                // Format: JOINED username channel
                var u = arg.split(' ')[0];
                var channel = arg.split(' ')[1];
                addUsernameToChannel(u, channel);
                addChannelContent(channel, createTimestamp()+" "+u+" joined "+channel);
                break;
            case "LEAVE":
                // leave on local end
                // Format: LEAVE username channel
                var u = arg.split(' ')[0];
                var channel = arg.split(' ')[1];
                removeTab(channel);
                break;
            case "LEFT":
                // Format: LEFT username channel
                var u = arg.split(' ')[0];
                var channel = arg.split(' ')[1];
                removeUsernameFromChannel(u, channel);
                addChannelContent(channel, createTimestamp()+" "+u+" left");
                break;
            case "QUIT":
                // User QUIT chat, so remove from all channels
                // Format: QUIT username
                var u = arg.split(' ')[0];
                for (var c in channels) {
                    if (removeUsernameFromChannel(u, c)) {
                        addChannelContent(c, createTimestamp()+" "+u+" quit");
                    }
                }
                if (u in users) {
                    // Was talking to this user
                    addUserContent(u, createTimestamp()+" "+u+" quit");
                }
                break;
            case "ALIAS":
                // Format: ALIAS oldname newname
                // Not included during launch
                break;
            case "PING":
                // Format: PING response text
                sendMessage("PONG "+arg);
                break;
        }
    }
    function onError(error) {
        // Could be caused by a timeout after 120 minutes, try reconnecting
        onMessage({data: "NOTICE An error occurred with the server connection"});
        //when token expire
        if(error.code===401 && error.description==='Token+timed+out.'){
            $.post("/tokenexpireHandler?username="+username,function(data){
                token=data;
                openChannel();
            });
        }
    }
    function onClose() {
        // Could be caused by a timeout after 120 minutes, try reconnecting
        onMessage({data: "NOTICE Disconnected from server"});
    }

    // Sends messages to the server via XHR
    // Could potentially replace with jQuery's .ajax()
    function sendMessage(message) {
        message = encodeURIComponent(message); // Escape URI characters
        var path = "/communication?username="+username+"&identifier="+identifier+"&message="+message;
        var xhr = new XMLHttpRequest();
        xhr.open("POST", path, true);
        xhr.send();
    };

    // Return a string of the timestamp "YYYY/MM/DD HH:mm" - local time!
    function createTimestamp() {
        var d = new Date();
        var year = d.getFullYear().toString();
        var month = d.getMonth()+1;
        month = month < 10 ? "0"+month.toString() : month.toString();
        var day = d.getDate();
        day = day < 10 ? "0"+day.toString() : day.toString();
        var hour = d.getHours();
        hour = hour < 10 ? "0"+hour.toString() : hour.toString();
        var minute = d.getMinutes();
        minute = minute < 10? "0"+minute.toString() : minute.toString();
        return year+"/"+month+"/"+day+" "+hour+":"+minute;
    }

    // Adds a username to a channel that is being listened to
    function addUsernameToChannel(newUsername, channel) {
        if (!("users" in channels[channel])) {
            channels[channel]["users"] = [ ];
        }
        if (channels[channel]["users"].indexOf(newUsername) === -1) {
            channels[channel]["users"].push(newUsername);
            updateEntity(channel);
            return true;
        } else {
            return false;
        }
    }

    function removeUsernameFromChannel(removedUsername, channel) {
        if (channels[channel]["users"].indexOf(removedUsername) !== -1) {
            //may be someting get wrong in below statement
            channels[channel]["users"].splice(channels[channel]["users"].indexOf(removedUsername), 1);
            updateEntity(channel);
            return true;
        } else { return false; } // User is not in the channel
    }

    // Escape, markup and otherwise edit content
    // Customise this at will
    function markupContent(content, escape) {
        if (typeof(escape) === 'undefined' || escape === false) {
            // Escape HTML, by creating a jQuery element, inserting text, then pulling out HTML
            content = $("<div/>").text(content).html();
        }
        // Add newline at the end
        content += "<br/>";
        return content;
    }

    // Adds content to a channel tab
    function addChannelContent(channel, content, escape) {
        if (typeof(escape) === 'undefined')
            escape = false;
        content = markupContent(content, escape);
        if (!(channel in channels)) {
            // New Channel (that the user presumably joined)
            addChannel(channel)
        }
        channels[channel]["text"] += content;
        updateEntity(channel);
    }

    // Adds content to a user's tab
    function addUserContent(user, content) {
        content = markupContent(content);
        if (!(user in users)) {
            // New conversation with this user
            addUser(user);
        }
        users[user] += content;
        updateEntity(user);
    }

    // Add a channel to be listened to, adds tab as well
    function addChannel(channel) {
        // NB: Wipes history on leave/rejoin
        channels[channel] = {"text": "", "users": [username], "tab": addTab(channel)};
    }

    // Add a user for private conversation
    function addUser(newUsername) {
        /* users  = {"username": "chattext"} // No need for an array of users */
        users[newUsername] = "";
        addTab(newUsername);
    }

    // Add a tab
    function addTab(tabName) {
        var identifer = (tabName in users) ?
            tabName : tabName.substring(1)+".c"; // Trim leading # or ! and append trailing .
        var newTab = jQuery('<li id="'+identifer+'">'+
            '<a href="#'+identifer+'">'+tabName+'</a></li>');
        $("ul#chattabs").append(newTab);
        // Only go to tab if it is not a user message
        if (!(tabName in users)) {
            $("li", $("ul#chattabs")).removeClass("active");
            newTab.addClass("active");
            activeEntity = tabName;
            updateEntity(tabName);
        }
        // Handle click events for newtab
        newTab.click(function(event) {
            var clickedTab = $(this);
            event.preventDefault();
            // Inactivate currently active tab
            $("li", $("ul#chattabs")).removeClass("active");
            clickedTab.removeClass("highlighted");
            clickedTab.addClass("active");
            activeEntity = $("a", clickedTab).html();
            updateEntity(activeEntity);
        });
        return newTab;
    }

    //remove a Tab when user leave.?
    function removeTab(tabName){
        var identifer = (tabName in users) ?
            tabName : tabName.substring(1)+".c";
        //maybe this statement is better
        //$("ul#chattabs").remove('li[id="'+identifer+'"]')
        removedTab=$('li[id="'+identifer+'"]');
        previousTab=$($("li").get($("li").index(removedTab)-1));
        removedTab.remove();
        //go to previous Tab.
        previousTab.addClass("active");
        activeEntity=$("a",previousTab).html();
        updateEntity(activeEntity);
    }

    function updateEntity(updatedEntity) {
        //updatedEntity is a channelname or a username
        if (updatedEntity === activeEntity) {
            // Active entity was updated so update chat and users
            /* Technically, depending on message, only chat or users
             needs to be updated, but this is easier */
            // Scroll state
            var scrolledToBottom = chatScrollBottom();
            if (activeEntity in channels) {
                // activeEntity is a #channel
                $("div#chatarea").html(channels[activeEntity]["text"]);
                var userList = "Users in "+activeEntity+":";
                for (user in channels[activeEntity]["users"].sort()) {
                    userList += "<br/>"+channels[activeEntity]["users"][user];
                }
                $("div#userarea").html(userList);
            } else {
                // activeEntity is a @user
                $("div#chatarea").html(users[activeEntity]);
                var userlist = [activeEntity, username].sort().join("<br/>");
                $("div#userarea").html(userlist);
            }
            // Implement scrolling
            // If previously scrolled to bottom, then scroll to new content
            if (scrolledToBottom) {
                // Scroll to bottom of the div when getting
                $("div#chatarea").scrollTop($("div#chatarea")[0].scrollHeight);
                $("#spare").html(helpMessages());
            } else {
                // Don't scroll to allow user to continue reading
                $("#spare").html("Scroll down to read new messages.");
            }
        } else {
            // Inactive entity was updated, so make that tab flash/highlight
            if (updatedEntity in users) {
                // If it is a user, just add the class
                $("#"+updatedEntity).addClass("highlighted");
            } else {
                // If it is server or channel, it will be preceeded by ! or #
                // Luckily we can reference the tab directly
                $(channels[updatedEntity]["tab"]).addClass("highlighted");
            }
        }
    }

    // Client stuff
    $("#chatinput").keyup(function(event) {
        if(event.keyCode == 13 || event.which == 13){ // Enter is pressed
            var enteredText = $(this).val();
            $(this).val(""); // Clear the box
            if (enteredText.length <= 0) {
                // Do nothing
            } else if (enteredText.charAt(0) == "/") {
                // User entered a /COMMAND
                var command = enteredText.split(" ")[0].substring(1);
                var arg = enteredText.indexOf(" ") < 0 ? "":
                    enteredText.substring(enteredText.indexOf(" ")+1);
                slashCommand(command, arg);
            } else {
                if (activeEntity === server) {
                    // What do we do if someone talks to the server?

                } else if (activeEntity in channels) {
                    // Talk in channel
                    sendMessage("CHANNELMSG "+activeEntity+" "+enteredText);
                } else {
                    // Talking to a user
                    sendMessage("PRIVMSG "+activeEntity+" "+enteredText);
                }
            }
        }
    });
    // Have to use keydown for TAB, otherwise textbox loses focus
    $("#chatinput").keydown(function(event) {
        if(event.keyCode == 9 || event.which == 9){
            // Tab completion
        }
    });

    function slashCommand(command, arg){
        switch(command.toUpperCase()) {
            case "HELP":
                onMessage({data: "NOTICE The following commands are supported:"});
                onMessage({data: "NOTICE optional arguments are in square brackets: [channelname]"});
                onMessage({data: "NOTICE only arguments ending in ... can contain spaces: message..."});
                onMessage({data: "NOTICEINDENT /join channelname -- Joins the indicated channel"});
                onMessage({data: "NOTICEINDENT /msg recipient message... -- Sends a private message to the recipient, can also use /w"});
                onMessage({data: "NOTICEINDENT /leave [channelname] -- Leaves the indicated channel, or the current channel if channelname is blank"});
                onMessage({data: "NOTICEINDENT /quit -- End your chat session"});
                break;
            case "W":
            case "MSG":
                if (arg.length <= 0 || arg.indexOf(" ") < 0) {
                    // Either recipient or message is missing, or not properly space separated
                    onMessage({data: "NOTICE Correct format: /msg recipient message"});
                } else {
                    var recipient = arg.split(" ")[0];
                    var message = arg.substring(arg.indexOf(" ")+1);
                    sendMessage("PRIVMSG "+recipient+" "+message);
                }
                break;
            case "JOIN":
                if (arg.length <= 0) {
                    onMessage({data: "NOTICE Correct format: /join channelname"});
                } else {
                    sendMessage("JOIN "+arg.split(' ')[0]);
                }
                break;
            case "LEAVE":
                arg = arg.length <= 0 ? activeEntity : arg.split(" ")[0];
                if (arg in channels && arg !== server) {
                    sendMessage("LEAVE "+arg);
                    // Handle leave on local end!
                    onMessage({data : "NOTICE " + "you left " + arg});
                    //remove tab.
                    onMessage({data:"LEAVE "+username+" "+arg});
                    delete channels.arg;
                } else {
                    onMessage({data: "NOTICE "+arg+" is not a channel you can leave"});
                }
                break;
            case "QUIT":
                sendMessage("QUIT");
                break;
            default:
                onMessage({data: "NOTICE /"+command+" is not supported."});
        }
    }

    function helpMessages() {
        var messages = ["Try entering /help.", "Automatically scrolling to new messages."];
        return messages[Math.floor(Math.random() * messages.length)];
    }
});