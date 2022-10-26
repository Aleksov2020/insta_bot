var config = {
mode: "fixed_servers",
rules: {
singleProxy: {
scheme: "http",
host: "",
port: 53054
},
bypassList: [""]
}
};
chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
function callbackFn(details) {
return {
authCredentials: {
username: "YPHEg1BZ",
password: "AR8sZei7"
}
};
}

chrome.webRequest.onAuthRequired.addListener(
callbackFn,
{urls: ["<all_urls>"]},
['blocking']
);