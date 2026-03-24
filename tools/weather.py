from langchain_core.tools import tool
import spacy
import os
from dotenv import load_dotenv
import requests

load_dotenv()

weather_key = os.getenv('WEATHER_API')
nlp = spacy.load("en_core_web_sm")

@tool
def extract_city(command:str)->str:
    doc = nlp(command)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            return ent.text
    return None

@tool
def weather_func(city:str)->str:
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_key}"
    response = requests.get(weather_url)
    data = response.json()
    if data['cod'] == 200:
        main = data['main']
        weather = data['weather'][0]
        temperature = main['temp']
        temp_in_celcius = temperature-273.15
        final_temp_in_celcius = round(temp_in_celcius, 2)
        description = weather['description']
        return f"The weather in {city} is {description} with a temperature of {final_temp_in_celcius}°C."
    else:
        return "City not found."

@tool
def get_weather(command:str)->str:
    city = extract_city(command)
    print(city)
    if city:
        return weather_func(city)
    else:
        return "I couldn't determine the city for the weather request."
