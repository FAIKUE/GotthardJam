# -*- coding: utf-8 -*-

import twitter
import re
import yaml

from datetime import datetime
from direction import Direction

TWEET_THRESHOLD_HOURS = 4


class GotthardJam(object):
    def __init__(self, api_config_path):
        with open(api_config_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            api_consumer_key = config["consumer_key"]
            api_consumer_secret = config["consumer_secret"]
            api_access_token_key = config["access_token_key"]
            api_access_token_secret = config["access_token_secret"]
            self.api = twitter.Api(api_consumer_key, api_consumer_secret, api_access_token_key, api_access_token_secret, tweet_mode="extended")

    def get_gotthard_jam(self, config_path):
        gotthard_tweets = self.api.GetUserTimeline(screen_name="TCSGotthard", count=10, exclude_replies=True)
        south_jam = {}
        north_jam = {}
        general_info = []

        for tweet in gotthard_tweets:
            tweet.full_text = tweet.full_text.replace("-&gt;", "Richtung")
            tweet.time = datetime.strptime(tweet.created_at, "%a %b %d %H:%M:%S %z %Y")
            tweet.age_minutes = GotthardJam._get_tweet_age_minutes(tweet.time)
            # If tweet is older than a few hours, it's probably outdated
            if tweet.age_minutes > TWEET_THRESHOLD_HOURS * 60:
                continue

            # jam tweet
            with open(config_path, "r") as yaml_file:
                config = yaml.safe_load(yaml_file)
                jam_match = re.match(config["tweet_jam_regex"], tweet.full_text)
            if jam_match is not None:
                city = jam_match.groups()[0]
                direction = Direction.get_direction_from_city(city)
                if not south_jam and direction == Direction.south:
                    south_jam = GotthardJam._get_jam_from_tweet_match(tweet, jam_match, direction)
                elif not north_jam and direction == Direction.north:
                    north_jam = GotthardJam._get_jam_from_tweet_match(tweet, jam_match, direction)
            # info tweet
            with open(config_path, "r") as yaml_file:
                config = yaml.safe_load(yaml_file)
                info_match = re.match(config["tweet_info_regex"], tweet.full_text)
            if info_match is not None and len(info_match.groups()) > 0:

                general_info.append({"text": info_match.groups()[0], "age_minutes": tweet.age_minutes})

        total_jam_minutes = 0
        if south_jam:
            total_jam_minutes = int(south_jam["waiting_time_minutes"])
        if north_jam:
            total_jam_minutes += int(north_jam["waiting_time_minutes"])

        return {
            "north": north_jam,
            "south": south_jam,
            "general_info": general_info,
            "body_class": "no-jam" if total_jam_minutes <= 10 else ("little-jam" if total_jam_minutes <= 30 else "much-jam")
        }

    @staticmethod
    def _get_jam_from_tweet_match(tweet, match, direction):
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
            "time": tweet.time.strftime("%d.%m.%Y %H:%M"),
            "age_minutes": tweet.age_minutes,
            "length_kilometers": jam_length_kilometers,
            "direction": str(direction),
            "waiting_time_minutes": waiting_time_minutes,
            "waiting_time_hours": waiting_time_hours
        }
        return jam

    @staticmethod
    def _get_tweet_age_minutes(tweet_time):
        tweet_time = tweet_time.replace(tzinfo=None)
        return (datetime.now() - tweet_time).total_seconds()/60

