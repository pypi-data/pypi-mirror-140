import requests,pprint


class Weather:
    """Creates a weather object getting an apikey as input
    and either a city name or lat and lon coordinates.

    package use example:

    # Create a weather object using a city name:
    # The api key below is not guranteed to work.
    # Get your own apikey from https://openweather.org
    # And wait a couple of hours for the apikey to be activated

    >>> weather1 = Weather(apikey="a95a27c945074819e1f4ac78d53814ab", city="Madrid")

    # Using longitude and latitude coordinates
    >>> weather2 = Weather(apikey="a95a27c945074819e1f4ac78d53814ab", lat=41.1, lon=-4.1)

    # Get complete weather for the next 12 hours:
    >>> weather1.next_12h()

    # Get simplified weather data for the next 12 hours:
    >>> weather2.next_12h_simplified()

    """

    def __init__(self, apikey=None, city=None, lat=None, lon=None):

        self.type = "metric"

        if city:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={apikey}&units={self.type}"
            print(url)
            response = requests.get(url)
            self.data = response.json()
        elif lat and lon:
            url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={apikey}&units={self.type}"
            response = requests.get(url)
            self.data = response.json()
        else:
            raise TypeError("Enter either city or lat and lon as arguments")

        if self.data['cod'] != "200":
            raise ValueError(self.data['message'])

    def next_12h(self):
        """Returns 3 hour data for the next 12 hours as dict
        """
        return self.data['list'][:4]

    def next_12h_simplified(self):
        """Returns date, temperature and sky condition every 3 hours
        for the next 12 hours as a tuple of tuples
        """
        simple_data = []
        for dicty in self.data['list'][:4]:
            simple_data.append((dicty['dt_txt'], dicty['main']['temp'], dicty['weather'][0]['description'], dicty['weather'][0]['icon']))
        return simple_data


weather1 = Weather(apikey="a95a27c945074819e1f4ac78d53814ab", city="Sydney", lat=43, lon=-3.14)
pprint.pprint(weather1.next_12h_simplified())
