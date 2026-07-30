import httpx
from crewai.tools import tool


@tool("Weather")
def weather_tool(location: str) -> str:
    """Gets current weather conditions for any city or location.
    Use when the user asks about weather, temperature, or climate conditions."""
    try:
        geo = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        geo.raise_for_status()
        geo_data = geo.json()
        if not geo_data.get("results"):
            return f"Location '{location}' not found."
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        name = geo_data["results"][0]["name"]
        country = geo_data["results"][0].get("country", "")

        wx = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "timezone": "auto",
            },
            timeout=10,
        )
        wx.raise_for_status()
        data = wx.json()["current_weather"]

        temp = data["temperature"]
        wind = data["windspeed"]
        code = data.get("weathercode", 0)

        conditions = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle",
            61: "Slight rain", 71: "Slight snow", 95: "Thunderstorm",
        }
        desc = conditions.get(code, f"Code {code}")

        return (
            f"Weather in {name}, {country}:\n"
            f"  Temperature: {temp}°C\n"
            f"  Conditions:  {desc}\n"
            f"  Wind Speed:  {wind} km/h"
        )
    except Exception as e:
        return f"Weather lookup failed: {e}"


@tool("Currency Converter")
def currency_tool(amount: float, from_currency: str, to_currency: str) -> str:
    """Converts an amount from one currency to another using live exchange rates.
    Use for billing inquiries, international payments, or price comparisons
    across different currencies.
    Examples: amount=100, from_currency='USD', to_currency='EUR'"""
    try:
        src = from_currency.upper().strip()
        dst = to_currency.upper().strip()
        resp = httpx.get(
            f"https://api.frankfurter.app/latest",
            params={"from": src, "to": dst},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        rate = data["rates"][dst]
        converted = amount * rate
        return (
            f"{amount:.2f} {src} = {converted:.2f} {dst}\n"
            f"Exchange rate: 1 {src} = {rate:.6f} {dst}"
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Currency conversion failed: unknown currency code '{from_currency}' or '{to_currency}'."
        return f"Currency conversion failed: {e}"
    except Exception as e:
        return f"Currency conversion failed: {e}"
