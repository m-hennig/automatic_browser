var background = chrome.extension.getBackgroundPage();  

function updateButton () {
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
    background.turnOn();
    background.status = "Enabled";
    updateButton();     
}

function turnOff () {   
    background.turnOff();
    background.status = "Disabled";    
    updateButton();
}        

function cancel () {
    window.close();
}

$(document).ready(function() {
    updateButton();
    $('#on_btn').click(turnOn);
    $('#off_btn').click(turnOff);
    $('#cancel_btn').click(cancel);
    $('#status').html(background.status);
});        