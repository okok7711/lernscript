import asyncio
from main import Client

    
client = Client(
    input("Email: "),
    input("Passwort: ")
)

print(await client.login())