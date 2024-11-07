#!/usr/bin/env bash

# jellyfin-find-duplicates script
# https://github.com/tremby/jellyfin-find-duplicates

function usage() {
	cat <<END
Usage: $(basename "$0") [-h] [--help]

Find duplicate TV show episodes in a Jellyfin library.

Information is output about any duplicate episodes found.
If the program exits with no output and a success status, no duplicates were
found.

Options:
  -h, --help: Show this help text

Configuration:
  The file \$XDG_CONFIG_HOME/jellyfin-find-duplicates.conf
  is sourced as a bash script if it exists.

  An example is distributed as jellyfin-find-duplicates.conf.example;
  it can be copied into place with
    cp jellyfin-find-duplicates.conf.example \$XDG_CONFIG_HOME/jellyfin-find-duplicates.conf
  and then edited.

  The following variables are then expected to exist:
    - JELLYFIN_HOST
      The Jellyfin URL scheme and hostname for the server, with no trailing
      slash. Example: "https://jellyfin.local"
    - JELLYFIN_TOKEN:
      The Jellyfin API token. Example: "abc123abc123"
    - JELLYFIN_USER:
      The name of the Jellyfin user to use as context. Example: "bob"
    - JELLYFIN_SHOWS_LIB_NAME:
      The name of the TV shows library in Jellyfin. Example: "Shows"
END
}

# Deal with any arguments
while [ $# -gt 0 ]; do
	case "$1" in
		"-h"|"--help")
			usage
			exit 0
			;;
		*)
			echo "Unexpected argument \"$1\"" >&2
			echo >&2
			usage >&2
			exit 65
	esac
	shift
done

# Ensure we have an XDG_CONFIG_HOME
if [ -z "$XDG_CONFIG_HOME" ]; then
	XDG_CONFIG_HOME="$HOME/.config"
fi

# Load config from a config file if it exists
if [ -f "$XDG_CONFIG_HOME/jellyfin-find-duplicates.conf" ]; then
	. "$XDG_CONFIG_HOME/jellyfin-find-duplicates.conf"
fi

# Ensure we have the configuration we need
if [ -z "$JELLYFIN_HOST" ]; then
	echo "JELLYFIN_HOST must be set" >&2
	exit 65
fi
if [ -z "$JELLYFIN_TOKEN" ]; then
	echo "JELLYFIN_TOKEN must be set" >&2
	exit 65
fi
if [ -z "$JELLYFIN_USER" ]; then
	echo "JELLYFIN_USER must be set" >&2
	exit 65
fi
if [ -z "$JELLYFIN_SHOWS_LIB_NAME" ]; then
	echo "JELLYFIN_SHOWS_LIB_NAME must be set" >&2
	exit 65
fi

# Ensure we have the binaries we need
if ! command -v curl &>/dev/null; then
	echo "Expected the binary \"curl\" to be available" >&2
	exit 69
fi
if ! command -v jq &>/dev/null; then
	echo "Expected the binary \"jq\" to be available" >&2
	exit 69
fi
if ! command -v date &>/dev/null; then
	echo "Expected the binary \"date\" to be available" >&2
	exit 69
fi

function req() {
	curl --silent --header "Accept: application/json" --header "Authorization: MediaBrowser Token=\"$JELLYFIN_TOKEN\"" "$JELLYFIN_HOST$1"
}

USER_ID=$(req /Users | jq --raw-output ".[] | select(.Name==\"$JELLYFIN_USER\") | .Id")
LIB_ID_1=$(req /Library/MediaFolders | jq --raw-output ".Items[] | select(.Name==\"$JELLYFIN_SHOWS_LIB_NAME\") | .Id")
#LIB_ID_2=$(req /Library/MediaFolders | jq --raw-output ".Items[] | select(.Name==\"$JELLYFIN_SHOWS_LIB_NAME_1\") | .Id")


SERIES_IDS_1=$(req "/Items?isSeries=true&userId=$USER_ID&parentId=$LIB_ID_1" | jq --raw-output '.Items[] | .Id')
#SERIES_IDS_2=$(req "/Items?isSeries=true&userId=$USER_ID&parentId=$LIB_ID_2" | jq --raw-output '.Items[] | .Id')

#SERIES_IDS="$SERIES_IDS_1 $SERIES_IDS_2"
SERIES_IDS="$SERIES_IDS_1"

for SERIES_ID in $SERIES_IDS; do
	echo "Vlherg"
	echo "$(req "/Shows/$SERIES_ID/Episodes?userId=$USER_ID&fields=SeriesName,Path" | jq --raw-output '.Items[0].SeriesName')"
	echo "$(req "/Shows/$SERIES_ID/Episodes?userId=$USER_ID&fields=SeriesName,Path" | jq  '.Items[0]')"
	echo "Vlherg"
	echo "$(req "/Shows/$SERIES_ID" | jq --raw-output '.SeriesName')"
	DUPLICATES_JSON="$(req "/Shows/$SERIES_ID/Episodes?userId=$USER_ID&fields=DateCreated,Path" | jq '.Items | group_by([.ParentIndexNumber, .IndexNumber]) | map(select(length > 1))')"
	if [ "$DUPLICATES_JSON" = "[]" ]; then
		continue
	fi
	SERIES_NAME="$(echo "$DUPLICATES_JSON" | jq --raw-output '.[0] | .[0].SeriesName')"
	echo "Series \"$SERIES_NAME\" has duplicates:"
	for DUPES_B64 in $(echo "$DUPLICATES_JSON" | jq --raw-output --compact-output '.[] | @base64'); do
		DUPES="$(echo "$DUPES_B64" | base64 --decode)"
		SEASON_NUM=$(echo "$DUPES" | jq --raw-output '.[0].ParentIndexNumber')
		EPISODE_NUM=$(echo "$DUPES" | jq --raw-output '.[0].IndexNumber')
		echo "  $SERIES_NAME S$(printf "%02d" "$SEASON_NUM")E$(printf "%02d" "$EPISODE_NUM")"
		for DUPE_B64 in $(echo "$DUPES" | jq --raw-output --compact-output 'sort_by(.DateCreated)[] | @base64'); do
			DUPE="$(echo "$DUPE_B64" | base64 --decode)"
			echo "  - $(date --iso=second --date="$(echo "$DUPE" | jq --raw-output '.DateCreated')"): $(echo "$DUPE" | jq --raw-output '.Path')"
		done
	done
done
