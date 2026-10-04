/**
 * AB2DETECT — Background Service Worker
 * Abubakar Khan (1RUA24CSE0010) · Abhishek D Nagoor (1RUA24CSE0009)
 */

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'open_popup') {
    chrome.action.openPopup();
  }
});

chrome.runtime.onInstalled.addListener(() => {
  console.log('AB2DETECT extension installed. Backend: http://localhost:8000');
});
