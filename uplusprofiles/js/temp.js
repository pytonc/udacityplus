// Used by inbox/outbox

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
        url = m[1] + "from=" + from + "&to=" + to;
    }
    window.location.href = url
};