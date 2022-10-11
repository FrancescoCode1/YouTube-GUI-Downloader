# YouTube-GUI-Downloader
pyQt5 implementation of yt-dlp

__Make sure you have at least Python 3.10 as this code contains match case statements which have been added in version 3.10__

## Work in progress
This project is under development, bugs may occur. If you encounter any problems, please open an issue.

This YouTube Download Tool is based on yt-dlp and only works if yt-dlp is in the same directory or in PATH.

Current Issues:
- Progress Bar doesnt work on playlists, as the for loop only iterates through one link and increases the counter, but a playlist is technically only one link.
- Mp4 doesnt work

![YouTube_Downloader_v0 5_idkNk6aldf](https://user-images.githubusercontent.com/71893290/195176969-8f5cfeae-6759-49fe-884b-60cbaf7fc4c4.png)
