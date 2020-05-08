let MAIN_HOST = 'tv.nrk.no',
    SUBS_URLS = '*://undertekst.nrk.no/*.vtt'

let Id_To_Url = {}
let Downloads = new Set()

let Mode = {
  Frøya: {
    title: 'Frøya: English subtitles',
    icon: 'icons/Frøya.png',
    handle (url) {
      if (Downloads.has(url))
        return // don't block Varg

      let filename = 'subs/' + url.split(/(\\|\/)/g).pop()
      let local = chrome.runtime.getURL(filename)

      fetch(local).catch(() => Mode.Varg.handle(url))

      return {redirectUrl: local}
    },
  },
  Orm: {
    title: 'Orm: Norse subtitles',
    icon: 'icons/Orm.png',
    handle () {}
  },
  Varg: {
    title: 'Varg: Norse subtitles, downloads them',
    icon: 'icons/Varg.png',
    handle (url) {
      if (!Downloads.has(url)) {
        Downloads.add(url)
        chrome.downloads.download({url}, (id) => Id_To_Url[id] = url)
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
  if (delta.state?.current == 'complete') {
    Downloads.delete(Id_To_Url[delta.id])
    chrome.alarms.create({when: Date.now() + 2000})
  }
})

chrome.alarms.onAlarm.addListener(function() {
  chrome.tabs.reload()
});

// Intercept the subtitles requests, and let the active mode handle it.
chrome.webRequest.onBeforeRequest.addListener(
  (req) => activeMode().handle(req.url),
  {urls: [SUBS_URLS]},
  ['blocking']
)
