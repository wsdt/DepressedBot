from chatterbot import ChatBot
from peewee import SqliteDatabase
from global_constants import DB_NAME
from secrets.secrets import TWITTER
import logging
from starterkit.fallback_module.CustomTwitterTrainer import CustomTwitterTrainer

## TODO: Create template file!

""" As get_smart_answer is no regular module, the .conf-file here looks completely different. """

# Set database file
db = SqliteDatabase(DB_NAME)

# Set up chatbot
"""chatbot = ChatBot(
    'HOME_ASSISTANT',
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
)"""

# Comment out the following line to disable verbose logging
logging.basicConfig(level=logging.INFO)

chatbot = ChatBot(
    'DEPRESSIVE_BOT',
    logic_adapters=[
        "chatterbot.logic.BestMatch"
    ],
    twitter_consumer_key=TWITTER["CONSUMER_KEY"],
    twitter_consumer_secret=TWITTER["CONSUMER_SECRET"],
    twitter_access_token_key=TWITTER["ACCESS_TOKEN"],
    twitter_access_token_secret=TWITTER["ACCESS_TOKEN_SECRET"],
    twitter_lang="en",
    trainer="starterkit.fallback_module.CustomTwitterTrainer.CustomTwitterTrainer"
)


