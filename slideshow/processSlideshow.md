# Slideshow

Given a set of image/video/PDF/HTML files in a folder, produces an HTML file that cycles through each sub-page in turn, with defineable transition method (fade) and time.

This project consists of a Python script, intended to be run server-side, and a client-side web page component:
- The server-side Python script should be able to process most formats of image and video files into standardised versions suitible for showing via the web-based client.
- The client-side web page component is used by the server-side script, but can also be used as a self-contained, stand-alone slideshow application - as long as you can get your images, videos, etc into formats viewable by the browser you should be able to use it. The slideshow page should work on most modern web browsers, including browsers in kiosk mode as typically used for digital signage appliations. Client-side resources (i.e. RAM, disk space) used will depend on the content, but shouldn't be more than average.

## Server-Side Python Script

## Client-Side Slideshow Web Page




                    location.replace(window.location.protocol + "//" + window.location.hostname + ":" + window.location.port + window.location.pathname.replace(/\/$/, "") + "?transition=" + (slideTransitionTime/1000) + "&fadesteps=" + (1/slideFadeStep) + "&fadeinterval=" + (slideFadeInterval/1000) + "&clickRequired=" + clickRequired.toString() + "&refreshAt=" + refreshAt[0] + ":" + refreshAt[1] + ":" + refreshAt[2]);
