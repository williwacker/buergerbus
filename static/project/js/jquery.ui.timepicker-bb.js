/* German initialisation for the timepicker plugin */
/* Written by Lowie Hulzinga. */
jQuery(function($){
    $.timepicker.regional['de'] = {
                hourText: "Stunden",
                minuteText: "Minuten",
                amPmText: ["AM", "PM"],
                onHourShow: OnHourShowCallback,
         		dropdown: true,
                closeButtonText: "Beenden",
                nowButtonText: "Aktuelle Zeit",
                deselectButtonText: "Wischen" }
    $.timepicker.setDefaults($.timepicker.regional['de']);
});
function OnHourShowCallback(hour) {
    if ((hour < 8) || (hour >16) || (hour == 12)|| (hour == 13)) {
        return false; // not valid
    }
    return true; // valid
}