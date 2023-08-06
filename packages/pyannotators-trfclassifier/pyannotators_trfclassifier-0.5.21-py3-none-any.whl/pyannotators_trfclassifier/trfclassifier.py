import os
import re
from enum import Enum
from functools import lru_cache
from math import floor
from typing import Type, List, cast, Union, Dict

import icu as icu
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.annotator import AnnotatorParameters, AnnotatorBase
from pymultirole_plugins.v1.schema import Document, Category, Sentence
from transformers import pipeline, TextClassificationPipeline

_home = os.path.expanduser('~')
xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or os.path.join(_home, '.cache')


class TrfModel(str, Enum):
    bert_base_multilingual_uncased_sentiment = 'nlptown/bert-base-multilingual-uncased-sentiment'
    distilbert_base_uncased_finetuned_sst_2_english = 'distilbert-base-uncased-finetuned-sst-2-english'
    barthez_sentiment_classification = 'moussaKam/barthez-sentiment-classification'
    distilbert_base_uncased_emotion = 'bhadresh-savani/distilbert-base-uncased-emotion'


class ProcessingUnit(str, Enum):
    document = 'document'
    segment = 'segment'


class TrfClassifierParameters(AnnotatorParameters):
    model: TrfModel = Field(TrfModel.bert_base_multilingual_uncased_sentiment,
                            description="""Which [Transformers model)(
                            https://huggingface.co/models?pipeline_tag=text-classification) fine-tuned
                            for Text classification to use, can be one of:<br/>
                            <li>`nlptown/bert-base-multilingual-uncased-sentiment`: This a bert-base-multilingual-uncased model finetuned for sentiment analysis on product reviews in six languages: English, Dutch, German, French, Spanish and Italian. It predicts the sentiment of the review as a number of stars (between 1 and 5).
                            <li>`distilbert-base-uncased-finetuned-sst-2-english`: This model is a fine-tune checkpoint of DistilBERT-base-uncased, fine-tuned on SST-2. It predicts a binary sentiment polarity POSITIVE/NEGATIVE.
                            <li>`moussaKam/barthez-sentiment-classification`: The BARThez model was proposed in BARThez: a Skilled Pretrained French Sequence-to-Sequence Model by Moussa Kamal Eddine, Antoine J.-P. Tixier, Michalis Vazirgiannis on 23 Oct, 2020. It predicts a binary sentiment polarity Positive/Negative.
                            <li>`bhadresh-savani/distilbert-base-uncased-emotion`: Distilbert-base-uncased finetuned on the emotion dataset. It predicts an emotion among a list of 6 (joy, sadness, love, anger, fear, surprise).
                            """)
    processing_unit: ProcessingUnit = Field(ProcessingUnit.document,
                                            description="""The processing unit to apply the classification in the input
                                            documents, can be one of:<br/>
                                            <li>`document`
                                            <li>`segment`""")
    # candidate_labels: str = Field("sport,politics,science",
    #                               description="""The comma-separated list of possible class labels to classify
    #                                     each sequence into. For example `\"sport,politics,science\"`""")
    # multi_label: bool = Field(False, description="Whether or not multiple candidate labels can be true.")
    # multi_label_threshold: float = Field(0.5,
    #                                      description="If multi-label you can set the threshold to make predictions.")
    # hypothesis_template: Optional[str] = Field(None,
    #                                            description="""The template used to turn each label into an NLI-style
    #                                            hypothesis. This template must include a {} for the
    #                                            candidate label to be inserted into the template. For
    #                                            example, the default template in english is
    #                                            `\"This example is {}.\"`""")


MAX_LENGTH_BUG = int(floor(10 ** 30 + 1))


class TrfClassifierAnnotator(AnnotatorBase):
    """[🤗 Transformers](https://huggingface.co/transformers/index.html) text classifier.
    """

    # cache_dir = os.path.join(xdg_cache_home, 'trankit')

    def annotate(self, documents: List[Document], parameters: AnnotatorParameters) \
            -> List[Document]:
        params: TrfClassifierParameters = \
            cast(TrfClassifierParameters, parameters)
        # Create cached pipeline context with model
        p: TextClassificationPipeline = get_pipeline(params.model)
        model_max_length = p.tokenizer.model_max_length \
            if (p.tokenizer.model_max_length and p.tokenizer.model_max_length < MAX_LENGTH_BUG) else 512
        if params.processing_unit == ProcessingUnit.document:
            dtexts = [document.text for document in documents]
            results = p(dtexts, truncation=True, max_length=model_max_length)
            for doc, result in zip(documents, results):
                doc.categories = compute_categories(result)
        else:
            for document in documents:
                if not document.sentences:
                    document.sentences = [Sentence(start=0, end=len(document.text))]
                stexts = [document.text[s.start:s.end] for s in document.sentences]
                results = p(stexts, truncation=True, max_length=model_max_length)
                for sent, result in zip(document.sentences, results):
                    sent.categories = compute_categories(result)
        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return TrfClassifierParameters


def compute_categories(result: Union[List[Dict], Dict]) -> List[Category]:
    cats: List[Category] = []
    rmax = max(result, key=lambda x: x['score']) if isinstance(result, List) else result
    cats.append(Category(label=rmax['label'], score=rmax['score']))
    return cats


@lru_cache(maxsize=None)
def get_pipeline(model):
    p = pipeline("text-classification", model=model.value)
    return p


nonAlphanum = re.compile(r'[\W]+', flags=re.ASCII)
underscores = re.compile("_{2,}", flags=re.ASCII)
trailingAndLeadingUnderscores = re.compile(r"^_+|_+\$", flags=re.ASCII)
# see http://userguide.icu-project.org/transforms/general
transliterator = icu.Transliterator.createInstance(
    "Any-Latin; NFD; [:Nonspacing Mark:] Remove; NFC; Latin-ASCII; Lower;", icu.UTransDirection.FORWARD)


def sanitize_label(string):
    result = transliterator.transliterate(string)
    result = re.sub(nonAlphanum, "_", result)
    result = re.sub(underscores, "_", result)
    result = re.sub(trailingAndLeadingUnderscores, "", result)
    return result
