#!/bin/sh
# lists all problematic feeds found in r2e logfile for today's runs.
last_date=$(date +'%m-%d')
grep ^$last_date ${XDG_DATA_HOME:-$HOME/.local/share}/r2e/log | grep WARNING | grep http | sed 's/.*[ "]\(http:[^ "]*\).*/\1/' | sort | uniq
