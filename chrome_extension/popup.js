var background = chrome.extension.getBackgroundPage();  

function updateButton () {
    background.console.log("popup.updateButton " + background.active);
    $('#status').html(background.status);                 
    if (background.active) {
        $('#on_btn').hide();
        $('#off_btn').show();
    } else {
        $('#on_btn').show();
        $('#off_btn').hide();
    }
}
background.updateButton = updateButton;
        
function turnOn () {
    background.console.log("popup.turnOn");
    background.turnOn();
    background.status = "Enabled";
    updateButton();     
}

function turnOff () {   
    background.console.log("popup.turnOff");    
    background.turnOff();
    background.status = "Disabled";    
    updateButton();
}        

function cancel () {
    background.console.log("popup.cancel");    
    window.close();
}

$(document).ready(function() {
    updateButton();
    $('#on_btn').click(turnOn);
    $('#off_btn').click(turnOff);
    $('#cancel_btn').click(cancel);
    $('#status').html(background.status);
});        