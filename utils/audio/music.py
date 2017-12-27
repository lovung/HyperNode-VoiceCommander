import sys
from os.path import join, dirname
#from transcribe_streaming_mic import speech2Text
import pyaudio
import time
import json 
import os.path
import logging
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import pafy

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
UTILS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/logger"))
    import logger as log
except ImportError:
    exit()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/JSON"))
    import json_utils
except ImportError:
    exit()

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyBtMTZyNPxawJLtGEmbR7Co_8h9cbSbOKE"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtubeSearch(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=options.q,
        part="id,snippet",
        maxResults=options.max_results
        ).execute()

    videosString = []
    videoIDs = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videosString.append("%s (%s)" % (search_result["snippet"]["title"],
                                         search_result["id"]["videoId"]))
            videoIDs.append(search_result["id"]["videoId"])

    print("Videos:\n", "\n".join(videosString), "\n")
    return videoIDs 

def youtubeLoadandPlay(videoID):
    print(videoID)
    url = "https://www.youtube.com/watch?v="+videoID
    print(url)
    video = pafy.new(url)
    audios = video.audiostreams
    #for a in audios:
        #print(a.bitrate, a.extension, a.get_filesize())
        #if a.extension is "m4a":
    bestAudio = video.getbestaudio()
    fileName = "yb_download."+bestAudio.extension
    bestAudio.download(filepath=fileName)
    print("Download success")
    os.system("cvlc " +fileName)

def MusicProcess(log_q, amqp_s_q, audio_q, cmd_q):
    logger = log.loggerInit(log_q)
    logger.log(logging.INFO, "Music proccess is started")

    while True:
        time.sleep(1)
        try:
            command = cmd_q.get_nowait()
            logger.log(logging.DEBUG, "Command: " + command)
            if json_utils.jsonSimpleParser(command, "des") == "music":
                pass
            


if __name__ == "__main__":
    argparser.add_argument("--q", help="Search term", default="Mashup Christmas & Happy New year")
    argparser.add_argument("--max-results", help="Max results", default=5)
    args = argparser.parse_args()

    try:
        videoIDs = youtubeSearch(args)
        youtubeLoadandPlay(videoIDs[0])
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
