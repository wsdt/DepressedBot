from starterkit.fallback_module.conf import chatbot

""" +++++++++ Train assistant (= default module (not removeable without coding) +++
-> Train bot/assistant with default language (english) """
print("Training assistant, this can take a while.")
#TODO: make language configurable (also modules) and also train via twitter (also language chooseable)
#chatbot.train("chatterbot.corpus.english")
chatbot.train()