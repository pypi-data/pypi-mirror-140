from textblob import TextBlob
from textblob.classifiers import NaiveBayesClassifier

class NLPService:
    def __init__(self):
        self.text = ""
        self.blob = None

    def setText(self,text):
        self.text = text
        self.blob = TextBlob(text)

    def getText(self):
        return self.text

    def detactLanguage(self):
        return self.blob.detect_language()


    def translate(self,lang):
        
        b = self.blob.translate(to=lang)
        return str(b)


    def train(self):
        # self.cl = NaiveBayesClassifier(TRAINING_SAMPLE)
        pass


    def test(self):
        return self.cl.classify(self.text)

    def getTags(self):
        return self.blob.tags
