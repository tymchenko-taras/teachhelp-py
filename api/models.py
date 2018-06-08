from django.db import models
from django.utils import timezone
import re
import sphinxapi
from search.repositories import Search


class SentenceManager(models.Manager):
    def gerund_regexp(self, keyword):
        return self.filter(title__icontains=keyword).count()

class GrammarConstruction(models.Model):
    class Meta:
        db_table = 'grammar_construction'
    name = models.TextField()

class SentenceGrammarConstruction(models.Model):
    class Meta:
        db_table = 'sentence_grammar_construction'

    sentence = models.ForeignKey('Sentence')
    grammar_construction = models.ForeignKey('GrammarConstruction')
    user = models.ForeignKey('auth.User')
    value = models.IntegerField()
    comment = models.TextField()

class Sentence(models.Model):
    class Meta:
        db_table = 'sentence'

    content = models.TextField()
    objects = SentenceManager()
    grammar_constructions = models.ManyToManyField('GrammarConstruction', through='SentenceGrammarConstruction')

    flags = {
        1: {1:True, 2:True, 3:False},
        2: {1:True, 3:True},
        3: {4:True},
    }

    expressions = {
        1: {
            'description': 'continuous form of verb == all words with ing ending except wing, king... ',
            'expression': re.compile(r'(\b(?!\b(bring|during|wing|king|interesting|something|spring|hawking|thing|anything|everything|nothing|ceiling|building|dressing|dwelling|feeling|filling|longing|meaning|morning|evening|pudding|shilling|wedding)\b)\w+ing)\b'),
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
        5: {
            'description': 'Continuous tense',
            'expression': r"\b(am|'m|is|'s|are|'re|had been|'d been|has been|'s been|have been|'ve been|will be|'ll be| was|were)\s((?!(?!dr|eg|mr|mrs)\w{2,}(\.|,|;|\?|!)).)*[result.1]",
        },
        6: {
            'description': 'Having + past participle',
            'expression': r"[result.1]\s(\w+ed|arisen|awakened|awoken|backslidden|backslid|been|born|borne|beaten|beat|become|begun|bent|bet|betted|bidden|bid|bound|bitten|bled|blown|broken|bred|brought|broadcast|broadcasted|browbeaten|browbeat|built|burned|burnt|burst|busted|bust|bought|cast|caught|chosen|clung|clothed|clad|come|cost|crept|crossbred|cut|daydreamed|daydreamt|dealt|dug|disproved|disproven|dived|dived|done|drawn|dreamed|dreamt|drunk|driven|dwelt|dwelled|eaten|fallen|fed|felt|fought|found|fitted|fit|fit|fitted|fled|flung|flown|forbidden|forecast|foregone|foreseen|foretold|forgotten|forgot|forgiven|forsaken|frozen|frostbitten|gotten|got|given|gone|ground|grown|hand-fed|handwritten|hung|had|heard|hewn|hewed|hidden|hit|held|hurt|inbred|inlaid|input|inputted|interbred|interwoven|interweaved|interwound|jerry-built|kept|knelt|kneeled|knitted|knit|known|laid|led|leaned|leant|leaped|leapt|learned|learnt|left|lent|let|lain|lied|lit|lighted|lip-read|lost|made|meant|met|miscast|misdealt|misdone|misheard|mislaid|misled|mislearned|mislearnt|misread|misset|misspoken|misspelled|misspelt|misspent|mistaken|mistaught|misunderstood|miswritten|mowed|mown|offset|outbid|outbred|outdone|outdrawn|outdrunk|outdriven|outfought|outflown|outgrown|outleaped|outleapt|outlied|outridden|outrun|outsold|outshined|outshone|outshot|outsung|outsat|outslept|outsmelled|outsmelt|outspoken|outsped|outspent|outsworn|outswum|outthought|outthrown|outwritten|overbid|overbred|overbuilt|overbought|overcome|overdone|overdrawn|overdrunk|overeaten|overfed|overhung|overheard|overlaid|overpaid|overridden|overrun|overseen|oversold|oversewn|oversewed|overshot|overslept|overspoken|overspent|overspilled|overspilt|overtaken|overthought|overthrown|overwound|overwritten|partaken|paid|pleaded|pled|prebuilt|predone|premade|prepaid|presold|preset|preshrunk|proofread|proven|proved|put|quick-frozen|quit|quitted|read|reawaken|rebid|rebound|rebroadcast|rebroadcasted|rebuilt|recast|recut|redealt|redone|redrawn|refit|refitted|refitted|refit|reground|regrown|rehung|reheard|reknitted|reknit|relaid|relayed|relearned|relearnt|relit|relighted|remade|repaid|reread|rerun|resold|resent|reset|resewn|resewed|retaken|retaught|retorn|retold|rethought|retread|retrofitted|retrofit|rewaken|rewaked|reworn|rewoven|reweaved|rewed|rewedded|rewet|rewetted|rewon|rewound|rewritten|rid|ridden|rung|risen|roughcast|run|sand-cast|sawed|sawn|said|seen|sought|sold|sent|set|sewn|sewed|shaken|shaved|shaven|sheared|shorn|shed|shined|shone|shit|shat|shitted|shot|shown|showed|shrunk|shut|sight-read|sung|sunk|sat|slain|slayed|slayed|slept|slid|slung|slinked|slunk|slit|smelled|smelt|sneaked|snuck|sown|sowed|spoken|sped|speeded|spelled|spelt|spent|spilled|spilt|spun|spit|spat|split|spoiled|spoilt|spoon-fed|spread|sprung|stood|stolen|stuck|stung|stunk|strewn|strewed|stridden|stricken|struck|stricken|strung|striven|strived|sublet|sunburned|sunburnt|sworn|sweat|sweated|swept|swollen|swelled|swum|swung|taken|taught|torn|telecast|told|test-driven|test-flown|thought|thrown|thrust|trodden|trod|typecast|typeset|typewritten|unbent|unbound|unclothed|unclad|underbid|undercut|underfed|undergone|underlain|undersold|underspent|understood|undertaken|underwritten|undone|unfrozen|unhung|unhidden|unknitted|unknit|unlearned|unlearnt|unsewn|unsewed|unslung|unspun|unstuck|unstrung|unwoven|unweaved|unwound|upheld|upset|woken|waked|waylaid|worn|woven|weaved|wed|wedded|wept|wet|wetted|whetted|won|wound|withdrawn|withheld|withstood|wrung|written)\b",
        },
        7: {
            'description': 'Participle',
            'expression': r"[result.1]\s(of|to|that|about|from)",
        },
        8: {
            'description': 'Participle',
            'expression': r"without\s[result.1]",
        },
        9: {
            'description': 'Participle',
            'expression': r"(while|when)\s[result.1]",
        },
        10: {
            'description': 'Stable phrase "get going"',
            'expression': r"(get|got)\s[result.1]",
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

    def get_items(query, params):
        client = sphinxapi.SphinxClient()
        client.SetServer('container-sphinx', 9312)
        client.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED)
        client.SetLimits(params)

    def get_approximate_flags2(self, content):
        result = set()
        expression_results = self.process_sentence_by_expressions(content)
        for i in expression_results:
            if expression_results[i]:
                result.add(i)
        return result

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
