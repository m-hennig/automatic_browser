var SERVER = "http://localhost:5050";
var active = false;
var current_url = "NONE";
var user_id = null;
var timeout = null;
var auto = false;

chrome.browserAction.setIcon({path: "icon_38_bw.png"});
chrome.browserAction.setBadgeBackgroundColor({color: [255, 0, 0, 0]});

// take this out, it's for testing only:
console.log("hello world");
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
    if (!active) {
        if (auto == true) auto = false;    
        return;
    }
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
                            console.log("(settings page, ignoring)");                            
                        } else {
                            current_url = tab.url;
                            postUrl();
                        }                        
                    } else {
                        console.log("(same url, ignoring)");
                        if (auto == true) auto = false;    
                    }
                } else {
                    console.log("(no tabs, ignoring)");
                }
            });                        
        }
    });    
}

function postUrl () {
    console.log("background.postUrl " + current_url);
    if (timeout != null) clearTimeout(timeout);    
    $.post(SERVER, {action: 'report', user_id: user_id, url: current_url, auto: auto}, function(data) {
        console.log("post result: " + data);
        if (data == "NOFUTURE") return;
        var parts = data.split(" ");
        var url = parts[0]
        var delay = parts[1]
        timeout = setTimeout(function () {
            chrome.tabs.getSelected(null, function (tab) {
                auto = true;
                if (url != current_url) {
                    chrome.tabs.update(tab.id, {url: url});
                } else {
                    if (auto == true) auto = false;                
                }
            });        
        }, delay);
    }).fail(function () {
        console.log("post failed");
    });
    if (auto == true) auto = false;
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