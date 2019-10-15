import twitter
import re
import yaml
import locale

from datetime import datetime
from direction import Direction


def _get_jam_from_tweet_match(tweet, match, direction):
    locale.setlocale(locale.LC_ALL, 'en_US')
    tweet_time = datetime.strptime(tweet.created_at, "%a %b %d %H:%M:%S %z %Y")
    print(tweet.text)
    jam_length_kilometers = match.groups()[1]
    waiting_time = match.groups()[2]
    waiting_time_unit = match.groups()[3]
    return (f"{tweet_time:%d.%m.%Y %H:%M}: {jam_length_kilometers} Kilometer Stau in Richtung {direction}. "
            f"Bis zu {waiting_time} {waiting_time_unit} Wartezeit.")


class GotthardJam(object):
    def __init__(self, api_config_path):
        with open(api_config_path, "r") as ymlfile:
            config = yaml.safe_load(ymlfile)
            api_consumer_key = config["consumer_key"]
            api_consumer_secret = config["consumer_secret"]
            api_access_token_key = config["access_token_key"]
            api_access_token_secret = config["access_token_secret"]
            self.api = twitter.Api(api_consumer_key, api_consumer_secret, api_access_token_key, api_access_token_secret)

    def get_gotthard_jam(self):
        gotthard_tweets = self.api.GetUserTimeline(screen_name="TCSGotthard", count=10, exclude_replies=True)
        south_jam = False
        north_jam = False

        for tweet in gotthard_tweets:
            match = re.match(r".*?- (.*?) -&gt; Gotthard.*?(\d*) km Stau.*?(\d*) (Stunden|Minuten)", tweet.text)
            if match is not None:
                direction = Direction.SOUTH if match.groups()[0] == "Luzern" else Direction.NORTH
                if south_jam is not True and direction == Direction.SOUTH:
                    south_jam = True
                    print(_get_jam_from_tweet_match(tweet, match, direction))
                elif north_jam is not True and direction == Direction.NORTH:
                    north_jam = True
                    print(_get_jam_from_tweet_match(tweet, match, direction))
