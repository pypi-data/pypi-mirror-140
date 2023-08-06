import json
from pathlib import Path
from typing import List

import pytest as pytest
from pyannotators_zeroshotclassifier.zeroshotclassifier import ZeroShotClassifierAnnotator, \
    ZeroShotClassifierParameters, TrfModel, ProcessingUnit
from pymultirole_plugins.v1.schema import Document, Sentence, DocumentList


@pytest.fixture
def expected_en():
    return {
        'sport': "The french team is going to win Euro 2021 football tournament",
        'politics': "Who are you voting for in 2021?",
        'science': "Coronavirus vaccine research are progressing"
    }


@pytest.fixture
def expected_fr():
    return {
        'sport': "L'équipe de France joue aujourd'hui au Parc des Princes",
        'politique': "Les élections régionales auront lieu en Juin 2021",
        'science': "Les recherches sur le vaccin du Coronavirus avancent bien"
    }


def test_zeroshotclassifier_english(expected_en):
    model = ZeroShotClassifierAnnotator.get_model()
    model_class = model.construct().__class__
    assert model_class == ZeroShotClassifierParameters
    annotator = ZeroShotClassifierAnnotator()
    parameters = ZeroShotClassifierParameters(model=TrfModel.distilbert_base_uncased_mnli,
                                              candidate_labels=','.join(expected_en.keys()),
                                              multi_label=True)
    docs: List[Document] = annotator.annotate([Document(text=t) for t in expected_en.values()], parameters)
    for expected_label, doc in zip(expected_en.keys(), docs):
        assert doc.categories[0].label == expected_label


def test_zeroshotclassifier_english_segments(expected_en):
    model = ZeroShotClassifierAnnotator.get_model()
    model_class = model.construct().__class__
    assert model_class == ZeroShotClassifierParameters
    annotator = ZeroShotClassifierAnnotator()
    doc = Document(text="", sentences=[])
    start = 0
    for text in expected_en.values():
        doc.text += text + "\n"
        end = len(doc.text)
        doc.sentences.append(Sentence(start=start, end=end))
        start = end
    if doc.text:
        doc.text.rstrip()
        doc.sentences[-1].end -= 1
    parameters = ZeroShotClassifierParameters(model=TrfModel.distilbert_base_uncased_mnli,
                                              candidate_labels=','.join(expected_en.keys()),
                                              processing_unit=ProcessingUnit.segment,
                                              multi_label=True)
    docs: List[Document] = annotator.annotate([doc], parameters)
    for expected_label, sent in zip(expected_en.keys(), docs[0].sentences):
        assert sent.categories[0].label == expected_label


def test_zeroshotclassifier_french(expected_fr):
    model = ZeroShotClassifierAnnotator.get_model()
    model_class = model.construct().__class__
    assert model_class == ZeroShotClassifierParameters
    annotator = ZeroShotClassifierAnnotator()
    parameters = ZeroShotClassifierParameters(model=TrfModel.camembert_base_xnli,
                                              candidate_labels=','.join(expected_fr.keys()),
                                              multi_label=True)
    docs: List[Document] = annotator.annotate([Document(text=t) for t in expected_fr.values()], parameters)
    for expected_label, doc in zip(expected_fr.keys(), docs):
        assert doc.categories[0].label == expected_label


def test_zeroshotclassifier_french_segments(expected_fr):
    model = ZeroShotClassifierAnnotator.get_model()
    model_class = model.construct().__class__
    assert model_class == ZeroShotClassifierParameters
    annotator = ZeroShotClassifierAnnotator()
    doc = Document(text="", sentences=[])
    start = 0
    for text in expected_fr.values():
        doc.text += text + "\n"
        end = len(doc.text)
        doc.sentences.append(Sentence(start=start, end=end))
        start = end
    if doc.text:
        doc.text.rstrip()
        doc.sentences[-1].end -= 1
    parameters = ZeroShotClassifierParameters(model=TrfModel.camembert_base_xnli,
                                              candidate_labels=','.join(expected_fr.keys()),
                                              processing_unit=ProcessingUnit.segment,
                                              multi_label=True)
    docs: List[Document] = annotator.annotate([doc], parameters)
    for expected_label, sent in zip(expected_fr.keys(), docs[0].sentences):
        assert sent.categories[0].label == expected_label


@pytest.mark.skip(reason="Not a test")
def test_zeroshotclassifier_HM(expected_fr):
    from sklearn.metrics import classification_report
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/kairntech_exemple.json')
    with source.open("r") as fin:
        docs = json.load(fin)
    docs = [Document(**doc) for doc in docs]
    y_true = [doc.metadata['Thème'] for doc in docs]
    annotator = ZeroShotClassifierAnnotator()
    parameters = ZeroShotClassifierParameters(model=TrfModel.camembert_base_xnli,
                                              candidate_labels="Apprentissage et éducation,Arts et culture,Complexité et incertitude,Innovation et créativité,La générosité,La mort,La motivation,L'amour,La technologie et ses usages,La violence,Les émotions et notre cognition,Les intersections,Les mouvements migratoires,Les réseaux sociaux,Le temps,L'inattendu dans nos interactions,L'individu et l'appartenance à un collectif,Ma théorie,Mondialisation et circuits courts,Nature et environnement,Résilience et adaptabilité,Santé et bien-être,Surconsommation et ressources naturelles,Travail et modes de vie,Urbanisme et ruralité,Valeur et perception,Vie collective (bien commun - démocratie - solidarité)",
                                              multi_label=False, multi_label_threshold=0.2)
    docs: List[Document] = annotator.annotate(docs, parameters)
    y_pred = [doc.categories[0].label for doc in docs]
    print(classification_report(y_true, y_pred))
    dl = DocumentList(__root__=docs)
    result = Path(testdir, 'data/kairntech_exemple_zeroed.json')
    with result.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
