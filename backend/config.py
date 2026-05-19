import os 
from dotenv import load_dotenv

load_dotenv()

class Config: 

    Database_URL = os.getenv('DATABASE_URL')

    Secret_Key = os.getenv('SECRET_KEY')

    Algorithm = 'HS256'
    Access_Token_Expire_Minutes = 60 * 24 * 7


    Google_Client_ID = os.getenv('GOOGLE_CLIENT_ID')
    Google_Client_Secret = os.getenv('GOOGLE_CLIENT_SECRET')

    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
    Mistral_model_name = "mistral-small-latest"

    