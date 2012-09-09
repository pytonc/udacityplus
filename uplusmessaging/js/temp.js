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