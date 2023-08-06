import json
from pathlib import Path
from typing import List

import pytest as pytest
from pyannotators_trfclassifier.trfclassifier import TrfClassifierAnnotator, TrfModel, TrfClassifierParameters, \
    ProcessingUnit
from pymultirole_plugins.v1.schema import Document, Sentence, DocumentList


@pytest.fixture
def expected_en():
    return [
        "I like you. I love you",
        "I hate you",
        "I'm scared"
    ]


@pytest.fixture
def expected_fr():
    return [
        "J'adore ce truc'",
        "Je film est nul",
        "Barthez est le meilleur gardien du monde."
    ]


def test_trfclassifier_english(expected_en):
    model = TrfClassifierAnnotator.get_model()
    model_class = model.construct().__class__
    assert model_class == TrfClassifierParameters
    annotator = TrfClassifierAnnotator()
    parameters = TrfClassifierParameters(model=TrfModel.distilbert_base_uncased_emotion)
    docs: List[Document] = annotator.annotate([Document(text=t) for t in expected_en], parameters)
    docs[0].categories[0].label == 'love'
    docs[1].categories[0].label == 'anger'
    docs[2].categories[0].label == 'fear'


def test_trfclassifier_english_segments(expected_en):
    annotator = TrfClassifierAnnotator()
    doc = Document(text="", sentences=[])
    start = 0
    for text in expected_en:
        doc.text += text + "\n"
        end = len(doc.text)
        doc.sentences.append(Sentence(start=start, end=end))
        start = end
    if doc.text:
        doc.text.rstrip()
        doc.sentences[-1].end -= 1
    parameters = TrfClassifierParameters(model=TrfModel.distilbert_base_uncased_finetuned_sst_2_english,
                                         processing_unit=ProcessingUnit.segment)
    docs: List[Document] = annotator.annotate([doc], parameters)
    docs[0].sentences[0].categories[0].label == 'POSITIVE'
    docs[0].sentences[1].categories[0].label == 'POSITIVE'
    docs[0].sentences[2].categories[0].label == 'NEGATIVE'


def test_trfclassifier_french(expected_fr):
    annotator = TrfClassifierAnnotator()
    parameters = TrfClassifierParameters(model=TrfModel.barthez_sentiment_classification)
    docs: List[Document] = annotator.annotate([Document(text=t) for t in expected_fr], parameters)
    docs[0].categories[0].label == 'Positive'
    docs[1].categories[0].label == 'Negative'
    docs[2].categories[0].label == 'Positive'


def test_trfclassifier_french_segments(expected_fr):
    annotator = TrfClassifierAnnotator()
    doc = Document(text="", sentences=[])
    start = 0
    for text in expected_fr:
        doc.text += text + "\n"
        end = len(doc.text)
        doc.sentences.append(Sentence(start=start, end=end))
        start = end
    if doc.text:
        doc.text.rstrip()
        doc.sentences[-1].end -= 1
    parameters = TrfClassifierParameters(model=TrfModel.bert_base_multilingual_uncased_sentiment,
                                         processing_unit=ProcessingUnit.segment)
    docs: List[Document] = annotator.annotate([doc], parameters)
    docs[0].sentences[0].categories[0].label == '5 stars'
    docs[0].sentences[1].categories[0].label == '1 star'
    docs[0].sentences[2].categories[0].label == '5 stars'


@pytest.mark.skip(reason="Not a test")
def test_trfclassifier_HM(expected_fr):
    # from sklearn.metrics import classification_report
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/kairntech_exemple.json')
    with source.open("r") as fin:
        docs = json.load(fin)
    docs = [Document(**doc) for doc in docs]
    annotator = TrfClassifierAnnotator()
    parameters = TrfClassifierParameters(model=TrfModel.barthez_sentiment_classification)
    docs: List[Document] = annotator.annotate(docs, parameters)
    dl = DocumentList(__root__=docs)
    result = Path(testdir, 'data/kairntech_exemple_sa.json')
    with result.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
