// Global toggle for the icon
let ENABLED = true

chrome.browserAction.onClicked.addListener((tab) => {
  ENABLED = !ENABLED
  if (ENABLED)
    chrome.browserAction.setIcon({path: "icons/on.png", tabId:tab.id})
  else
    chrome.browserAction.setIcon({path: "icons/off.png", tabId:tab.id})
})

// And the intercept for the subtitles requests
chrome.webRequest.onBeforeRequest.addListener(
  (req) => {
    if (req.url.endsWith('.vtt') && ENABLED) {
      let filename = 'subs/' + req.url.split(/(\\|\/)/g).pop()
      return {redirectUrl: chrome.runtime.getURL(filename)}
    }
  },
  {
    urls: ["*://undertekst.nrk.no/*"]
  },
  ["blocking"]
)
