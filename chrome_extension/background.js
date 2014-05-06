var SERVER = "http://localhost:5050";
var active = false;
var current_url = "NONE";
var user_id = null;
var key = null;
var timeout = null;
var auto = false;

chrome.browserAction.setIcon({path: "icon_19_disable.png"});
chrome.browserAction.setBadgeBackgroundColor({color: [255, 0, 0, 0]});

// take this out, it's for testing only:
console.log("hello world");
chrome.storage.sync.clear();

function initUser () {
    console.log("initUser");
    chrome.storage.sync.get("user_id", function(data) {
        if (data['user_id'] != null && data['key'] != null) {
            user_id = data['user_id'];
            key = data['key'];
            console.log("user_id is " + user_id);
            console.log("key is " + key);
        } else {
            console.log("getting new user id");
            $.post(SERVER, {'action': "new_user"}, function (data) {
                user_id = data;
                key = Math.random().toString(36).slice(2); // random 16-digit string
                chrome.storage.sync.set({"user_id": data});
                chrome.storage.sync.set({"key": key});
                console.log("user_id is " + user_id);
                console.log("key is " + key);
            });
        }
    });
}

function turnOn () {
    console.log("background.turnOn");  
    active = true;
    initUser();
    chrome.browserAction.setIcon({path: "icon_19.png"});
}

function turnOff () {
    console.log("background.turnOff");  
    active = false;
    if (timeout != null) clearTimeout(timeout);    
    chrome.browserAction.setIcon({path: "icon_19_disable.png"});
}

function checkUrl () {
    if (!active) {
        if (auto == true) auto = false;    
        return;
    }
    // console.log("background.checkUrl");  
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
                        // console.log("(same url, ignoring)");
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
    $.post(SERVER, {action: 'report', user_id: user_id, host: host, page: page, auto: auto}, function(data) {
        if (data == "NOFUTURE") {
            console.log("--> received NO FUTURE");
            return;
        }
        var parts = data.split(" ");
        var host = parts[0];
        var page = parts[1];
        var delay = parts[2];
        var url = "http://" + decrypt(host) + (page == '/' ? '/' : decrypt(page));
        console.log("--> received future: " + url);
        timeout = setTimeout(function () {
            chrome.tabs.getSelected(null, function (tab) {
                auto = true;
                console
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

function parseURL (url) {
    var parts = document.createElement('a');
    parts.href = url;
    return parts;
}

function encrypt (message) {
    /* deterministic encryption for server-side comparison, but key is client-side only and unique to user */
    // return message
    var encrypted = CryptoJS.AES.encrypt(message, CryptoJS.enc.Hex.parse(key), {iv: CryptoJS.enc.Hex.parse(key)});    
    var encoded = base32.encode("" + encrypted);
    return encoded;
}

function decrypt (encoded) {    
    // return encoded
    var decoded = base32.decode(encoded);    
    var decrypted = CryptoJS.AES.decrypt(decoded, CryptoJS.enc.Hex.parse(key), {iv: CryptoJS.enc.Hex.parse(key)});    
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

