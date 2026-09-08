from time import timezone
import requests

from weather_agent.config import FORECAST_URL, GEOCODE_URL, WEATHER_REQUEST_TIMEOUT

WEATHER_CODES: dict[int, str] = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudly",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    80: "rain showers",
    95: "thunderstorm",
    96: "thunderstorm with hail"

}

def lookup_weather(location:str) -> str:
    try:
        geo = requests.get(GEOCODE_URL,params={"name":location,"count":1},timeout=WEATHER_REQUEST_TIMEOUT)

        geo.raise_for_status()

        print(geo.json())
        matches = geo.json().get("results")

        if not matches:
            return f"We couldn't find a place called {location}"
        
        place = matches[0]
        lat,lon = place["latitude"], place["longitude"]

        #join the name and country with a comma
        label = ", ".join(part for part in (place.get("name"),place.get("country")) if part)
        print(label)

        forecast = requests.get(FORECAST_URL,params={"latitude":lat,"longitude":lon,"current":"temperature_2m,weather_code,wind_speed_10m"},timeout=WEATHER_REQUEST_TIMEOUT)
        #get the current temperature , weather code and wind speed

        forecast.raise_for_status()
        print(forecast.json())

        current = forecast.json().get("current")

        temperature = current.get("temperature_2m")
        weather_code = current.get("weather_code")
        wind_speed = current.get("wind_speed_10m")

        sky = WEATHER_CODES.get(weather_code,f"weather code {weather_code}")

        wind_note = f", wind {wind_speed} km/h" if wind_speed else ""

        return f"The current temperature in {label} is {temperature} degree celcius, the sky is {sky}{wind_note}."
    except requests.exceptions.RequestException as err:
        return f"We couldnt look up the weather for {location}: {err}"
    except Exception as err:
        return f"Unexpected weather response error: {err}"
        



print(lookup_weather("London"))