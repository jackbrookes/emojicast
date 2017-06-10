import tweepy
import pyowm
import datetime
import time
import json

with open('settings_example.json') as settings_file:
    settings = json.load(settings_file)

class EmojiWeather():

    emojidict = {'clearnight': u'\U0001F303',
                 'clear': u'\u2600',
                 'rain': u'\U0001F327',
                 'sun': u'\u2600',
                 'clouds': u'\u2601',
                 'fog': u'\U0001F32B',
                 'haze': u'\u2601',
                 'mist': u'\u2601',
                 'snow': u'\U0001F328',
                 'tornado': u'\U0001F32A',
                 'storm': u'\U0001F329',
                 'hurricane': u'\U0001F300',}

    def __init__(self, weather):
        self.time = self.weather_to_datetime(weather)
        self.temperature = int(weather.get_temperature(unit='celsius')['temp'])
        self.status = self.augment_status(weather)
        self.emoji = self.emoji_from_status(self.status)
        self.extra = self.generate_extra(self.status, weather)

    def generate_extra(self, status, weather):
        if status == 'rain':
            rain_info = weather.get_rain()
            print(rain_info)

    def emoji_from_status(self, status):
        try:
            return self.emojidict[status]
        except KeyError:
            return status

    def augment_status(self, weather):
        status = weather._status.lower()
        sunset = self.time\
                 .replace(hour=19, minute=0, second=0, microsecond=0)
        if status == 'clear' and self.time > sunset:
            return status + "night"
        else:
            return status

    def weather_to_datetime(self, weather):
        unixtime = weather.get_reference_time()
        return datetime.datetime.fromtimestamp(unixtime)

    def __str__(self):
        timestr = self.time.strftime('%I%p')
        timestr = timestr if timestr[0] != '0' else timestr[1:]
        return u"{}: {}\u00B0C {}".format(timestr,
                                          self.temperature,
                                          self.emoji)



class Tweet():

    def __init__(self, location):
        self.weathers = []
        self.location = location

    def add_weather(self, weather):
        self.weathers.append(weather)

    def __str__(self):
        strweathers = [str(w) for w in self.weathers]

        header = "#EmojiCast for {}:\n".format(self.location)
        main = "\n".join(strweathers)

        return header + main


auth = tweepy.OAuthHandler(settings['consumer_key'], settings['consumer_secret'])
auth.set_access_token(settings['access_key'], settings['access_secret'])
api = tweepy.API(auth)
owm = pyowm.OWM(settings['owm_key'])

while 1:
    forecaster = owm.three_hours_forecast(settings['location'])
    tweet = Tweet(settings['location_name'])
    i = 0
    for w in forecaster.get_forecast():
        emojiweather = EmojiWeather(w)
        tweet.add_weather(emojiweather)
        i += 1
        if i >= 4:
            break
    print(tweet)
    try:
        1
        api.update_status(str(tweet))
    except tweepy.TweepError:
        print("Same forecast")
    time.sleep(60*60*3)
