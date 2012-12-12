function setMaxLength() {
    $("#short_description").each(function(i){
        intMax = $(this).attr("maxlength");
        $(this).after("<div><span id='"+this.id+"Counter'>"+intMax+"</span> remaining</div>");
    });
}

function checkMaxLength(strID) {
    intCount = $("#"+strID).val().length;
    intMax = $("#"+strID).attr("maxlength");
    strID = "#"+strID+"Counter";
    $(strID).text(parseInt(intMax) - parseInt(intCount));
    if (intCount < (intMax * .8)) {$(strID).css("color", "#006600"); } //Good
    if (intCount > (intMax * .8)) { $(strID).css("color", "#FF9933"); } //Warning at 80%
    if (intCount > (intMax)) { $(strID).text(0).css("color", "#990000"); } //Over
}

function redirectToUserHome(username) {
    window.location="/" + username;
}

function setCookie(c_name,c_value) {
    document.cookie=c_name + "=" + c_value;
}

function getCookie(c_name) {
    var i,x,y,ARRcookies=document.cookie.split(";");
    for (i=0;i<ARRcookies.length;i++) {
      x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
      y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
      x=x.replace(/^\s+|\s+$/g,"");
      if (x==c_name) {
        return y;
      }
    }
}

function removeSelectedProject(username, csrf_token) {
    var form = document.createElement('form');
    form.setAttribute('method', 'POST');
    form.setAttribute('action', '/' + username + '/project/delete');
    
    var hiddenField1 = document.createElement('input');
    hiddenField1.setAttribute('type', 'hidden');
    hiddenField1.setAttribute('name', '_csrf_token');
    hiddenField1.setAttribute('value', csrf_token);

    var hiddenField2 = document.createElement('input');
    hiddenField2.setAttribute('type', 'hidden');
    hiddenField2.setAttribute('name', 'project_id');
    var e = document.getElementById('projects_dropdown');
    var pid = e.options[e.selectedIndex].value;
    hiddenField2.setAttribute('value', pid);

    form.appendChild(hiddenField1);
    form.appendChild(hiddenField2);

    document.body.appendChild(form);
    form.submit();
}

function loadSelectedProject(self, index) {
    var project_index = 0;
    if(index && index < self.length) {
        project_index = parseInt(index, 10);
        self.selectedIndex = project_index;
        $('#projects_dropdown').trigger('liszt:updated');
    } else {
        project_index = self.selectedIndex;
    }
     
    document.getElementById("title").value = js_title[project_index];
    document.getElementById("proj_url").value = js_url[project_index];
    document.getElementById("short_description").value = js_short_description[project_index];
    setCookie('sel_i', project_index.toString());
}