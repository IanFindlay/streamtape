# Streamtape

## Name a channel, set a time and let Streamtape take over.

Future development may make Streamtape a bit more substantial, but for now here's why you might like to wrap some Streamtape around your [Streamlink](https://github.com/streamlink/streamlink):

* No lost sleep - Recording starts at a specified time 
* No wasted energy - Option to automatically shutdown the computer once the stream ends
* No half streams - Set a reconnect time and nothing will be missed should the stream drop before then

### Usage Instructions

To use Streamtape simply download this repository, [install Streamlink](https://streamlink.github.io/install.html) and run the file with two positional arguments:  

* The name of the Twitch channel to record from
* Local time to start recording formatted HH:MM

Further Streamtape features can be accessed through the use of these optional command line arguments:

* -f FILENAME: Name to save recording as
*  -r RECONNECT: Attempt to reconnect and record stream if it disconnects before this time (HH:MM)
*  -s: Shutdown computer when stream finishes

For example:
```
python3 streamtape.py channel 03:00 -f my-download -r 07:00 -s
```
Will record the stream at twitch.tv/channel at 03:00 local time. Save the downloaded file as my-download.ts and attempt to reconnect to the stream if the connection drops anytime before 07:00.