document.addEventListener("DOMContentLoaded", function(event) { 

    regExtrasFunctions.push(function(extras) {
        response = "";
        if (!Array.isArray(extras)) {
            return '';
        }
        extras.forEach(function (item, index) {
            if (item.type == "vaccine_lookup") {
                var text_class = "text-secondary";
                if (item.response.vaxStatus == "Approved") {
                    text_class = "text-success";
                }
                response += '<strong>DancerVax Status: <span class="' + text_class + '">';
                response += item.response.vaxStatus + '</span></strong><br />';
            }
        });
        return response;
    });
});
