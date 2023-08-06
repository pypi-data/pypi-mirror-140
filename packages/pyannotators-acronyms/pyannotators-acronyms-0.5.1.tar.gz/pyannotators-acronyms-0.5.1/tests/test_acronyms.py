import json
import logging
from pathlib import Path
from typing import List

import pytest
from pyannotators_acronyms.acronyms import AcronymsAnnotator, AcronymsParameters
from pymultirole_plugins.v1.schema import Document, Sentence, DocumentList

testdir = Path(__file__).parent
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level="INFO",
    handlers=[logging.FileHandler(testdir / "tests.log"), logging.StreamHandler()],
)


def test_acronyms():
    sents = [
        "Les technologies de l'information et de la communication (TIC) prennent diverses formes : Internet, ordinateur, téléphone portable, modem, progiciels, etc.",
        "Les représentants du MoDem (Mouvement Démocrate) à la région, élus en 2015 sur la liste de M. Wauquiez, avaient annoncé en mars qu'ils quittaient la majorité, sans pour autant rejoindre l'opposition.",
        "Y compris dans la majorité, la vice-présidente du groupe LREM (La République En Marche) Sophie Beaudouin-Hubière a écrit au Premier ministre LREM Jean Castex pour dénoncer une décision d'autant plus injuste que les règles de distanciation ont été bien respectées DANS ces commerces.",
        "La vice-présidente Les Républicains (LR) de l'Assemblée nationale Annie Genevard a aussi pointé le désarroi des petits commerçants, la situation accentuant le risque réel de dépérissement de nos centres-villes.",
        "Aide directe ou préfinancement du CESU ? Cette aide peut prendre la forme, en pratique, d'une aide financière directe versée aux salariés ou de chèques emploi-service universel (CESU).",
        "Exonération ZRR et ZRU : nouveaux formulaires \n\nLes embauches effectuées dans les zones de revitalisation rurale (ZRR) et de redynamisation urbaine (ZRU)",
        "L'employeur doit inviter les syndicats intéressés à négocier le protocole d'accord préélectoral en vue de l'élection d'un comité social et économique (CSE).",
    ]
    text = ""
    sentences = []
    for sent in sents:
        sstart = len(text)
        text += sent + "\n\n"
        send = len(text)
        sentences.append(Sentence(start=sstart, end=send))
    doc = Document(text=text, sentences=sentences)
    annotator = AcronymsAnnotator()
    parameters = AcronymsParameters(model="fr")
    docs: List[Document] = annotator.annotate([doc], parameters)
    doc0 = docs[0]
    assert len(doc0.annotations) == 17


@pytest.mark.skip(reason="Not a test")
def test_acronyms_rf():
    testdir = Path(__file__).parent / "data"
    json_file = testdir / "grouperf-export-search.json"
    with json_file.open("r") as fin:
        docs = json.load(fin)
    docs = [Document(**doc) for doc in docs]
    annotator = AcronymsAnnotator()
    parameters = AcronymsParameters(model="fr")
    for i, doc100 in enumerate(chunks(docs)):
        result: List[Document] = annotator.annotate(doc100, parameters)
        dl = DocumentList(__root__=result)
        result_file = testdir / f"grouperf-export-acro{i}.json"
        with result_file.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


def chunks(seq, size=100):  # noqa
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))
