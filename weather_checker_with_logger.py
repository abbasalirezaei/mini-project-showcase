import logging
import random
import time

# Set up logging
logger = logging.getLogger("weather_checker")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# Console log output
console = logging.StreamHandler()
console.setFormatter(formatter)

# File log output
file = logging.FileHandler("weather.log", encoding="utf-8")
file.setFormatter(formatter)

logger.addHandler(console)
logger.addHandler(file)

# Simulated weather checker
def check_weather():
    logger.info("Starting weather check...")
    cities = ["Tehran", "Shiraz", "Isfahan", "Tabriz"]
    for city in cities:
        logger.info(f"Checking weather for {city}")
        time.sleep(1)
        weather = random.choice(["Sunny", "Cloudy", "Rainy", "Stormy"])
        logger.info(f"The weather in {city} is: {weather}")

    logger.info("Weather check completed ✅")

check_weather()