---
title: Release build - 1.24b (2026-10-29)
subtitle: ''
source: Zen Browser releases
source_url: https://github.com/zen-browser/desktop/releases/tag/1.24b
author: mr-cheffy
date: '2026-10-29T21:29:46Z'
fetched: '2026-10-29T23:35:39Z'
image: ''
summary: Zen Stable Release Security • <https://www.mozilla.org/en-US/security/advisories/mfsa2026-118/> New Features • Updated to Firefox 159.0 • You can now import Spaces and Profiles from Arc and Dia. • Boosts gets a nice upgrade!
tags: []
guid: tag:github.com,2008:Repository/778556932/1.24b
---

## Zen Stable Release

### Security

- <https://www.mozilla.org/en-US/security/advisories/mfsa2026-118/>

### New Features

- Updated to Firefox 159.0
- You can now import Spaces and Profiles from Arc and Dia.
- Boosts gets a nice upgrade! THey can now be shared with others and they get an overall quality improvement.
- Holding 'ctrl' (or 'cmd' on macOS) while hovering over the new tab button will now give the option to 'Paste & Search'.
- You can now remove/add tabs from the library.
- An indicator will now show when a tab is not visible.

### Fixes

- Fixed an issue where expanded glance tabs would not appear on the right Space. ([#16080](https://github.com/zen-browser/desktop/issues/16080))
- Fixed the file upload dialog opening in the last folder a file was saved to, such as Downloads, instead of the folder last used for uploads.
- Fixed memory usage growing rapidly when sites such as the Zoom web app were left open in a minimized window.
- Fixed some videos displaying incorrectly on Windows when NVIDIA RTX Video HDR is enabled.
- Fixed bookmarks not being imported from Google Chrome profiles that are signed in to a Google account.
- Fixed the Replace button in Apple Writing Tools on macOS inserting the clipboard contents instead of the rewritten text on some sites.
- Fixed long drop-down lists on web pages sometimes showing blank space in place of the last options until the list was scrolled.
- Fixed some sites, such as Slack, failing to load instead of falling back to HTTP/2 when the site rejected an HTTP/3 request.
- Fixed Zen using excessive memory on Linux with AMD graphics when viewing map or place results on sites such as ChatGPT.
- Fixed quick gamepad button presses sometimes being missed in web games on macOS.
- Fixed tabs sometimes detaching into a new window when clicked on Linux with Wayland.
- Fixed menus and panels fading in on Windows and Linux when animation effects are turned off in the operating system.
- More bug fixes and improvements.

### Changes

- Zen's keyboard shortcuts have been improved and moved to about:keyboard.
- Space Routing settings have been moved to the Library
- On the site center, the reader mode button has been moved next to the 'Secure' button and shown only if available.
- Web addresses written in the Javanese, Balinese, Canadian Aboriginal Syllabics, and N'Ko scripts are now displayed in their own script instead of as encoded "xn--" text.
