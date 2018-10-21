# Streamtape

## Name a channel, set a time and let Streamtape take over

Future development may make Streamtape a bit more substantial, but for now here's why you might like to wrap some Streamtape around your [Streamlink](https://github.com/streamlink/streamlink):

* No lost sleep - Recording starts at a specified time 
* No wasted energy - Option to automatically shutdown the computer once the stream ends
* No half streams - Set a reconnect time and nothing will be missed should the stream drop before then

### Usage Instructions

To use Streamtape simply download this repository, [install Streamlink](https://streamlink.github.io/install.html) and run the file with two positional arguments:  

* The name of the Twitch channel to record from
* Local, 24hr time to start recording formatted HH:MM

Further Streamtape features can be accessed through the use of these optional command line arguments:

* -q QUALITY: Override default recording quality in settings to a single value or a list of fallbacks e.g. '720p,480p,best'
* -f FILENAME: Name to save recording as
*  -r RECONNECT: Attempt to reconnect and record stream if it disconnects before this time (HH:MM)
*  -s: Shutdown computer when stream finishes

For example:
```
python3 streamtape.py channel 03:00 -q 480p -f my-download -r 07:00 -s
```
Will:
* Record the stream at twitch&#46;tv/channel at 03:00 local time  

* The downloaded file will be saved as my-download.ts and in 480p quality

* If the connection drops anytime before 07:00, Streamtape will continually attempt to reconnect to and download the stream. The new files will be named using the default channel-(timestamp).ts format

* Once the stream goes down after 07:00 and the download completes the computer will be shutdown

As seen, the -q argument allows you to override the default value set within the settings.ini file. This plaintext file contains the following values and can be edited at will in the text editor of your choice:

* Path: Defaults to a 'saved' folder within the same directory. Use an absolute path or one relative to the Streamtape directory to specify where to save your files and if there is no folder at that path one will be created

* The Connecting section has both a Wait (time to wait between each attempt to connect to the stream) and Attempt (how many attempts to make to connect) setting. The defaults result in trying to find a stream at the specified address every 30 seconds for up to 5 minutes

* The Recording section has both an Attempts (how many times to attempt to open the stream that has been successfully connected to and Quality (the quality of the stream to download) setting. The default values result in attempting to record the stream up to five times at the best available quality for that stream

The possible values of these settings (excluding Path) and further information about some of the other options that Streamtape uses can be found at the documentation for the [Streamlink CLI](https://streamlink.github.io/cli.html).