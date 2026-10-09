from .providers.open_meteo import fetch_weather

# Later, this could wrap the provider with more business logic.
# For now, it simply exposes the existing implementation to maintain the contract.
