/**
 * AB2DETECT — Content Script
 * Injects a floating "Detect" button on pages with AI-generated text.
 * Abubakar Khan (1RUA24CSE0010) · Abhishek D Nagoor (1RUA24CSE0009)
 */

(function () {
  'use strict';

  // Only inject on known AI chat pages
  const AI_DOMAINS = ['chat.openai.com', 'claude.ai', 'gemini.google.com', 'bard.google.com'];
  if (!AI_DOMAINS.some(d => location.hostname.includes(d))) return;

  const btn = document.createElement('button');
  btn.id = 'ab2detect-float';
  btn.textContent = 'AB2';
  btn.title = 'Detect hallucinations with AB2DETECT';
  btn.style.cssText = `
    position: fixed; bottom: 80px; right: 20px; z-index: 99999;
    width: 44px; height: 44px; border-radius: 50%;
    background: #5B5FEF; color: #fff;
    border: none; cursor: pointer;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; font-weight: 600;
    box-shadow: 0 2px 12px rgba(91,95,239,0.4);
    transition: transform 0.15s, opacity 0.15s;
    display: flex; align-items: center; justify-content: center;
  `;

  btn.addEventListener('mouseenter', () => { btn.style.transform = 'scale(1.1)'; });
  btn.addEventListener('mouseleave', () => { btn.style.transform = 'scale(1)'; });
  btn.addEventListener('click', () => {
    // Open extension popup via chrome.runtime message
    chrome.runtime.sendMessage({ action: 'open_popup' });
  });

  document.body.appendChild(btn);
})();
