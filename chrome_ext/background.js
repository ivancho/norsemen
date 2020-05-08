let MAIN_HOST = 'tv.nrk.no',
    SUBS_URLS = '*://undertekst.nrk.no/*.vtt'

let Downloads = new Set()

let Mode = {
  Frøya: {
    title: 'Frøya: English subtitles',
    icon: 'icons/Frøya.png',
    handle (req) {
      let filename = 'subs/' + req.url.split(/(\\|\/)/g).pop()
      return {redirectUrl: chrome.runtime.getURL(filename)}
    }
  },
  Orm: {
    title: 'Orm: Norse subtitles',
    icon: 'icons/Orm.png',
    handle () {}
  },
  Varg: {
    title: 'Varg: Norse subtitles, downloads them',
    icon: 'icons/Varg.png',
    handle (req) {
      if (!Downloads.has(req.url)) {
        Downloads.add(req.url)
        chrome.downloads.download({url: req.url})
      }
    }
  }
}


let State = {'Mode': Object.keys(Mode)}
let activeMode = () => Mode[State.Mode[0]]
let rotateMode = () => State.Mode.push(State.Mode.shift())


// Update icon and tooltip to current active mode
let setIcon = (tabId) => {
  let m = activeMode()
  chrome.browserAction.setIcon({path: m.icon, tabId})
  chrome.browserAction.setTitle({title: m.title, tabId})
}


// Load saved mode
chrome.webNavigation.onCompleted.addListener((tab) => {
  chrome.storage.local.get(State, (item) => {
    State = item
    setIcon(tab.id)
  })
}, {url: [{hostEquals : MAIN_HOST}]})


// Rotate modes
chrome.browserAction.onClicked.addListener((tab) => {
  rotateMode()
  setIcon(tab.id)
  chrome.storage.local.set(State)
})


// Mark finished downloads
chrome.downloads.onChanged.addListener((delta) => {
  if (delta.state?.current != 'complete')
    return

  Downloads.remove(delta.url)
})


// Intercept the subtitles requests, and let the active mode handle it.
chrome.webRequest.onBeforeRequest.addListener(
  (req) => activeMode().handle(req),
  {urls: [SUBS_URLS]},
  ['blocking']
)
