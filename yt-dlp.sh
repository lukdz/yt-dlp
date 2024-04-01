#!/usr/bin/env sh
exec "${PYTHON:-python3}" -Werror -Xdev "$(dirname "$(realpath "$0")")/yt_dlp/__main__.py" "$@"


# ./yt-dlp.sh https://www.youtube.com/watch?v=mneAoOiHm0Y
# https://github.com/yt-dlp/yt-dlp/issues/8584