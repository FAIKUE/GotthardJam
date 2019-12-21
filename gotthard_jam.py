# -*- coding: utf-8 -*-

import twitter
import re
import yaml

from datetime import datetime
from direction import Direction

TWEET_THRESHOLD_HOURS = 3


class GotthardJam(object):
    def __init__(self, api_config_path):
        with open(api_config_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            api_consumer_key = config["consumer_key"]
            api_consumer_secret = config["consumer_secret"]
            api_access_token_key = config["access_token_key"]
            api_access_token_secret = config["access_token_secret"]
            self.api = twitter.Api(api_consumer_key, api_consumer_secret, api_access_token_key, api_access_token_secret)

    def get_gotthard_jam(self):
        gotthard_tweets = self.api.GetUserTimeline(screen_name="TCSGotthard", count=10, exclude_replies=True)
        south_jam = {}
        north_jam = {}

        for tweet in gotthard_tweets:
            with open("config.yaml", "r") as yaml_file:
                config = yaml.safe_load(yaml_file)
                match = re.match(config["tweet_regex"], tweet.text)
            print(tweet.text)
            if match is not None:
                place = match.groups()[0]
                direction = Direction.south if place == "Luzern" else Direction.north
                if not south_jam and direction == Direction.south:
                    south_jam = GotthardJam._get_jam_from_tweet_match(tweet, match, direction)
                elif not north_jam and direction == Direction.north:
                    north_jam = GotthardJam._get_jam_from_tweet_match(tweet, match, direction)

        total_jam_minutes = 0
        if south_jam:
            total_jam_minutes = int(south_jam["waiting_time_minutes"])
        if north_jam:
            total_jam_minutes += int(north_jam["waiting_time_minutes"])

        return {
            "north": north_jam,
            "south": south_jam,
            "body_class": "no-jam" if total_jam_minutes <= 10 else ("little-jam" if total_jam_minutes <= 30 else "much-jam")
        }

    @staticmethod
    def _get_jam_from_tweet_match(tweet, match, direction):
        tweet_time = datetime.strptime(tweet.created_at, "%a %b %d %H:%M:%S %z %Y")
        # If tweet is older than 3 hours, it's probably outdated
        if (datetime.utcnow() - tweet_time.replace(tzinfo=None)).total_seconds() > TWEET_THRESHOLD_HOURS * 3600:
            return {}
        jam_length_kilometers = match.groups()[1]
        waiting_time = match.groups()[2]
        waiting_time_unit = match.groups()[3]

        if waiting_time_unit == "Minuten":
            waiting_time_hours = int(waiting_time) / 60
            waiting_time_minutes = waiting_time
        else:
            waiting_time_minutes = int(waiting_time) * 60
            waiting_time_hours = waiting_time

        jam = {
            "time": tweet_time.strftime("%d.%m.%Y %H:%M"),
            "length_kilometers": jam_length_kilometers,
            "direction": str(direction),
            "waiting_time_minutes": waiting_time_minutes,
            "waiting_time_hours": waiting_time_hours
        }
        return jam
