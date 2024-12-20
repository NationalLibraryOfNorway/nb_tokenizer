#!/usr/bin/ python3
# -*- coding: utf-8 -*-

"""
Tokenisator for ngramleser (evt. parsing).
-------------------------------------------
Lars G Johnsen, Nasjonalbiblioteket, juni 2014

Tokenisatorens oppgave er å danne token eller ord fra en sekvens med tegn.
I utgangspunktet fungerer skilletegn og mellomrom som ordgrenser,
men det er unntak, se listen nedenfor. Skilletegn danner som oftest egne token,
men spesielt punktum og komma brukes på flere måter, noe det må tas høyde for.

Noen ord (token) har bestanddeler i form av skilletegn, som forkortelser, tall,
i tillegg kan ordene selv være bundet sammen med bindestrek:

p-pille (bindestrek)
3.3 (punktum i seksjonsnummerering)
etc. (forkortelser)
10 000 (token over mellomrom)
3,14 (desimaltall med komma)
co2 (bokstaver og tall i kjemiske formler)
co2-forurensning (bokstaver tall pluss bindestrek)
17. (ordenstall som i 17. mai)
P. A. Munch (punktum i initialer)
... tre eller flere  punktum
Når punktum følger tall vil tokenisatoren la punktum tilhøre tallet
med mindre punktumet følges av mellomrom og stor bokstav.

Punktum tilhører alle forkortelser som tar punktum uavhenging av kontekst.
Den kan imidlertid gjøres følsom for påfølgende stor bokstav,
men det er altså ikke gjort her.
Punktum tillates inne i ord og deler ikke opp ord med punktum i seg.

Alle skilletegn ellers utgjør egne token, bortsett fra § som kan sekvensieres,
så § og §§ vil være egne tokener;
de benyttes en hel del i lovtekster for entall og flertall.

Tall skrevet med mellomrom blir ett token om de er på formen xx xxx, altså 1
eller 3 siffer etterfulgt av grupper på tre siffer skilt med ett mellomrom.
Så 3 1995 vil være to tokener, mens 3 995 blir ett token,
4000 398 blir igjen to token. (Mulig det er endret)

Tall som følger etter § (adskilt med maks ett mellomrom)
vil aldri tiltrekke seg punktum.

Øvrige tegn som ikke passer inn med mønstrene over behandles som separate token.
"""

import re
import sys
import time
import regex


fork = [
    "[Aa]/[Ss]",
    "[Aa][.]?[Dd]\\.",
    "[Aa][.]?l\\.",
    "[Aa][.]?m\\.",
    "[Aa]b\\.prov\\.", 
    "[Aa]dm\\.dir\\.",
    "[Aa]dm\\.",
    "[Aa]dr\\.",
    "[Aa]dv\\.",
    "[Aa]ga\\.",
    "[Aa]lt\\.",
    "[Aa]ng\\.",
    "[Aa]nk\\.",
    "[Aa]plf\\.",
    "[Aa]pr\\.",
    "[Aa]q\\.",
    "[Aa]ss\\.",
    "[Aa]tt\\.",
    "[Aa]ug\\.",
    "[Aa]ut\\.",
    "[Aa]vd\\.",
    "[Aa]vg\\.",
    "[Aa]vst\\.",
    "[Bb]\\.[Cc]\\.",
    "[Bb]d\\.",
    "[Bb]ed\\.øk\\.",
    "[Bb]et\\.",
    "[Bb]ill\\.mrk\\.",
    "[Bb]ill\\.",
    "[Bb]l[.]?a\\.",
    "[Bb]m\\.",
    "[Bb]nr\\.",
    "[Bb]to\\.",
    "[Bb]vl\\.",
    "[Cc][.]?[Cc]\\.",
    "[Cc]a\\.",
    "[Cc]and\\.mag\\.",
    "[Cc]and\\.",
    "[Cc][Oo]\\.",
    "[Dd][.]?d\\.",
    "[Dd][.]?e\\.",
    "[Dd][.]?m\\.",
    "[Dd][.]?y\\.",
    "[Dd][.]?s\\.",
    "[Dd]\\.å\\.",
    "[Dd]\\.",
    "[Dd]ept\\.",
    "[Dd]es\\.",
    "[Dd]fm\\.",
    "[Dd]g\\.",
    "[Dd]ir\\.",
    "[Dd]isp\\.",
    "[Dd]iv\\.",
    "[Dd]o\\.",
    "[Dd]r\\.philos\\.",
    "[Dd]r\\.",
    "[Dd]ss\\.",
    "[Dd]vs\\.",
    "[Ee]\\.[Kk]r\\.",
    "[Ee][.]?l\\.",
    "[Ee][.]?g\\.",
    "[Ee]\\.f\\.",
    "[Ee]ig\\.",
    "[Ee]ks\\.",
    "[Ee]kskl\\.",
    "[Ee]ksp\\.",
    "[Ee]t\\.",
    "[Ee]tab\\.",
    "[Ee]tabl\\.",
    "[Ee]tc\\.",
    "[Ee]v\\.",
    "[Ee]vt\\.",
    "[Ee]x\\.fac\\.",
    "[Ee]x\\.phil\\.",
    "[Ff][.]?eks\\.",
    "[Ff]\\.[Kk]r\\.",
    "[Ff][.]?m\\.",
    "[Ff][.]?o[.]?f\\.",
    "[Ff][.]?o[.]?m\\.",
    "[Ff]\\.k\\.",
    "[Ff]\\.nr\\.",
    "[Ff]\\.t\\.",
    "[Ff]\\.ø\\.",
    "[Ff]\\.å\\.",
    "[Ff]\\.",
    "[Ff]eb\\.",
    "[Ff]f\\.",
    "[Ff]hv\\.",
    "[Ff]ig\\.",
    "[Ff]l\\.",
    "[Ff]lg\\.",
    "[Ff]oreg\\.",
    "[Ff]orf\\.",
    "[Ff]ork\\.",
    "[Ff]orts\\.",
    "[Ff]r\\.",
    "[Ff]ramh\\.",
    "[Ff]re\\.",
    "[Ff]rk\\.",
    "[Ff]ung\\.",
    "[Ff]v\\.",
    "[Ff]vt\\.",
    "[Gg][.]?m\\.",
    "[Gg]\\.",
    "[Gg]l\\.",
    "[Gg]no\\.",
    "[Gg]nr\\.",
    "[Gg]rl\\.",
    "[Gg]t\\.",
    "[Hh][.]?r\\.adv\\.",
    "[Hh]\\.v\\.",
    "[Hh]hv\\.",
    "[Hh]oh\\.",
    "[Hh]r\\.",
    "[Hh]vv\\.",
    "[Hh]å\\.",
    "[Ii][.]?e\\.",
    "[Ii]b\\.",
    "[Ii]bid\\.",
    "[Ii]fb\\.",
    "[Ii]fbm\\.",
    "[Ii]fm\\.",
    "[Ii]ft\\.",
    "[Ii]ht\\.",
    "[Ii]la\\.",
    "[Ii]ll\\.",
    "[Ii]ng\\.",
    "[Ii]nkl\\.",
    "[Ii]nnb\\.",
    "[Ii]nst\\.",
    "[Ii]stf\\.",
    "[Jj]an\\.",
    "[Jj]f\\.",
    "[Jj]fr\\.",
    "[Jj]nr\\.",
    "[Jj]r\\.",
    "[Jj]ul\\.",
    "[Jj]un\\.",
    "[Jj]ur\\.",
    "[Kk]ap\\.",
    "[Kk]fr\\.",
    "[Kk]gl[.]?res\\.",
    "[Kk]l\\.",
    "[Kk]omm\\.",
    "[Kk]st\\.",
    "[Kk]to\\.",
    "[Kk]v\\.",
    "[Ll][.]?c\\.",
    "L\\.",
    "[Ll]au\\.",
    "[Ll]ib\\.",
    "[Ll]nr\\.",
    "[Ll]oc\\.cit\\.",
    "[Ll]t\\.",
    "[Ll]ø\\.",
    "[Ll]ør\\.",
    "[Mm][.]?a[.]?o\\.",
    "[Mm][.]?a\\.",
    "[Mm][.]?m\\.",
    "[Mm][.]?o[.]?t\\.",
    "[Mm][.]?v\\.",
    "[Mm]ag[.]?art\\.",
    "[Mm]ag\\.",
    "[Mm]aks\\.",
    "[Mm]an\\.",
    "[Mm]ar\\.",
    "[Mm]ax\\.",
    "[Mm]d\\.",
    "[Mm]ed\\.",
    "Meld\\.",      #skal ikke ha liten forbokstav
    "[Mm]ek\\.",
    "[Mm]fl\\.",
    "[Mm]ht\\.",
    "[Mm]il\\.",
    "[Mm]ill\\.",
    "[Mm]in\\.",
    "[Mm]nd\\.",
    "[Mm]ob\\.",
    "[Mm]od\\.",
    "[Mm]oh\\.",
    "[Mm]r\\.",
    "[Mm]rd\\.",
    "[Mm]rs\\.",
    "[Mm]s\\.",
    "[Mm]tp\\.",
    "[Mm]uh\\.",
    "[Mm]va\\.",
    "[Mm]å\\.",
    "[Nn][.]?br\\.",
    "[Nn]\\.å\\.",
    "[Nn]df\\.",
    "[Nn]n\\.",
    "[Nn]o\\.",
    "[Nn]ov\\.",
    "[Nn]r\\.",
    "[Nn]to\\.",
    "[Nn]yno\\.",
    "[Oo][.]?a\\.",
    "[Oo]\\.l\\.",
    "[Oo]bs\\.",
    "[Oo]ff\\.",
    "[Oo]fl\\.",
    "[Oo]kt\\.",
    "[Oo]n\\.",
    "[Oo]ns\\.",
    "[Oo]p\\.cit\\.",
    "[Oo]p\\.",
    "[Oo]rg\\.nr\\.",
    "[Oo]sb\\.",
    "[Oo]sv\\.",
    "[Oo]t\\.prp\\.",
    "[Oo]vf\\.",
    "[Pp]\\.a\\.",
    "[Pp][.]?m\\.",
    "[Pp]\\.nr\\.",
    "[Pp][.]?p\\.",
    "[Pp]\\.[Ss]\\.",
    "[Pp][.]?t\\.",
    "[Pp]\\.",
    "[Pp]b\\.",
    "[Pp]ga\\.",
    "[Pp]h[.]?d\\.",
    "[Pp]harm\\.",
    "[Pp]hilol\\.",
    "[Pp]kt\\.",
    "[Pp]r\\.",
    "[Pp]rop\\.",
    "[Pp]st\\.",
    "R[.]?I[.]?P\\.",
    "[Rr]\\.",
    "[Rr]ed\\.anm\\.",
    "[Rr]ed\\.mrk\\.",
    "[Rr]ed\\.",
    "[Rr]ef\\.",
    "[Rr]eg\\.",
    "[Rr]ek\\.",
    "[Rr]es\\.kap\\.",
    "[Rr]es\\.",
    "[Rr]esp\\.",
    "[Rr]v\\.",
    "[Ss][.]?d\\.",
    "[Ss]\\.k\\.",
    "[Ss][.]?m\\.",
    "[Ss][.]?u\\.",
    "[Ss]\\.å\\.",
    "[Ss]\\.",
    "[Ss]ek\\.",
    "[Ss]en\\.",
    "[Ss]ep\\.",
    "[Ss]ign\\.",
    "[Ss]iv[.]?ing\\.",
    "[Ss]j\\.",
    "[Ss]ms\\.",
    "[Ss]os\\.øk\\.",
    "[Ss]os\\.",
    "[Ss]p\\.",
    "[Ss]pm\\.",
    "[Ss]r\\.",
    "[Ss]st\\.",
    "[Ss]t[.]?meld\\.",
    "[Ss]t[.]?prp\\.",
    "[Ss]t\\.",
    "[Ss]tip\\.",
    "[Ss]tk\\.",
    "[Ss]tp\\.",
    "[Ss]tr\\.",
    "[Ss]trpl\\.",
    "[Ss]tud\\.",
    "[Ss]tv\\.",
    "[Ss]v\\.",
    "[Ss]åk\\.",
    "[Ss]ø\\.",
    "[Ss]øn\\.",
    "[Tt][.]?d\\.",
    "[Tt][.]?o[.]?m\\.",
    "[Tt]\\.o\\.",
    "[Tt]ab\\.",
    "[Tt]echn\\.",
    "[Tt]emp\\.",
    "[Tt]i\\.",
    "[Tt]idl\\.",
    "[Tt]ils\\.",
    "[Tt]ilsv\\.",
    "[Tt]ir\\.",
    "[Tt]lf\\.",
    "[Tt]o\\.",
    "[Tt]or\\.",
    "[Tt]y\\.",
    "[Tt]vml\\.",
    "[Uu]lt\\.",
    "[Uu]tg\\.",
    "[Vv]\\.",
    "[Vv]edk\\.",
    "[Vv]edr\\.",
    "[Vv]it\\.ass\\.",
    "[Vv]g\\.",
    "[Vv]gs\\.",
    "[Vv]ha\\.",
    "[Vv]n\\.",
    "[Vv]ol\\.",
    "[Vv]s\\.",
    "[Vv]sa\\.",
    "[Åå]rg\\.",
    "[Åå]rh\\.",
]

"""Her er listen over forkortelser med punktum.

Hentet fra Wikipedia og Språkrådet med egendefinerte tillegg.
"""


"""Numeriske uttrykk
-----------------------------------------------------------------------------

Numeriske uttrykk er alt som er bygd opp av tall, komma og punktum og blanke.

LGJ: juni 2014
"""


num = r"\d+(?:\.(?!\s[A-ZÆØÅ]))?"
"""Tall som kan slutte på punktum består av hele tall, som tokeniseres
 med punktum bare om neste påfølgende tegn (etter blank) ikke er stor bokstav.

Denne må justeres for samisk og andre språk med større utvalg av store bokstaver.
Det vil sannsynligvis ikke ha så veldig stor betydning for utfallet.
"""


num0 = r"\d{1,3}(?:\s\d{3}(?!\d))+"
"""F.eks. 10 000, tillater ikke punktum. 

Tokeniserer tall med mellomrom der de forekommer.
"""


num1 = r"\d+(?:\.\d+)+"
"""Seksjon 3.2.1 eller 2.3999, kan ikke ha sluttpunktum."""


num2 = r"\d+,\d+"
"""3,5 kan ikke ha sluttpunktum."""


num3 = r"\.\d+"
"""Det var .2 prosent økning."""


num4 = r"\.{3,}"
"""Tre eller flere punktum blir ett token."""

num5 = r"\d+(?:[-–]\w+)"
"""Tallord kombinert med ord, f.eks. 1900-tallet"""

# TODO: kombiner til det regulære uttrykket num eller num0 eller...
num = "|".join([num0, num1, num2, num3, num4, num5, num])


parnum0 = r"(?<=§\s)\d+(?:[-–—]\d+)*|(?<=§)\d+(?:[-–—]\d+)*"
"""Paragraftegn kan komme i en eller to (eller flere?) utgaver.

Tolk tall etter § som rene tall uten punktum,
men også med bindestrek så i § 2-5  blir 2-5 et token.
"""

#parnum = r"(?<=§\s)\d+|(?<=§)\d+"
#"""Tolk tall etter § som heltall uten punktum."""


paragrafer = "§+"
"""§ eller §§ brukes i lovtekster."""


epost = r"\w+[-.+!#$%&'*/=?^(){}[\]\w]*@\w+[-.\w]*\.\w+"
"""E-post består av et brukernavn, fulgt av @ og et domene med punktum.

Brukernavnet må begynne på et alfanumerisk tegn, men kan
inneholde spesialtegn.

Domenet må begynne på et alfanumerisk tegn, men kan
inneholde bindestrek og punktum.
"""


url1 = r"(?:HTTPS?|https?|FTP|ftp)://\S+[-~/#[@$&(*+=%\w](?=[.,:;?!')\]\"]*(?:\s|$))"
"""URL som starter med http, https eller ftp. 

Kan bestå av hvilke som helst tegn, men siste tegn må være et alfanumerisk 
tegn eller et av de spesifiserte spesialtegnene. Følges av mulig tegnsetting 
og mellomrom eller linjeslutt.
"""

url2 = r"(?:WWW|www)\.\S+[-~/#[@$&(*+=%\w](?=[.,:;?!')\]\"]*(?:\s|$))"
"""URL som starter med www. 

Kan bestå av hvilke som helst tegn, men siste tegn må være et alfanumerisk 
tegn eller et av de spesifiserte spesialtegnene. Følges av mulig tegnsetting 
og mellomrom eller linjeslutt.
"""

url3 = r"[\w-]+\.[-.~:/?#[\]@!$&'()*+,;=%\w]+[-~/#[@$&(*+=%\w](?=[.,:;?!')\]\"]*(?:\s|$))"
"""Matcher gjenværende URL-er som ikke begynner med http, https, ftp eller www.

Må begynne med alfanumeriske tegn eller bindestrek og et punktum. Siste tegn må være
et alfanumerisk tegn eller et av de spesifiserte spesialtegnene. Følges av mulig 
tegnsetting og mellomrom eller linjeslutt.
"""

url = "|".join([url1, url2, url3])



initialer = r"(?<=(?:\s|\.))[A-ZÆØÅ]\."
word = r"\w+[-.@\w]*[\w]+-?"
word = "|".join([initialer, word])
"""Ord er alt som ikke inneholder skillende skilletegn.

Bindestrek og @ og lignende går inn i tokenet, punktum inkludert,
tar også med @ for mailadresser.
Bindestrek kan også avslutte ord som i "ord- og setningsdeling".
Andre tegn, som punktum og kolon i slutt, vil ikke tokeniseres sammen med ordet.
"""

catchall = r"\S"  # alle tegn som ikke er blanke blir til et eget token
"""Alle tegn som ikke er et blankt tegn
 (tab, mellomrom linjeskift osv.),
 og som ikke er blitt matchet opp tidligere,
 blir å regne som egne token.
"""


regex_pattern = fork + [epost, parnum0, num, paragrafer, url, word, catchall]    #parnum kommentert ut
regex_pattern = regex.compile("|".join(regex_pattern))
"""Kombiner alle uttrykkene i rekkefølge og kompiler dem.

Sjekk først om det er en forkortelse, ellers sjekk om det er et tall,
sjekk paragrafer, prøv å lag et ord. Hvis ikke noe av det her,
la tegnet være sitt eget token og gå videre.
"""


def tokenize_timer(text: str) -> list:
    """Time the :func:`tokenize` function and return the resulting tokens."""
    t0 = time.process_time()
    tokens = tokenize(text)
    t1 = time.process_time()
    t = t1 - t0
    print(f"tid: {t}")
    return tokens


def tokenize(text: str) -> list:
    """Tokenize the input ``text`` with the default ``regex`` pattern."""
    tokens = regex.findall(regex_pattern, text)
    return tokens


class Tokens:
    """Create a list of tokens from a text with :func:`tokenize`."""

    def __init__(self, text):
        self.tokens = tokenize(text)
        self.size = len(self.tokens)


if __name__ == "__main__":
    try:
        with open(sys.argv[1], "r", encoding="utf-8") as charfile:
            for token in tokenize(charfile.read()):
                print(token, "\n")
    except BaseException:
        print('Får ikke åpnet fila "%s"' % (sys.argv[1],))
