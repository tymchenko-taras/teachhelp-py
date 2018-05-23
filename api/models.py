from django.db import models
from django.utils import timezone
import re


class SentenceManager(models.Manager):
    def gerund_regexp(self, keyword):
        return self.filter(title__icontains=keyword).count()

class Sentence(models.Model):
    class Meta:
        db_table = 'sentence'

    content = models.TextField()
    objects = SentenceManager()

    flags = {
        1: {1:True, 2:True, 3:False},
        2: {1:True, 3:True},
        3: {4:True},
    }

    expressions = {
        1: {
            'description': 'continuous form of verb == all words with ing ending except wing, king... ',
            'expression': re.compile(r'(\b(?!\b(during|wing|king|interesting|something|spring|hawking|thing|anything|everything|nothing|ceiling|building|dressing|dwelling|feeling|filling|longing|meaning|morning|evening|pudding|shilling|wedding)\b)\w+ing)\b'),
            # 'expression': r'(\b(?!\b(during|wing|king|interesting|something|spring|hawking|thing|anything|everything|nothing|ceiling|building|dressing|dwelling|feeling|filling|longing|meaning|morning|evening|pudding|shilling|wedding)\b)\w+ing)\b',
        },
        2: {
            'description': '[result.1] - word from expression 1, (\b(is|was|has been|will be)\b) - word "to be", ((?!(?!dr|eg|mr|mrs)\w{2,}(\.|\?|!)).)* - будь-які символи крім (.|?|!) але не тоді коли вони йдуть після скорочень P.E.T.A. з одної букви (\w) або після dr, mr... Це look-ahead в look-aheadі',
            'expression': r'([result.1]((?!(?!dr|eg|mr|mrs)\w{2,}(\.|\?|!)).)*(\b(can|may|shall|must|could|might|should|would|is|was|has been|will)\b))',
        },
        3: {
            'description': '',
            'expression': r'(\b(the|a)\b((?!(?!dr|eg|mr|mrs)\w{2,}(\.|\?|!)).)*[result.2])',
        },
        4: {
            'description': 'Gerund after prepositions',
            'expression': r"\b(at|on|by|in|of|for|from|after|before|with|without|about|over|between|against|feel like|used to|forward to)\s(\w+\s)?[result.1]",
        },

        # 4: {
        #     'description': '',
        #     'expression': r'(((\b(is|was|been)\b))((?!(?!dr|eg|mr|mrs)\w{2,}(\.|\?|!)).)*[result.1])',
        # },
        # 5: {
        #     'description': '',
        #     'expression': r'[result.4]',
        # },
    }

    def get_approximate_flags(self, content):
        result = set()
        expression_results = self.process_sentence_by_expressions(content)
        for flag in self.flags:
            for expression_id in self.flags[ flag ]:
                if expression_id in expression_results:
                    if self.flags[ flag ][ expression_id ] == bool(expression_results[ expression_id ]):
                        result.add(flag)
                        continue

                # remove current flag from result because something didn't match
                result = {i for i in result if i != flag}
                break

        # return unique values
        return result


    def get_expressions_result(self):
        return self.process_sentence_by_expressions(self, self.content)

    def static_vars(**kwargs):
        def decorate(func):
            for k in kwargs:
                setattr(func, k, kwargs[k])
            return func

        return decorate

    def delete_banned_words(matchobj):
        word = matchobj.group(0)
        if word.lower() in set('abc', 'bac', 'cab'):
            return ""
        else:
            return word

    @static_vars(counter=re.compile('^(.*)\[result\.(\d+)\](.*)$'))
    def process_sentence_by_expressions(self, text):
        result = {}
        text = text.lower()
        def callback(match):
            if not match.group(2):
                return ''

            id = int(match.group(2))
            if id not in result:
                return ''

            if result[id]:
                escaped = [re.escape(word) for word in result[id] ]
                return match.group(1) + '(' + '|'.join(escaped) + ')' + match.group(3)

        for i in self.expressions:
            if isinstance(self.expressions[i]['expression'], str):
                expression = self.process_sentence_by_expressions.counter.sub(callback, self.expressions[i]['expression'])
            else:
                expression = self.expressions[i]['expression']
            if i not in result:
                result[i] = [];
            if expression:
                for match in re.finditer(expression, text):
                    result[i].append(match.group(0))

        return result
