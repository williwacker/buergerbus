window.onload = function() {
    if (document.getElementById('changelist') != null) {
        var matches = document.getElementById('changelist').getElementsByClassName('select2-hidden-accessible');
        for (var i=0; i<matches.length; i++) {
            matches[i].setAttribute("onchange", "form.submit();");
        }
    }

    // make ...favorit and ...klient one line
    var float_list = [['id_abholfavorit',"form-row-left"],['id_abholklient',"form-row-right"],['id_zielfavorit',"form-row-left"],['id_zielklient',"form-row-right"],['id_bemerkung',"form-row-clear"]];
    set_float(float_list);

    // set on_change to abholfavorit
    if (document.getElementById('id_abholfavorit') != null) {
        var match = document.getElementById('id_abholfavorit');
        match.setAttribute("onchange", "set_abholklient();");
    }

    // set on_change to zielfavorit
    if (document.getElementById('id_zielfavorit') != null) {
        var match = document.getElementById('id_zielfavorit');
        match.setAttribute("onchange", "set_zielklient();")
    }
}

function set_float(float_list) {
    for (var i=0; i<float_list.length; i++) {
        if (document.getElementById(float_list[i][0]) != null) {
            var elem = document.getElementById(float_list[i][0])
            elem.parentElement.parentElement.className += ' '+float_list[i][1];
        }
    }
}

function set_abholklient() {
    var e = document.getElementById('id_abholfavorit');
    var sel1 = e.options[e.selectedIndex].value
    document.getElementById('id_abholklient').value = sel1;
    location.reload(false);    
}

function set_zielklient() {
    var e = document.getElementById('id_zielfavorit');
    var sel1 = e.options[e.selectedIndex].value
    document.getElementById('id_zielklient').value = sel1;
    location.reload(false);
}