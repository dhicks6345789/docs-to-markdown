# Slideshow

Given a set of image/video/PDF/HTML files in a folder, produces an HTML file that cycles through each sub-page in turn, with defineable transition method (fade) and time.

This project consists of a Python script, intended to be run server-side, and a client-side web page component. The client-side web page can be used as a stand-alone component without the server-side script.

## Server-Side Python Script

The server-side Python script should be able to process most formats of image and video files into standardised versions suitible for showing via the web-based client. It replies on external applications (ffmpeg) to do that.

### Installation

The server-side script is part of the [Docs To Markdown](https://github.com/dhicks6345789/docs-to-markdown/tree/WebconsoleUpdate) project, and should be installed as part of that project.

### Usage

## Client-Side Slideshow Web Page

The client-side web page component is used by the server-side script, but can also be used as a self-contained, stand-alone slideshow application - as long as you can get your images, videos, etc into formats viewable by the browser you should be able to use it. The slideshow page should work on most modern web browsers, including browsers in kiosk mode as typically used for digital signage appliations. Client-side resources (i.e. RAM, disk space) used will depend on the content, but shouldn't be more than average.

### Installation

The web page component can simply be used as a single-page web application in your own projects - just download the "slideshowIndex.html" file. It is self-contained, any Javascript code or CSS styles are included in the one file.

### Usage

For stand-alone usage, download the "slideshowIndex.html" file. You are probably best off placing it in its own sub folder, along with the resource files you want to use (images, videos, PDF documents, HTML documents, etc), and renaming it "index.html" so your web server will see it as the default index file for that folder. Make sure resources are in formats that can be viewed by the web browser (see the server-side component above if you need a way of doing that).

You can modify the (by default) empty array defined at the start of the web page to contain a list of resources you want to load. Look for the line:

```
var resources = [];
```

and modify to be a list of your resources:

```
var resources = ["myImage.png", "myVideo.mp4", "myDocument.pdf"];
```

The slides will be loaded in the order defined in the array.

#### Parameters

The web page component accepts parameters passed in as part of the URL string.

transition seconds
fadesteps 5
fadeinterval seconds
clickRequired true false
refreshAt hours:min:sec
