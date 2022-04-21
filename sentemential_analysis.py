import text2emotion as te
from googletrans import Translator

from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from textblob import TextBlob
from textblob.sentiments import PatternAnalyzer


class EmotionAnalyzer:

    def __init__(self):
        tokenizer = RegexTokenizer()
        self.model = FastTextSocialNetworkModel(tokenizer=tokenizer)

        self.comm_org = [
            'Курс биткоина прогноз на пятницу, 22-е апреля: 41241 долларов, максимум 44128, минимум 38354.',
            'Прогноз курса биткоина на понедельник, 25-е апреля: 41941 долларов, максимум 44877, минимум 39005!',
            'Курс биткоина прогноз на вторник, 26-е апреля: 43124 долларов, максимум 46143, минимум 40105.',
            'Прогноз курса биткоина на среду, 27-е апреля: 42376 долларов, максимум 45342, минимум 39410!!!',
            'Эксперты рассказали, почему первая криптовалюта может вернуться к росту.'
        ]
        self.summary = {}

        self.comm_rus = []
        self.comm_en = []

        self.text_en = ''

        self.emotions_dost = []
        self.emotions_t2e = {}
        self.emotions_blob = []

    def translate(self):
        translator = Translator()

        for comm in self.comm_org:
            self.comm_rus.append(translator.translate(comm, 'ru').text)
            self.comm_en.append(translator.translate(comm, 'en').text)
            self.text_en += self.comm_en[-1]

    def get_sentiments(self):
        self.emotions_dost = self.model.predict(self.comm_rus, k=5)
        self.emotions_t2e = te.get_emotion(self.text_en)

        for i in range(len(self.comm_en)):
            blob = TextBlob(self.comm_en[i], analyzer=PatternAnalyzer())
            self.emotions_blob.append(blob.sentiment)

    def get_summary(self):

        neg_t2e = self.emotions_t2e['Angry'] + self.emotions_t2e['Sad'] + self.emotions_t2e['Fear'] / 3 * 100
        pos_t2e = self.emotions_t2e['Happy'] + self.emotions_t2e['Surprise'] / 2 * 100

        surprise_t2e = self.emotions_t2e['Surprise'] * 100

        neg_dost = 0
        pos_dost = 0
        spc_dost = 0

        pol_blob = 0
        sub_blob = 0

        l = len(self.comm_en)

        for i in range(l):
            neg_dost += self.emotions_dost[i]['negative']
            pos_dost += self.emotions_dost[i]['positive']
            spc_dost += self.emotions_dost[i]['speech']

            sub_blob += self.emotions_blob[i].subjectivity / l
            pol_blob += self.emotions_blob[i].polarity / l

        neg_dost = neg_dost / l * 100
        pos_dost = pos_dost / l * 100
        spc_dost = spc_dost * 100

        neg_blob = 2 - pol_blob + 1 / 2 * 100
        pos_blob = 100 - neg_blob
        sub_blob *= 100

        pos_sum = (pos_blob + pos_dost) / 2 + pos_t2e
        neg_sum = (neg_blob + neg_dost) / 2 + neg_t2e

        self.summary = {"negative": neg_sum, "positive": pos_sum, "emotionality": sub_blob, "impressive": surprise_t2e,
                        "appeal": spc_dost}

    def show(self):
        print("t2e.sentiments:", self.emotions_t2e)

        print("\n dost.sentiments:")
        for comment in self.emotions_dost:
            print(comment)

        print("\n blob.sentiments:")
        for comment in self.emotions_blob:
            print(comment)

    def show_summary(self):
        print(self.summary)


a = EmotionAnalyzer()
a.translate()
a.get_sentiments()

a.get_summary()
a.show_summary()

# summary example:
# { 'negative': 46.04873134835561, 'positive': 32.47725801429153, 'emotionality': 23.466666666666665,
# 'impressive': 14.000000000000002, 'appeal': 3.2520064734853804 }
