var SERVER = "http://localhost:5050";
var active = false;
var current_url = "NONE";
var user_id = null;

chrome.browserAction.setIcon({path: "icon_38_bw.png"});
chrome.browserAction.setBadgeBackgroundColor({color: [255, 0, 0, 0]});

// take this out, it's for testing only:
chrome.storage.sync.clear();

function initUser () {
    console.log("initUser");
    chrome.storage.sync.get("user_id", function(data) {
        if (data['user_id'] != null) {
            user_id = data['user_id'];
            console.log("user_id is " + user_id);
        } else {
            console.log("getting new user id");
            $.post(SERVER, {'action': "new_user"}, function (data) {
                console.log(data);
                user_id = data;
                chrome.storage.sync.set({"user_id": data});
            });
        }
    });
}

function turnOn () {
    console.log("background.turnOn");  
    active = true;
    initUser();
    chrome.browserAction.setIcon({path: "icon_38_i.png"});
}

function turnOff () {
    console.log("background.turnOff");  
    active = false;
    chrome.browserAction.setIcon({path: "icon_38_bw.png"});
}

function checkUrl () {
    if (!active) return;
    console.log("background.checkUrl");  
    chrome.windows.getCurrent(function (window) {
        if (window == null || !window.focused) {
            console.log('(using other application)');
            current_url = 'NONE';
            postUrl();            
        } else {
            chrome.tabs.getSelected(null, function (tab) {
                if (tab != null) {
                    if (tab.url != current_url) {
                        if (tab.url.substr(0, 4) != "http") {
                            console.log("(settings page)");                            
                        } else {
                            current_url = tab.url;
                            postUrl();
                        }
                    } else {
                        console.log("(same url)");
                    }
                } else {
                    console.log("(no tabs)");
                }
            });                        
        }
    });    
}

function postUrl () {
    console.log("background.postUrl " + current_url);
    $.post(SERVER, {action: 'report', user_id: user_id, url: current_url}, function(data) {
        console.log("post result: " + data);
    }).fail(function () {
        console.log("post failed");
    });
}

chrome.tabs.onSelectionChanged.addListener(function (tab_id, select_info) {
    checkUrl();
});

chrome.tabs.onUpdated.addListener(function (tab_id, change_info, tab) {
    checkUrl();
});        

chrome.windows.onFocusChanged.addListener(function (window_id) {
    checkUrl();
});        

chrome.windows.onRemoved.addListener(function (window_id) {
    checkUrl();
});        