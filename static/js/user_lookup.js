function userFormatResult(person) {
    var markup = "<table class='psearch-result'><tr>";
    markup += "<td class='psearch-avatar'><img src='" + person.gravatar + "'/></td>"
    markup += "<td class='psearch-info'><div class='psearch-username'>"
    markup += "<a href='" + person.username + "'>" + person.username + "</a></div>";


    if (person.real_name !== undefined) {
        markup += "<div class='psearch-realname'>" + person.real_name + "</div>";
    }

    markup += "</td></tr></table>"
    return markup;
}

function userFormatSelection(person) {
    return person.username;
}
$(document).ready(function() {
    $("#search").select2({
        placeholder: "Search for a Udacian",
        minimumInputLength: 3,
        ajax: { // instead of writing the function to execute the request we use Select2's convenient helper
            url: "/search",
            dataType: 'jsonp',
            data: function (term, page) {
                return {
                    q: term, // search term
                    page_limit: 10,
                    apikey: "1234567890" // please do not use so this example keeps working
                };
            },
            results: function (data, page) { // parse the results into the format expected by Select2.
                // since we are using custom formatting functions we do not need to alter remote JSON data
                return {results: data.people};
            }
        },
        formatResult: userFormatResult, // omitted for brevity, see the source of this page
        formatSelection: userFormatSelection,  // omitted for brevity, see the source of this page
        dropdownCssClass: "bigdrop" // apply css that makes the dropdown taller
    });
});