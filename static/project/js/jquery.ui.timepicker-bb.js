/* German initialisation for the timepicker plugin */
/* Written by Lowie Hulzinga. */
jQuery(function($){
    $.timepicker.regional['de'] = {
                hourText: "Stunden",
                minuteText: "Minuten",
                onHourShow: OnHourShowCallback,
         		dropdown: true,
                closeButtonText: "Sichern",
                nowButtonText: "",
                deselectButtonText: "Wischen" }
    $.timepicker.setDefaults($.timepicker.regional['de']);
});
function OnHourShowCallback(hour) {
    if ((hour >= 8) & (hour < 12) || (hour >= 14) & (hour < 17)) {
        return true;
    }
    return false;
}