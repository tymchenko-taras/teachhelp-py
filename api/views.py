from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse
from .models import Sentence
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.db import connection
import csv
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import datetime
from django.http import StreamingHttpResponse
import time
import re
import nltk
from django.utils.html import escape
from django.db import connections
from nltk.tokenize import PunktSentenceTokenizer
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_extraction.text import CountVectorizer

import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
import nltk



class TestView(ListView):

    def run(self):
        nltk.data.path.append('/var/lib/python/nltk')
        vectorizer = CountVectorizer(ngram_range=(1, 3))

        rows = self.get_rows()
        x = vectorizer.fit_transform(row['tokens'] for row in rows).toarray()
        y = [row['value'] for row in rows]

        model = GaussianNB()
        model.fit(x, y)

        expected = y
        predicted = model.predict(x)

        for i, value in enumerate(predicted):
            rows[i]['predicted'] = value

        missed = rows
        # missed = [row for row in rows if row['predicted'] == row['value']]
        return missed
        # print(predicted)
        # summarize the fit of the model
        print(metrics.classification_report(expected, predicted))
        # print(metrics.confusion_matrix(expected, predicted))

    def get_rows(self):
        cnx = mysql.connector.connect(user='dev', password='dev', host='container-mysql', database='teachhelp')
        sentences = cnx.cursor()
        query = ("""
          SELECT `s`.`id`, `s`.`content`, sgc.`value`
          FROM `sentence` s INNER JOIN `sentence_grammar_construction` sgc ON (`s`.`id` = `sgc`.`sentence_id`)
          WHERE `sgc`.`grammar_construction_id` IN (1)
          LIMIT 1000
        """)
        sentences.execute(query)
        result = []
        for (id, content, value) in sentences:
            result.append({
                'id': id,
                'content': content,
                'tokens': self.get_tokens(content),
                'value': value
            })
        return result

    def get_tokens(self, text):
        try:
            allowed = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS',
                       'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN',
                       'VBP',
                       'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
            words = nltk.word_tokenize(text)
            words = nltk.pos_tag(words)
            return ' '.join([word[1] for word in words if word[1] in allowed])

        except Exception as e:
            print(str(e))

    def learn_1(self):
        y, tokens = [], []
        sentences = Sentence.objects.filter(grammar_constructions__in=[1])
        vectorizer = CountVectorizer(ngram_range=(1, 3))

        for sentence in sentences:
            tokens.append(self.get_tokens(sentence.content))
            y.append(sentence.sentencegrammarconstruction_set.get().value)

        x = vectorizer.fit_transform(tokens).toarray()


        model = GaussianNB()
        model.fit(x, y)

        res = []
        x = x.tolist()
        for i in x:
            predicted = model.predict([x[i]])
            if predicted[0] != y[i]:
                res.append([sentence.content, y[i]], predicted[0])

        # predicted = model.predict(x)
        a = res



    def train(self, x, y):
        from sklearn import metrics
        from sklearn.linear_model import LogisticRegression
        from sklearn.naive_bayes import GaussianNB
        model = GaussianNB()
        # model = LogisticRegression()
        model.fit(x, y)
        # print(model)
        # make predictions
        expected = y
        predicted = model.predict(x)
        # print(predicted)
        # summarize the fit of the model
        # print(metrics.classification_report(expected, predicted))


        y_test = np.asarray(y)
        y_test = np.asarray(y_test)
        misclassified = np.where(y_test != model.predict(x))



        print(metrics.confusion_matrix(expected, predicted))

    def vectorize_ngrams_tokenization(self, texts):
        from sklearn.feature_extraction.text import CountVectorizer
        allowed = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS',
                   'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP',
                   'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
        vectorizer = CountVectorizer(ngram_range=(1, 3), vocabulary=allowed)
        result = vectorizer.fit_transform(texts).toarray()
        res1 = vectorizer.vocabulary_

        return result

    def vectorize_bag_of_words(self):
        from functools import reduce
        import numpy as np

        texts = [['i', 'have', 'a', 'cat'],
                 ['he', 'have', 'a', 'dog'],
                 ['he', 'and', 'i', 'have', 'a', 'cat', 'and', 'a', 'dog']]

        dictionary = list(enumerate(set(reduce(lambda x, y: x + y, texts))))

        def vectorize(text):
            vector = np.zeros(len(dictionary))
            for i, word in dictionary:
                num = 0
                for w in text:
                    if w == word:
                        num += 1
                if num:
                    vector[i] = num
            return vector

        for t in texts:
            print(vectorize(t))

    def split_by_sentences(self):

        text = """
        Where username is your username in your system. Save and close sudoers file (if you haven't changed your default terminal editor (you'll know if you have), press ctl+x to exit nano (but note that the screenshot below shows vim), and it'll prompt you to save).
        """
        sentences = nltk.tokenize.sent_tokenize(text)
    def wordnet(self):
        synonimus = nltk.corpus.wordnet.synsets('program')


        #synset
        i = synonimus[0].name()

        # one word
        i = synonimus[0].lemmas()[0].name()

        #definition
        i = synonimus[0].definition()

        #examples
        i = synonimus[0].examples()

        #antonyns
        i = synonimus[0].lemmas()[0].antonyms()



        return 1

    # def get_tokens(self, text):
    #     try:
    #         allowed = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS','PDT', 'POS', 'PRP', 'PRP$','RB', 'RBR', 'RBS', 'RP', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
    #         words = nltk.word_tokenize(text)
    #         words = nltk.pos_tag(words)
    #         return ' '.join([word[1] for word in words if word[1] in allowed])
    #
    #     except Exception as e:
    #         print(str(e))

    def get(self, request, *args, **kwargs):
        nltk.data.path.append('/var/lib/python/nltk')
        items = self.run()

        return render(request, 'api/list_of_dict.html', {'items': items})
        # return HttpResponse()

class SentenceView(ListView):
    model = Sentence
    template_name = 'api/sentence_list.html'  # Default: <app_label>/<model_name>_list.html
    context_object_name = 'sentences'  # Default: object_list
    paginate_by = 100
    # queryset = Sentence.objects.all()[:432]  # Default: Model.objects.all()
    def get_queryset(self):
        params = {
            'page': self.request.GET.get('page'),
            'ipp': self.paginate_by,
            'filters': [],
        }
        qs = self.model.get_items(self.request.GET.get('query'), params);
        return qs


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        time.sleep(1)
        return value


def get_xml(sentences):
    yield '''<?xml version="1.0" encoding="UTF-8"?>
 <sphinx:docset>
  <sphinx:schema>
   <sphinx:field name="content"/>
   <sphinx:attr name='itemId' type='int' bits='16'/>
   <sphinx:attr name='flags' type='multi'/>
   <sphinx:attr name='content' type='string'/>
  </sphinx:schema>'''
    i = 0
    for sentence in sentences:
        # flags = '';
        # result = Sentence().process_sentence_by_expressions(sentence.content)
        # if 1 in result and 2 in result and 3 in result and result[1] and result[2] and not result[3]:
        #     flags = '<items id="0">1</items>';
        #yield '<sphinx:document id="' + str(sentence.id) + '"><content>' + escape(sentence.content) + '</content><itemId>' + str(sentence.id)    + '</itemId><flags>'+flags+'</flags></sphinx:document>'
        i = i + 1
        yield '<sphinx:document id="'+ str(i) +'"><content>lalala</content><itemId>1</itemId><flags></flags></sphinx:document>'
    yield '</sphinx:docset>'


def sentences_xml(request):
    # result = Sentence().get_approximate_flags('going to school is')
    #
    # return HttpResponse({'2'})


    connection = connections['sphinx']
    start_time = time.time()
    offset = 0
    limit = 50000
    while True:
        sentences = Sentence.objects.all()[offset:limit+offset]
        # sentences = Sentence.objects.all()[:limit]
        offset = offset + limit
        if not sentences.exists():
            break

        values = []
        params = []
        for sentence in sentences:
            flags = Sentence().get_approximate_flags(sentence.content)

            values.append('('+ str(sentence.id) +', %s, ('+ ','.join({str(flag) for flag in flags}) +'))')
            params.extend([sentence.content])

        with connection.cursor() as cursor:
            sql = 'REPLACE INTO  paragraph_rt (id, content, flags_t) VALUES ' + (', '.join(values))
            cursor.execute(sql, params)

        # with open('test.txt', 'w') as f:
        #     f.write(str(limit) + '\n')
        # break
    return HttpResponse({"--- %s seconds ---" % (time.time() - start_time)})


def sentences_xml2(request):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    #sentences = Sentence.objects.all()[:1000]
    sentences = [{'id':1, 'content':''}]*100000

    response = HttpResponse((x for x in range(100000)))
    # response = StreamingHttpResponse((x for x in range(100000)))
    # response = StreamingHttpResponse(get_xml(sentences))
    # response = HttpResponse(get_xml(sentences), content_type="text/xml")
    return response

def sentences_xml1(request):

    generated_on = str(datetime.datetime.now())

    # Configure one attribute with set()
    root = Element('opml')
    root.set('version', '1.0')

    root.append(Comment('Generated by ElementTree_csv_to_xml.py for PyMOTW'))

    head = SubElement(root, 'head')
    title = SubElement(head, 'title')
    title.text = 'My Podcasts'
    dc = SubElement(head, 'dateCreated')
    dc.text = generated_on
    dm = SubElement(head, 'dateModified')
    dm.text = generated_on

    body = SubElement(root, 'body')


    current_group = None


    group_name = 'g1'
    podcast_name = 'p1'
    xml_url = 'u1'
    html_url = 'h1'
    if current_group is None or group_name != current_group.text:
        # Start a new group
        current_group = SubElement(body, 'outline', {'text': group_name})
    # Add this podcast to the group,
    # setting all of its attributes at
    # once.
    podcast = SubElement(current_group, 'outline',
                         {'text': podcast_name,
                          'xmlUrl': xml_url,
                          'htmlUrl': html_url,
                          })

    # print(root)
    return HttpResponse(root)





    # r = Sentence().process_sentence_by_expressions(text='tommy`s working is good')
    # post = get_object_or_404(Sentence, pk=1)
    # sentences = Sentence.objects.all()[:1000]
    # for sentence in sentences:
    #     flags = sentence.get_expressions_result()
    # return HttpResponse({})
    #
    # count = Sentence.objects.count();
    # all = Sentence.objects.all();
    # for post in all:
    #     return HttpResponse(post.content, content_type='application/json')
    # import nltk
    # posts = Post.objects.filter(created_date__lte=timezone.now()).order_by('published_date')
    # return render(request, 'blog/post_list.html', {'posts': posts})
