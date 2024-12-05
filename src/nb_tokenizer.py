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


fork = [
    "[Aa]/[Ss]",
    "[Aa]b\\.prov\\.",  
    "[Aa]plf\\.",
    "[Aa][.]?[Dd]\\.",
    "a[.]?l\\.",
    "a[.]?m\\.",
    "adm\\.dir\\.",
    "adm\\.",
    "adr\\.",
    "adv\\.",
    "aga\\.",
    "alt\\.",
    "ang\\.",
    "ank\\.",
    "apr\\.",
    "aq\\.",
    "ass\\.",
    "att\\.",
    "aug\\.",
    "aut\\.",
    "avd\\.",
    "avg\\.",
    "avst\\.",
    "[Bb]\\.[Cc]\\.",
    "bd\\.",
    "bed\\.øk\\.",
    "bet\\.",
    "bill\\.mrk\\.?",
    "bill\\.",
    "bl[.]?a\\.",
    "bm\\.",
    "bnr\\.",
    "bto\\.",
    "bvl\\.",
    "[Cc][.]?[Cc]\\.",
    "[Cc][Oo]\\.",
    "ca\\.",
    "cand\\.mag\\.",
    "cand\\.",
    "d[.]?d\\.",
    "d[.]?e\\.",
    "d[.]?m\\.",
    "d[.]?y\\.",
    "d[.]?s\\.",
    "d\\.å\\.",
    "d\\.",
    "dept\\.",
    "des\\.",
    "dfm\\.",
    "dg\\.",
    "dir\\.",
    "disp\\.",
    "div\\.",
    "do\\.",
    "dr\\.philos\\.",
    "[Dd]r\\.",
    "dss\\.",
    "dvs\\.",
    "[Ee]\\.[Kk]r\\.",
    "e[.]?l\\.",
    "e[.]?g\\.",
    "e\\.f\\.",
    "eig\\.",
    "eks\\.",
    "ekskl\\.",
    "eksp\\.",
    "et\\.",
    "etab\\.",
    "etabl\\.",
    "etc\\.",
    "ev\\.",
    "evt\\.",
    "ex\\.fac\\.",
    "ex\\.phil\\.",
    "[Ff][.]?eks\\.",
    "[Ff]\\.[Kk]r\\.",
    "f[.]?m\\.",
    "f[.]?o[.]?f\\.",
    "f[.]?o[.]?m\\.",
    "f\\.k\\.",
    "f\\.nr\\.",
    "f\\.t\\.",
    "f\\.ø\\.",
    "f\\.å\\.",
    "f\\.",
    "feb\\.",
    "ff\\.",
    "fhv\\.",
    "fig\\.",
    "fl\\.",
    "flg\\.",
    "foreg\\.",
    "forf\\.",
    "fork\\.",
    "forts\\.",
    "[Ff]r\\.",
    "framh\\.",
    "fre\\.",
    "[Ff]rk\\.",
    "fung\\.",
    "fv\\.",
    "fvt\\.",
    "g[.]?m\\.",
    "g\\.",
    "gl\\.",
    "gno\\.",
    "gnr\\.",
    "grl\\.",
    "gt\\.",
    "h[.]?r\\.adv\\.",
    "h\\.v\\.",
    "hhv\\.",
    "hoh\\.",
    "[Hh]r[.]?",
    "hvv\\.",
    "hå\\.",
    "i[.]?e\\.",
    "ib\\.",
    "ibid\\.",
    "ifb\\.",
    "ifbm\\.",
    "ifm\\.",
    "ift\\.",
    "iht\\.",
    "ila\\.",
    "ill\\.",
    "ing\\.",
    "inkl\\.",
    "innb\\.",
    "inst\\.",
    "istf\\.",
    "jan\\.",
    "[Jj]f\\.",
    "jfr\\.",
    "jnr\\.",
    "[Jj]r\\.",
    "jul\\.",
    "jun\\.",
    "jur\\.",
    "kap\\.",
    "kfr\\.",
    "kgl[.]?res\\.",
    "kl\\.",
    "komm\\.",
    "kst\\.",
    "kto\\.",
    "kv\\.",
    "L\\.",
    "l[.]?c\\.",
    "lau\\.",
    "lib\\.",
    "lnr\\.",
    "loc\\.cit\\.",
    "lt\\.",
    "lø\\.",
    "lør\\.",
    "m[.]?a[.]?o\\.",
    "m[.]?a\\.",
    "m[.]?m\\.",
    "m\\.o\\.t\\.?",
    "m\\.\s*v\\.",
    "mag[.]?art\\.",
    "mag\\.",
    "maks\\.",
    "man\\.",
    "mar\\.",
    "max\\.",
    "md\\.",
    "med\\.",
    "Meld\\.",
    "mek\\.",
    "mfl\\.",
    "mht\\.",
    "mil\\.",
    "mill\\.",
    "min\\.",
    "mnd\\.",
    "mob\\.",
    "mod\\.",
    "moh\\.",
    "[Mm]r\\.",
    "mrd\\.",
    "[Mm]rs\\.",
    "[Mm]s\\.",
    "mtp\\.",
    "muh\\.",
    "mv\\.",
    "mva\\.",
    "må\\.",
    "n[.]?br\\.",
    "n\\.å\\.",
    "ndf\\.",
    "nn\\.",
    "no\\.",
    "nov\\.",
    "nr\\.",
    "nto\\.",
    "nyno\\.",
    "o[.]?a\\.",
    "o\\.l\\.",
    "obs\\.",
    "off\\.",
    "ofl\\.",
    "okt\\.",
    "on\\.",
    "ons\\.",
    "op\\.",
    "org\\.nr\\.",
    "osb\\.",
    "osv\\.",
    "ot\\.prp\\.",
    "ovf\\.",
    "p\\.a\\.",
    "p[.]?m\\.",
    "p\\.nr\\.",
    "p[.]?p\\.",
    "[Pp]\\.[Ss]\\.",
    "p[.]?t\\.",
    "p\\.",
    "pb\\.",
    "pga\\.",
    "ph[.]?d\\.",
    "pharm\\.",
    "philol\\.",
    "pkt\\.",
    "pr\\.",
    "prop\\.",
    "pst\\.",
    "R[.]?I[.]?P\\.",
    "r\\.",
    "red\\.anm\\.",
    "red\\.mrk\\.",
    "red\\.",
    "ref\\.",
    "reg\\.",
    "rek\\.",
    "res\\.kap\\.",
    "res\\.",
    "resp\\.",
    "rv\\.",
    "s[.]?d\\.",
    "s\\.k\\.",
    "s[.]?m\\.",
    "s[.]?u\\.",
    "s\\.å\\.",
    "s\\.",
    "sek\\.",
    "sen\\.",
    "sep\\.",
    "sign\\.",
    "siv[.]?ing\\.",
    "sj\\.",
    "sms\\.",
    "sos\\.øk\\.",
    "sos\\.",
    "sp\\.",
    "spm\\.",
    "[Ss]r\\.",
    "sst\\.",
    "st[.]?meld\\.",
    "st[.]?prp\\.",
    "[Ss]t\\.",
    "stip\\.",
    "stk\\.",
    "stp\\.",
    "str\\.",
    "strpl\\.",
    "stud\\.",
    "stv\\.",
    "sv\\.",
    "såk\\.",
    "sø\\.",
    "søn\\.",
    "t[.]?d\\.",
    "t\\.o\\.m[.]?",
    "t\\.o\\.",
    "tab\\.",
    "techn\\.",
    "temp\\.",
    "ti\\.",
    "tidl\\.",
    "tils\\.",
    "tilsv\\.",
    "tir\\.",
    "tlf\\.",
    "to\\.",
    "tor\\.",
    "ty\\.",
    "tvml\\.",
    "ult\\.",
    "utg\\.",
    "v\\.",
    "vedk\\.",
    "vedr\\.",
    "vit\\.ass\\.",
    "vg\\.",
    "vgs\\.",
    "vha\\.",
    "vn\\.",
    "vol\\.",
    "vs\\.",
    "vsa\\.",
    "årg\\.",
    "årh\\.",
]

"""Her er listen over forkortelser med punktum.

Hentet fra Wikipedia og Språkrådet med egendefinerte tillegg.
"""


"""Numeriske uttrykk
-----------------------------------------------------------------------------

Numeriske uttrykk er alt som er bygd opp av tall, komma og punktum og blanke.

LGJ: juni 2014
"""


num = r"\d+(?:\.(?! [A-ZÆØÅ]))?"
"""Tall som kan slutte på punktum består av hele tall, som tokeniseres
 med punktum bare om neste påfølgende tegn (etter blank) ikke er stor bokstav.

Denne må justeres for samisk og andre språk med større utvalg av store bokstaver.
Det vil sannsynligvis ikke ha så veldig stor betydning for utfallet.
"""


num0 = r"\d{1,3}(?:\s\d\d\d(?!\d))+"
"""F.eks. 10 000, tillater ikke punktum. 

Tokeniserer tall med mellomrom der de forekommer.
"""


num1 = r"\d+(?:\.\d+)+"
"""Seksjon 3.2.1 eller 2.3999, kan ikke ha sluttpunktum."""


num2 = r"\d+,\d+"
"""3,5 kan ikke ha sluttpunktum."""


num3 = r"\.\d+"
"""Det var .2 prosent økning."""


num4 = r"\.\.\.+"
"""Tre eller flere punktum blir ett token."""

num5 = r"\d+(?:[-–]\w+)"
"""Tallord kombinert med ord, f.eks. 1900-tallet"""

# TODO: kombiner til det regulære uttrykket num eller num0 eller...
num = "|".join([num0, num1, num2, num3, num4, num5, num])


parnum0 = r"(?<=§ )\d+(?:[-–—]\d+)*|(?<=§)\d+(?:[-–—]\d+)*"
"""Paragraftegn kan komme i en eller to (eller flere?) utgaver.

Tolk tall etter § som rene tall uten punktum,
men også med bindestrek så i § 2-5  blir 2-5 et token.
"""


parnum = r"(?<=§ )\d+|(?<=§)\d+"
"""Tolk tall etter § som heltall uten punktum."""

paragrafer = "§+"
"""§ eller §§ brukes i lovtekster."""


initialer = r"(?<=(?: |\.))[A-ZÆØÅ]\."
word = r"\w+[-\d.@\w]*[\w\d]+-?"
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


regex = fork + [parnum0, parnum, num, paragrafer, word, catchall]
regex = re.compile("|".join(regex))
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
    tokens = re.findall(regex, text)
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
