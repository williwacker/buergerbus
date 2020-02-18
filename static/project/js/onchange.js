window.onload = function() {
    if (document.getElementById('changelist') != null) {
        var matches = document.getElementById('changelist').getElementsByClassName('select2-hidden-accessible');
        for (var i=0; i<matches.length; i++) {
            matches[i].setAttribute("onchange", "form.submit();");
        }
    }

    // add link for ort/add to ort select box
    if (document.getElementById('id_ort') != null  && document.getElementById('id_ort').tagName == 'SELECT') {
        var elem = document.getElementById('id_ort').parentElement.getElementsByTagName('p');
        elem[0].insertAdjacentHTML("beforebegin", 
            '<a id="add_id_ort" class="related-widget-wrapper-link add-related initialized" href="/Klienten/orte/add/?_to_field=id&_popup=1" title="Ort hinzufügen"><span class="related-widget-wrapper-icon"></span></a>');
    }

    // add link for strasse/add to strasse select box
    if (document.getElementById('id_strasse') != null  && document.getElementById('id_strasse').tagName == 'SELECT') {
        var elem = document.getElementById('id_strasse').parentElement.getElementsByTagName('p');
        elem[0].insertAdjacentHTML("beforebegin", 
            '<a id="add_id_strasse" class="related-widget-wrapper-link add-related initialized" href="/Klienten/strassen/add/?_to_field=id&_popup=1" title="Strasse hinzufügen"><span class="related-widget-wrapper-icon"></span></a>');
    }
    
    // add link for dienstleister/add to abholklient select box
    if (document.getElementById('id_abholklient') != null  && document.getElementById('id_abholklient').tagName == 'SELECT') {
        var elem = document.getElementById('id_abholklient').parentElement.getElementsByTagName('p');
        elem[0].insertAdjacentHTML("beforebegin", 
            '<a id="add_id_abholklient" class="related-widget-wrapper-link add-related initialized" href="/Klienten/dienstleister/add/?_to_field=id&_popup=1" title="Dienstleister hinzufügen"><span class="related-widget-wrapper-icon"></span></a>');
    }

    // add link for dienstleister/add to zielklient select box
    if (document.getElementById('id_zielklient') != null  && document.getElementById('id_zielklient').tagName == 'SELECT') {
        var elem = document.getElementById('id_zielklient').parentElement.getElementsByTagName('p');
        elem[0].insertAdjacentHTML("beforebegin", 
            '<a id="add_id_zielklient" class="related-widget-wrapper-link add-related initialized" href="/Klienten/dienstleister/add/?_to_field=id&_popup=1" title="Dienstleister hinzufügen"><span class="related-widget-wrapper-icon"></span></a>');
    }
}

window.onunload = function() {
    opener.location.reload(false);
}

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

function getUrlParam(parameter, defaultvalue) {
    var urlparameter = defaultvalue;
    if (window.location.href.indexOf(parameter) > -1) {
        urlparameter = getUrlVars()[parameter];
    }
    return urlparameter;
}