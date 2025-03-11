# m3uclean
[![Star on GitHub](https://img.shields.io/github/stars/samestrin/m3uclean?style=social)](https://github.com/samestrin/m3uclean/stargazers) [![Fork on GitHub](https://img.shields.io/github/forks/samestrin/m3uclean?style=social)](https://github.com/samestrin/m3uclean/network/members) [![Watch on GitHub](https://img.shields.io/github/watchers/samestrin/m3uclean?style=social)](https://github.com/samestrin/m3uclean/watchers)

![Version 1.0.0](https://img.shields.io/badge/Version-1.0.0-blue) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ](https://opensource.org/licenses/MIT)[![Built with Python](https://img.shields.io/badge/Built%20with-Python-green)](https://www.python.org/)

A robust tool designed to validate and clean M3U playlists by verifying each channel's stream availability and removing any entries with invalid streams.

## Features

* **Stream Validation**: Automatically checks each channel's stream availability
  * **Rate Limiting Protection**: Smart handling of rate limits with automatic backoff
  * **Slow Mode**: Conservative request rates for more reliable validation
* **Cleaning**: Cleans and corrects malformed entries
  * **Aggressive Cleaning**: Removes potentially dangerous characters completely
* **Duplicate Removal**: Identifies and removes duplicate channel entries
* **Logging**: Detailed logs of actions performed on the playlists
* **Docker Integration**: Packaged into a Docker container for easy deployment

## Installation

### Using pip

```bash
pip install m3uclean
```

### From source

```bash
git clone https://github.com/samestrin/m3uclean.git
cd m3uclean
pip install -e .
```
  
### Using Docker

```bash
docker pull samestrin/m3uclean
```

Or build the Docker image yourself:

```bash
git clone https://github.com/samestrin/m3uclean.git
cd m3uclean
docker build -t m3uclean .
```

## Usage

### Command Line

```bash
# Basic usage
m3uclean input.m3u -o output.m3u

# With stream validation
m3uclean input.m3u -o output.m3u -v

# With stream validation in slow mode (recommended for large playlists)
m3uclean input.m3u -o output.m3u -v --slow

# With aggressive cleaning
m3uclean input.m3u -o output.m3u -a

# With custom log file
m3uclean input.m3u -o output.m3u -l logfile.log

# Full options
m3uclean input.m3u -o output.m3u -l logfile.log -v -a --slow
```

### Using Docker

```bash
docker run -it --rm \
  -e INPUT_FILE="/var/tmp/m3u/playlist.m3u" \
  -e OUTPUT_FILE="/var/tmp/m3u/playlist_clean.m3u" \
  -e LOG_FILE="/var/tmp/m3u/m3uclean.log" \
  -e STREAM_VALIDATE="true" \
  -e AGGRESSIVE_CLEAN="true" \
  -v "/path/to/your/local/m3ufiles:/var/tmp/m3u" \
  m3uclean
```

## Environment Variables

When using Docker, you can configure the application using the following environment variables:

* `INPUT_FILE`: Path to the input M3U playlist file
* `OUTPUT_FILE`: Path to the output M3U playlist file
* `LOG_FILE`: Path to the log file
* `STREAM_VALIDATE`: Set to "true" to enable stream validation
* `AGGRESSIVE_CLEAN`: Set to "true" to enable aggressive cleaning

## Contribute

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Share

[![Twitter](https://img.shields.io/badge/X-Tweet-blue)](https://twitter.com/intent/tweet?text=Check%20out%20this%20awesome%20project!&url=https://github.com/samestrin/m3uclean) [![Facebook](https://img.shields.io/badge/Facebook-Share-blue)](https://www.facebook.com/sharer/sharer.php?u=https://github.com/samestrin/m3uclean) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Share-blue)](https://www.linkedin.com/sharing/share-offsite/?url=https://github.com/samestrin/m3uclean)