# NVIDIA-SMI Reporter

This project reports statistics from the `nvidia-smi` command to a data consumer, which in turn alerts a bot.

Collected statistics are:

* The temperature of the GPU
* GPU Usage percent
* GPU Memory usage
* The processes that are using the GPU, and the memory they use - **Not supported on Windows due to an issue with** `nvidia-smi`


## How does it work?

This is made of three main components:

* The client, where the GPU resides
* The server, where the Telegram Bot and data collector reside
* The database (influxDB), where the metrics are stored

### The Client

The client polls nvidia-smi, parses the output to get the required metrics and sends them to the collector. This runs as a rudimentary CRON job running every 30 minutes, but will be updated to reflect an actual CRON job.

### The Server

The server contains the collector, queries the database every 30 minutes and retrieves data. Anything that crosses a certain threshold is considered anomalous and alerts the bot.

### The Database

Please use an [influxDB](https://www.influxdata.com/) instance. I am yet to find another time-series database that'll run on a Raspberry Pi.

## How do I get started?

1. Clone the repository.
2. Move the server and client code where needed.
3. Setup your database, and run `setup.py` in both the server and the client.
4. Create your Telegram bot and allow inline commands. [See here for more information](https://core.telegram.org/bots)
5. Setup an environment variable `NVIDIA_BOT_TOKEN` with the API key of your bot as its value.
6. Start the server at `listener.py` to listen for any metrics sent.
6. Once your bot is up and running, send a command `/hello` so that it registers your Telegram account.
7. Open `config.json` in your client and copy the `deviceid` variable. You'll need to register it to the bot in order to get updates.
8. Send `/link <<your deviceid>>` to the bot so that it links your device ID to the chat.
9. Run your client!

## How will you / can we improve this project?

* Time-Series Learning instead of a hardcoded value
* Inline documentation
* "Smarter" bot that analyzes trends and alerts better
* Better README?
* Better code structure
* Multi-GPU and multi-client support
* Better CRON
* Authentication for writing data points
* And many more...

## Where have you tested it?

* This project has been tested with the client running Linux Mint 19.2 and an nVidia GT-840M and the server being a Raspberry Pi 3 Model B+ running Raspbian Stretch.
* It also works with the server and bot running on Linux Mint 19.2 and client being a Windows 10 Machine with nVidia GTX-1660ti

## Oops! Something broke!

* Raise an issue! If you can fix it, make a PR! I'll gladly accept improvements!

## Ooh ooh I have an idea I want to implement in this project

* Build your feature and raise a PR by all means!