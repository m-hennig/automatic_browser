var SERVER = "http://automaticbrowser.com";
var verbose = false;
// var SERVER = "http://localhost:5050";
// var verbose = true;
var active = false;
var current_url = "NONE";
var user_id = null;
var user_key = null;
var timeout = null;
var auto = false;

if (verbose) {
    console.log("Automatic Browser");
}

chrome.browserAction.setIcon({path: {
        "19": "icon_19_disable.png",
        "38": "icon_38_disable.png"
    }
});
chrome.browserAction.setBadgeBackgroundColor({color: [255, 0, 0, 0]});
initUser();

function initUser () {
    if (verbose) console.log("initUser");
    chrome.storage.local.get(null, function(data) {
        if (data['user_id'] != null && data['user_key'] != null) {
            if (verbose) console.log("retrieved user id");
            user_id = data['user_id'];
            user_key = data['user_key'];
            if (verbose) console.log("user_id is " + user_id);
            if (verbose) console.log("user_key is " + user_key);
            if (data['active'] != null && data['active'] == true) {
                turnOn();
            }
        } else {
            if (verbose) console.log("getting new user id");
            $.post(SERVER, {'action': "new_user"}, function (data) {
                user_id = data;
                user_key = Math.random().toString(36).slice(2); // random 16-digit string
                if (verbose) console.log("user_id is " + user_id);
                if (verbose) console.log("user_key is " + user_key);
                chrome.storage.local.set({"user_id": user_id, "user_key": user_key}, function () {
                    turnOn();
                });
            });
        }
    });
}

function turnOn () {
    if (verbose) console.log("turnOn");  
    active = true;
    chrome.storage.local.set({"active": active});
    chrome.browserAction.setIcon({path: {
            "19": "icon_19.png",
            "38": "icon_38.png"
        }
    });    
}

function turnOff () {
    if (verbose) console.log("turnOff");  
    active = false;
    if (timeout != null) clearTimeout(timeout);    
    chrome.storage.local.set({"active": active});
    chrome.browserAction.setIcon({path: {
            "19": "icon_19_disable.png",
            "38": "icon_38_disable.png"
        }
    });
}

function checkUrl () {
    chrome.windows.getCurrent(function (window) {
        if (window == null || !window.focused) {
            if (verbose) console.log('(using other application)');
            current_url = 'NONE';
            postUrl();            
        } else {
            chrome.tabs.getSelected(null, function (tab) {
                if (tab != null) {
                    if (tab.url != current_url) {
                        if (tab.url.substr(0, 4) != "http") {
                            if (verbose) console.log("(settings page, ignoring)");                            
                        } else {
                            current_url = tab.url;
                            postUrl();
                        }                        
                    } else {
                        // console.log("(same url, ignoring)");
                        auto = false;    
                    }
                } else {
                    if (verbose) console.log("(no tabs, ignoring)");
                }
            });                        
        }
    });    
}

function postUrl () {
    if (verbose) console.log("postUrl " + current_url);
    if (timeout != null) clearTimeout(timeout);    
    if (current_url != 'NONE') {
        var parts = parseURL(current_url);
        var host = parts.hostname.replace("www.", "");
        var page = parts.pathname + parts.search + parts.hash;
        host = encrypt(host);
        page = encrypt(page);
    } else {
        var host = 'NONE';
        var page = 'NONE';
    }
    $.post(SERVER, {action: 'report', user_id: user_id, host: host, page: page, auto: auto, active: active}, function(data) {
        if (data == "NOFUTURE") {
            if (verbose) console.log("--> received NO FUTURE");
            return;
        }
        var parts = data.split(" ");
        var host = parts[0];
        var page = parts[1];
        var delay = parts[2];
        var url = host == "CLEAR" ? page : "http://" + decrypt(host) + (page == '/' ? '/' : decrypt(page));
        if (verbose) console.log("--> received future: " + url);
        timeout = setTimeout(function () {
            chrome.tabs.getSelected(null, function (tab) {
                auto = true;
                if (url != current_url) {
                    chrome.tabs.update(tab.id, {url: url});
                } else {
                    auto = false;                
                }
            });        
        }, delay);
    }).fail(function () {
        if (verbose) console.log("post failed");
    });
    auto = false;
}

function parseURL (url) {
    var parts = document.createElement('a');
    parts.href = url;
    return parts;
}

function encrypt (message) {
    /* deterministic encryption for server-side comparison, but key is client-side only and unique to user */
    // return message
    var encrypted = CryptoJS.AES.encrypt(message, CryptoJS.enc.Hex.parse(user_key), {iv: CryptoJS.enc.Hex.parse(user_key)});    
    var encoded = base32.encode("" + encrypted);
    return encoded;
}

function decrypt (encoded) {    
    // return encoded
    var decoded = base32.decode(encoded);    
    var decrypted = CryptoJS.AES.decrypt(decoded, CryptoJS.enc.Hex.parse(user_key), {iv: CryptoJS.enc.Hex.parse(user_key)});    
    var message = decrypted.toString(CryptoJS.enc.Utf8);
    return message;
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

chrome.browserAction.onClicked.addListener(function(tab) {
    if (active) {
        turnOff();
    } else {
        turnOn();
    }
});