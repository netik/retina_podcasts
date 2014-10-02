#!/bin/bash

# --- Required variables ---

RSS_URI="/wg/wicked_grounds.rss"
MAIL_TO="jna@retina.net"
LOG_FILE="/opt/nginx/logs/access.log"

# Log that subscriber numbers will be written to. You will have to create one.
SUBSCRIBER_LOG="/var/log/podcast_stats"

# --- Optional customization ---

MAIL_SUBJECT="Podcast Subscriber Report"

# Locale for printf number formatting (e.g. "10000" => "10,000")
LANG=en_US

# Date format:
HUMAN_FDATE=`date +"%m-%d-%Y"`

# --- The actual log parsing ---
# Unique IPs requesting RSS, except those reporting "subscribers":
IPSUBS=`grep -F " $RSS_URI" $LOG_FILE | grep -vE '[0-9]+ subscribers' | grep -vE 'bot' | grep -vE 'iTMS' | grep -vE 'Pour-Over' | grep -vE 'Jakarta' | cut -d' ' -f 1 | sort | uniq | wc -l`

# Podcatchers:
INSTACAST_INDEX=`grep -F " $RSS_URI" $LOG_FILE | grep -E 'InstacastPushEpisodeIndexer' | cut -d' ' -f 1 | sort | uniq | wc -l`
ITUNES_INDEX=`grep -F " $RSS_URI" $LOG_FILE | grep -E 'iTMS' | cut -d' ' -f 1 | sort | uniq | wc -l`
INSTACAST=`grep -F " $RSS_URI" $LOG_FILE | grep -E 'Instacast/' | cut -d' ' -f 1 | sort | uniq | wc -l`
DOWNCAST=`grep -F " $RSS_URI" $LOG_FILE | grep -E 'Downcast/' | cut -d' ' -f 1 | sort | uniq | wc -l`
PODCASTS=`grep -F " $RSS_URI" $LOG_FILE | grep -E 'Podcasts/' | cut -d' ' -f 1 | sort | uniq | wc -l`

# Indexing conditionals:
if [ $INSTACAST_INDEX -eq 1 ]
then
	INSTACAST_DID_INDEX="Instacast is indexing the feed."
else
	INSTACAST_DID_INDEX="Instacast is NOT indexing the feed."
fi
if [ $ITUNES_INDEX -ge 1 ]
then
	ITUNES_DID_INDEX="iTunes is indexing the feed."
else
	ITUNES_DID_INDEX="iTunes is NOT indexing the feed."
fi

# --- Write Data ---
# Email Report
REPORT=$(
    printf "Feed stats for $HUMAN_FDATE:\n\n"
    printf "%'8d total subscribers\n\n" $IPSUBS
    printf "%'8d people using Instacast\n" $INSTACAST
    printf "%'8d people using Downcast\n" $DOWNCAST
    printf "%'8d people using Podcasts\n" $PODCASTS
    echo   "--------"
    printf "$INSTACAST_DID_INDEX\n"
    printf "$ITUNES_DID_INDEX"
)

# Set custom log format
TO_LOG=$(
	printf "$HUMAN_FDATE, $IPSUBS, $DOWNCAST, $INSTACAST, $PODCASTS\n"
)

# Log and email
echo "$REPORT"
echo ""
echo "Also emailed to $MAIL_TO."

echo "$REPORT " | mail -s "[$HUMAN_FDATE] $MAIL_SUBJECT" $MAIL_TO

# Write to custom log
echo $TO_LOG >> $SUBSCRIBER_LOG
