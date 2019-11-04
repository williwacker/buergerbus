window.onload = function() {
    var matches = document.getElementsByClassName('select2-hidden-accessible');
    for (var i=0; i<matches.length; i++) {
        matches[i].setAttribute("onchange", "form.submit();");
    }
}