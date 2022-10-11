import urllib.request
import json
import urllib.parse as urlparse


def singleVideo(videoID):
    url_data = urlparse.urlparse(videoID)
    query = urlparse.parse_qs(url_data.query)
    video = query["v"][0]
    VideoID = video
    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % VideoID}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        print(data['title'])
        title = data['title']
        return title


def playlist(videoID):
    url_data = urlparse.urlparse(videoID)
    query = urlparse.parse_qs(url_data.query)
    video = query["list"][0]
    VideoID = video
    params = {"format": "json", "url": "https://www.youtube.com/playlist?list=%s" % VideoID}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        print(data['title'])
        title = data["title"]
        return title
