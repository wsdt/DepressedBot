from chatterbot.trainers import Trainer
from chatterbot.conversation import Statement, Response
from twitter import TwitterError
from keyword_datasets.extracted_keywords_light import depressed_keywords
import time, re

class CustomTwitterTrainer(Trainer):

    """ Initialize Custom Twitter Trainer and login into Twitter API. """
    def __init__(self, storage, **kwargs):
        super(CustomTwitterTrainer, self).__init__(storage, **kwargs)
        from twitter import Api as TwitterApi

        # The word to be used as the first search term when searching for tweets
        self.lang = kwargs.get('twitter_lang')

        self.api = TwitterApi(
            consumer_key=kwargs.get('twitter_consumer_key'),
            consumer_secret=kwargs.get('twitter_consumer_secret'),
            access_token_key=kwargs.get('twitter_access_token_key'),
            access_token_secret=kwargs.get('twitter_access_token_secret'),
            tweet_mode='extended'
        )


    """ Receive all statements with our keywords from Twitter and then filter them (remove mentions, 
    hashtags, etc.) and then save them into the db. """
    def get_statements(self):
        statements = []

        no_error_occurred = True
        for word in depressed_keywords:
            if no_error_occurred:
                no_error_occurred = self.perform_search(statements,word)
                print("CustomTwitterTrainer:get_statements: Stopped calling API. Waiting for 1.5 minutes, Last word -> "+word)
                self.save_statements(statements)
                time.sleep(75) # wait 75 seconds after each api call to prevent being banned
            else:
                print("CustomTwitterTrainer:get_statements: We got banned. Waiting for 16 minutes.")
                self.save_statements(statements)
                time.sleep(60*16) # wait 16 minutes bc. we have been banned
                no_error_occurred = True


    """ Save all new statements into database and remove it from the list to prevent 
     duplications. """
    def save_statements(self, statements):
        for statement in statements:
            self.storage.update(statement)
            statements.remove(statement) # remove statement as it got saved
        print("Saved {} new statements.".format(len(statements)))


    """ Search twitter for tweets with our settings (e.g. term, lang, etc.) """
    def perform_search(self, statements, word):
        self.logger.info(u'Requesting 100 ran'
                         u'dom tweets containing the word {}'.format(word))
        tweets = self.api.GetSearch(term=word, count=100, lang=self.lang)
        for tweet in tweets:

            # get full text not truncated
            if tweet.retweeted_status is None:
                full_text = tweet.full_text
            else:
                full_text = tweet.retweeted_status.full_text

            statement = Statement(self.clean_up(full_text))

            if tweet.in_reply_to_status_id:
                try:
                    status = self.api.GetStatus(tweet.in_reply_to_status_id)

                    statement.add_response(Response(self.clean_up(status.full_text)))
                    statements.append(statement)
                except TwitterError as error:
                    self.logger.warning(str(error))
                    # do not return false
                except Exception as error:
                    self.logger.error(str(error))
                    return False

        self.logger.info('Adding {} tweets with responses'.format(len(statements)))
        return True


    """ Clean up tweets from mentions, hashtags and so on. """
    regex_cleanup = re.compile(r'(,;\+-~:\|\(\)\[\])|([@#][\w_-]+)|(<[a-zA-Z0-9 ="\'/]+>)|((http://|https://)?(www\.)?(?:[a-zA-Z0-9]+@)?((?:[a-zA-Z0-9])+(?:\.)){1}(?:[a-zA-Z0-9])+(/[a-zA-Z0-9]+)*((\?[a-zA-Z0-9]+)(?:#[a-zA-Z0-9]+))?)|((\:\w+\:|\<[\/\\]?3|[\(\)\\\D|\*\$][\-\^]?[\:\;\=]|[\:\;\=B8][\-\^]?[3DOPp\@\$\*\\\)\(\/\|])(?=\s|[\!\.\?]|$))')
    regex_smileys = re.compile(r'[\U00010000-\U0010ffff]', re.UNICODE)
    regex_absatz = re.compile(r'\n')
    regex_multiplespaces = re.compile(r'( ){2,}')
    replace_with = r""

    def clean_up(self, text):
        print("Cleaning text: "+text)
        # After cleanup regex remove all unicode emojis and replace \n with ,
        text = re.sub(self.regex_multiplespaces," ",
                      re.sub(self.regex_absatz,", ",
                        re.sub(self.regex_smileys,self.replace_with, re.sub(self.regex_cleanup, self.replace_with, text))))

        print("Cleaned text: "+text)
        return text

    def train(self):
        self.get_statements()
