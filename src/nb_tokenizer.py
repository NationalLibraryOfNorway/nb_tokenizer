#!/usr/bin/ python3
# -*- coding: utf-8 -*-

"""
Tokenisator for ngramleser (evt. parsing).
-------------------------------------------
Lars G Johnsen, Nasjonalbiblioteket, juni 2014
Marie Iversdatter Røsok, Nasjonalbiblioteket, januar 2025

Tokenisatorens oppgave er å danne token eller ord fra en sekvens med tegn.
I utgangspunktet fungerer skilletegn og mellomrom som ordgrenser,
men det er unntak, se listen nedenfor. Skilletegn danner som oftest egne token,
men spesielt punktum og komma brukes på flere måter, noe det må tas høyde for.

Noen ord (token) har bestanddeler i form av skilletegn, som forkortelser, tall,
i tillegg kan ordene selv være bundet sammen med bindestrek:

p-pille (bindestrek)
3.3 (punktum i seksjonsnummerering)
etc. (forkortelser)
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

Paragraftegn § kan sekvensieres, så § og §§ vil være egne tokener;
de benyttes en hel del i lovtekster for entall og flertall.

Tall som følger etter § (adskilt med maks ett mellomrom)
vil aldri tiltrekke seg punktum.

Skilletegn og andre spesialtegn kan være del av e-poster eller URL-er som
skal tolkes som ett token, med mindre visse skilletegnet kommer på slutten
av strengen, da skilles det ut som eget token.
user123!@domain.com (tall, !,  @, og . inngår i tokenet)
https://example.com/path?key=value&Key=Value/ (:, /, ., ?, = og & inngår i tokenet)
https://example.com/resource . (punktum på slutten av URL er eget token)

Ellers utgjør alle skilletegn egne token, og øvrige tegn som ikke passer
inn med mønstrene over behandles som separate token.
"""



import re
import sys
import time



"""Forkortelser
-----------------------------------------------------------------------------

Liste over forkortelser med punktum.

Hentet fra Wikipedia, Språkrådet og Korrekturavdelingen med egendefinerte tillegg.

Lista inkluderer forkortelser for navn, som i Jens Chr. Gundersen.
Lista unngår navneforkortelser som også kan være fullendte navn på slutten
av setning, som "Alex.", "Fred.", "Holm." etc.
TODO: legge til flere navneforkortelser etter hvert som man kommer over dem.
"""

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
    "Chr?\\.",
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
    "ila\\.",
    "[Ii]ll\\.",
    "[Ii]ng\\.",
    "[Ii]nkl\\.",
    "[Ii]nnb\\.",
    "[Ii]nst\\.",
    "[Ii]stf\\.",
    "jan\\.",
    "[Jj]f\\.",
    "[Jj]fr\\.",
    "[Jj]nr\\.",
    "[Jj]r\\.",
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
    "[Mm]ar\\.",
    "[Mm]ax\\.",
    "[Mm]d\\.",
    "Meld\\.",
    "[Mm]ek\\.",
    "[Mm]fl\\.",
    "[Mm]ht\\.",
    "[Mm]ill\\.",
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
    "Sch\\.",
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
    "Ths?\\.",
    "[Tt]idl\\.",
    "[Tt]ils\\.",
    "[Tt]ilsv\\.",
    "[Tt]ir\\.",
    "[Tt]lf\\.",
    "[Tt]or\\.",
    "Tr\\.",
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
    "Werg\\.",
    "Wilh\\.",
    "[Åå]rg\\.",
    "[Åå]rh\\.",
]



"""Numeriske uttrykk
-----------------------------------------------------------------------------

Numeriske uttrykk er alt som er bygd opp av tall, komma, punktum og bindestrek.
"""

num1 = r"\d+(?:\.(?!\s[A-ZÆØÅÁÂÄČĐÉÏŊÖŠŦŽÞÐÇĞİÖŞÜȚȘĎĚŇŘŤÚŮĄĆĘŁŃÓŚŹŻŐŰĆ]))?"
"""Tall som kan slutte på punktum består av hele tall, som tokeniseres
 med punktum bare om neste påfølgende tegn (etter blank) ikke er stor bokstav.
"""

#num0 = r"\d{1,3}(?:\s\d{3}(?!\d))+"
#"""F.eks. 10 000, tillater ikke punktum.
#Tokeniserer tall med mellomrom der de forekommer.
#"""

num2 = r"\d+(?:\.\d+)+"
"""Seksjon 3.2.1 eller 2.3999, kan ikke ha sluttpunktum."""

num3 = r"\d+,\d+"
"""3,5 kan ikke ha sluttpunktum."""

num4 = r"\.\d+"
"""Det var .2 prosent økning."""

num5 = r"\d+(?:[-–]\w+)"
"""Tallord kombinert med ord, f.eks. 1900-tallet"""

parnum = r"(?<=§\s)\d+(?:[-–—]\d+)*|(?<=§)\d+(?:[-–—]\d+)*"
"""Tolk tall etter § som rene tall uten punktum,
men også med bindestrek så i § 2-5 blir 2-5 et token.
"""

num = "|".join([parnum, num2, num3, num4, num5, num1])



"""Tegn
-----------------------------------------------------------------------------

Sekvenser av tegn som skal tolkes som ett token, gjelder ellipse (tre eller
flere punktum) og sekvenser av paragraftegn §.
"""

ellipse = r"\.{3,}"
"""Tre eller flere punktum blir ett token."""

paragrafer = r"§+"
"""§ eller §§ brukes i lovtekster.
Paragraftegn kan komme i en eller to (eller flere?) utgaver.
"""



"""E-poster og URL-er
-----------------------------------------------------------------------------

E-poster og URL-er er strenger med kombinasjoner av bokstaver, tall og 
spesialtegn som skal tolkes som ett token.
"""

epost = r"\w+[-.+!#$%&'*/=?^(){}[\]\w]*@\w+[-.\w]*\.\w+"
"""E-post består av et brukernavn, fulgt av @ og et domene med punktum.

Brukernavnet må begynne på et alfanumerisk tegn, men kan
inneholde spesialtegn. Domenet må begynne på et alfanumerisk tegn,
men kan inneholde bindestrek og punktum.
"""

url1 = r"(?:HTTPS?|https?|FTP|ftp)://\S+[-~/#@$&*+=\w](?=[.,:;?!')\]\"]*(?:\s|$))"
"""URL som starter med http://, https:// eller ftp://.

Kan inneholde hvilke som helst tegn, men siste tegn må være et av de spesifiserte
spesialtegnene eller et alfanumerisk tegn. Følges av mulig tegnsetting og
mellomrom eller linjeslutt.
"""

url2 = r"(?:WWW|www)\.\S+[-~/#@$&*+=\w](?=[.,:;?!')\]\"]*(?:\s|$))"
"""URL som starter med www.

Kan inneholde hvilke som helst tegn, men siste tegn må være et av de spesifiserte
spesialtegnene eller et alfanumerisk tegn. Følges av mulig tegnsetting
og mellomrom eller linjeslutt.
"""

url3 = r"[\w-]+\.[-.~:/?#[\]@!$&'()*+,;=%\w]+[-~/#@$&*+=\w](?=[.,:;?!')\]\"]*(?:\s|$))"
"""Matcher gjenværende URL-er som ikke begynner med http, https, ftp eller www. URL-en
må begynne med alfanumeriske tegn eller bindestrek, fulgt av et punktum.

Kan inneholde spesialtegn og alfanumeriske tegn. Siste tegn må være et av de spesifiserte
spesialtegnene eller et alfanumerisk tegn. Følges av mulig tegnsetting og mellomrom
eller linjeslutt.
"""

url = "|".join([url1, url2, url3])



"""Initialer
-----------------------------------------------------------------------------

Initialer er enslige, store bokstaver med punktum som skal tolkes som ett token.
Gjelder også flere initialer på rad uten mellomrom.
"""

initialer = r"\b(?:[A-ZÆØÅÁÂÄČĐÉÏŊÖŠŦŽÞÐÇĞİÖŞÜȚȘĎĚŇŘŤÚŮĄĆĘŁŃÓŚŹŻŐŰĆ]\.)+(?=\W)"
"""(Sekvenser av) initial og punktum tokeniseres sammen: H.C. Andersen.
"""



word = r"\w+[-.@\w]*[\w]+-?"
"""Ord er alt som ikke inneholder skillende skilletegn.

Bindestrek, @ og punktum går inn i tokenet.
Bindestrek kan også avslutte ord som i "ord- og setningsdeling".
Andre tegn, som punktum og kolon i slutt, vil ikke tokeniseres sammen med ordet.

TODO: vurder å justere hvilke tegn som skal være tillatt i ord, og om @ skal
fjernes (e-poster håndteres av egen regex), eller andre tegn legges til
(f.eks. apostrof).
"""


catchall = r"\S"  # alle tegn som ikke er blanke blir til et eget token
"""Alle tegn som ikke er et blankt tegn (tab, mellomrom, linjeskift osv.),
og som ikke er blitt matchet opp tidligere, blir å regne som egne token.
"""


regex_pattern = fork + [epost, num, ellipse, paragrafer, url, initialer, word, catchall]
regex_pattern = re.compile("|".join(regex_pattern))
"""Kombiner alle uttrykkene i rekkefølge og kompiler dem.

Sjekk først om det er en forkortelse.
Sjekk om det er en e-post (fordi e-poster kan begynne med tall), ellers
sjekk om det er et tall, sjekk ellipse og paragrafer, sjekk URL-er, sjekk initialer,
prøv å lage et ord. Hvis ikke noe av det her, la tegnet være sitt eget token og gå videre.
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
    """Tokenize the input ``text`` with the default ``regex_pattern``."""
    tokens = re.findall(regex_pattern, text)
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
