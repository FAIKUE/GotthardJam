# -*- coding: utf-8 -*-

import twitter
import re
import yaml

from datetime import datetime
from direction import Direction
from config import Config

TWEET_THRESHOLD_HOURS = 4


class GotthardJam(object):
    def __init__(self, api_config_path):
        api_config = Config(api_config_path)
        api_consumer_key = api_config.get_value("consumer_key")
        api_consumer_secret = api_config.get_value("consumer_secret")
        api_access_token_key = api_config.get_value("access_token_key")
        api_access_token_secret = api_config.get_value("access_token_secret")
        self.api = twitter.Api(api_consumer_key, api_consumer_secret, api_access_token_key, api_access_token_secret, tweet_mode="extended")

    def get_gotthard_jam(self, config_path):
        gotthard_tweets = self.api.GetUserTimeline(screen_name="TCSGotthard", count=10, exclude_replies=True)
        config = Config(config_path)

        south_jam = {}
        north_jam = {}
        closed_info = {}
        general_info = []

        for tweet in gotthard_tweets:
            if north_jam or south_jam or closed_info:
                break

            # tcs uses -> Instead of the word "Richtung", this changes that.
            tweet.full_text = tweet.full_text.replace("-&gt;", "Richtung")
            tweet.time = datetime.strptime(tweet.created_at, "%a %b %d %H:%M:%S %z %Y")
            tweet.age_minutes = GotthardJam._get_tweet_age_minutes(tweet.time)
            # If tweet is older than a few hours, it's probably outdated
            if tweet.age_minutes > TWEET_THRESHOLD_HOURS * 60:
                continue

            # jam tweet
            jam_match = re.match(config.get_value("tweet_jam_regex"), tweet.full_text)
            if jam_match is not None:
                direction = Direction.get_direction_from_city(jam_match.groups()[0])
                if not south_jam and direction == Direction.south:
                    south_jam = GotthardJam._get_jam_from_tweet_match(tweet, jam_match, direction)
                elif not north_jam and direction == Direction.north:
                    north_jam = GotthardJam._get_jam_from_tweet_match(tweet, jam_match, direction)
                continue

            # closed tweet
            closed_match = re.match(config.get_value("tweet_closed_regex"), tweet.full_text)
            if closed_match is not None:
                # with direction
                city = closed_match.groups()[1]
                if city is not None:
                    direction = Direction.get_direction_from_city(closed_match.groups()[0])
                    if direction == Direction.south:
                        south_jam["closed"] = {}
                        south_jam["closed"]["text"] = closed_match.groups()[2]
                        south_jam["age_minutes"] = tweet.age_minutes
                    else:
                        north_jam["closed"] = {}
                        north_jam["closed"]["text"] = closed_match.groups()[2]
                        north_jam["age_minutes"] = tweet.age_minutes
                else:
                    closed_info["text"] = closed_match.groups()[2]
                    closed_info["age_minutes"] = tweet.age_minutes
                continue
            # info tweet
            info_match = re.match(config.get_value("tweet_info_regex"), tweet.full_text)
            if info_match is not None and len(info_match.groups()) > 0:
                general_info.append({"text": info_match.groups()[0], "age_minutes": tweet.age_minutes})

        total_jam_minutes = 0
        if south_jam and "waiting_time_minutes" in south_jam:
            total_jam_minutes = int(south_jam["waiting_time_minutes"])
        if north_jam and "waiting_time_minutes" in north_jam:
            total_jam_minutes += int(north_jam["waiting_time_minutes"])

        # Choose css class for colorization based on traffic minutes.
        if total_jam_minutes >= 30 or closed_info or "closed" in north_jam or "closed" in south_jam:
            body_css_class = "much-jam"
        elif total_jam_minutes >= 10:
            body_css_class = "little-jam"
        else:
            body_css_class = "no-jam"

        return {
            "north": north_jam,
            "south": south_jam,
            "closed": closed_info,
            "general_info": general_info,
            "body_class": body_css_class
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
        return (datetime.utcnow() - tweet_time).total_seconds()/60

