import logging
from functools import lru_cache
from typing import Type, List, cast, Union, Iterable

import spacy
from collections_extended import RangeMap
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.annotator import AnnotatorParameters, AnnotatorBase
from pymultirole_plugins.v1.schema import Document, Span, Annotation, Term
from spacy.cli.download import download_model, get_compatibility, get_version
from spacy.errors import OLD_MODEL_SHORTCUTS
from spacy.language import Language
from spacy.matcher import Matcher
from unidecode import unidecode
from wasabi import msg

logger = logging.getLogger(__name__)


class AcronymsParameters(AnnotatorParameters):
    model: str = Field(
        "en_core_web_sm",
        description="Name of the [spacy model](https://spacy.io/models) to use for NER extraction",
    )
    short_label: str = Field(
        "Acronym", description="Label of the annotation for the short form of acronyms"
    )
    long_label: str = Field(
        "Expanded",
        description="Label of the annotation for the expanded form of acronyms",
    )
    propagate: bool = Field(
        True, description="Propagate acronyms to the whole document"
    )
    max_size: int = Field(6, description="Maximum size of acronyms")


class AcronymsAnnotator(AnnotatorBase):
    """Acronyms annotator."""

    def annotate(
        self, documents: List[Document], parameters: AnnotatorParameters
    ) -> List[Document]:
        params: AcronymsParameters = cast(AcronymsParameters, parameters)
        # Create parsing context with time and language information
        nlp, matcher = get_nlp(params.model, params.max_size)
        for document in documents:
            document.annotations = []
            if not document.sentences:
                document.sentences = [Span(start=0, end=len(document.text))]

            sents_stexts = []
            for s in document.sentences:
                if s.end > s.start:
                    sents_stexts.append((s, document.text[s.start : s.end]))
            sents, stexts = zip(*sents_stexts)
            docs = nlp_clean(nlp, stexts)
            acro_dict = {}
            for sent, doc in zip(sents, docs):
                matches = matcher(doc)
                seen_offsets = RangeMap()
                sorted_matches = sorted(matches, key=get_sort_key, reverse=True)
                for match_id, start, end in sorted_matches:
                    acro_def = matcher.vocab[match_id].text
                    acro_span = doc[start:end]
                    long = None
                    acro = None
                    long_text = None
                    if (
                        seen_offsets.get(start) is None
                        and seen_offsets.get(end - 1) is None
                    ):
                        seen_offsets[start:end] = acro_def
                        if acro_def == "long2short":
                            acro = acro_span[2]
                            long = resolve_longform(
                                acro_def,
                                acro,
                                doc[max(0, start - 2 * params.max_size) : start + 1],
                            )
                            long_text = long.text if long else None
                        elif acro_def == "short2long":
                            acro = acro_span[0]
                            long = resolve_longform(acro_def, acro, acro_span[2:])
                            long_text = long.text if long else None
                        elif acro_def == "short":
                            acro = acro_span[0]
                            if params.propagate:
                                if acro.text in acro_dict:
                                    long_text = acro_dict[acro.text]
                                    logger.info(f"Propagate {acro.text}={long_text}")
                            else:
                                long_text = None
                        if acro and long_text:
                            start = sent.start + acro.idx
                            end = start + len(acro)
                            document.annotations.append(
                                Annotation(
                                    start=start,
                                    end=end,
                                    label=params.short_label,
                                    text=document.text[start:end],
                                    terms=[
                                        Term(
                                            identifier=acro.text,
                                            lexicon="acronyms",
                                            preferredForm=long_text,
                                        )
                                    ],
                                )
                            )
                        if long:
                            logger.info(f"Found {acro.text}={long.text}")
                            acro_dict[acro.text] = long.text
                            start = sent.start + long.start_char
                            end = sent.start + long.end_char
                            document.annotations.append(
                                Annotation(
                                    start=start,
                                    end=end,
                                    label=params.long_label,
                                    text=document.text[start:end],
                                    terms=[
                                        Term(
                                            identifier=acro.text,
                                            lexicon="acronyms",
                                            preferredForm=long.text,
                                        )
                                    ],
                                )
                            )
                    else:
                        continue

        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return AcronymsParameters


@lru_cache(maxsize=None)
def get_nlp(model, max_size):
    try:
        nlp: Language = spacy.load(model)
    except BaseException:
        nlp = load_spacy_model(model)
    short = [{"TEXT": {"REGEX": "^[A-Z].*[A-Z].*$"}, "LENGTH": {"<=": max_size}}]
    short2long = [
        {"TEXT": {"REGEX": "^[A-Z].*[A-Z].*$"}, "LENGTH": {"<=": max_size}},
        {"IS_PUNCT": True, "TEXT": "("},
        {},
    ]
    short2long.extend([{"OP": "?"}] * (max_size * 2))
    long2short = [
        {},
        {"IS_PUNCT": True, "TEXT": "("},
        {"TEXT": {"REGEX": "^[A-Z].*[A-Z].*$"}, "LENGTH": {"<=": max_size}},
    ]
    matcher = Matcher(nlp.vocab, validate=True)
    matcher.add("short", [short])
    matcher.add("short2long", [short2long])
    matcher.add("long2short", [long2short])
    return nlp, matcher


def load_spacy_model(model, *pip_args):
    suffix = "-py3-none-any.whl"
    dl_tpl = "{m}-{v}/{m}-{v}{s}#egg={m}=={v}"
    model_name = model
    if model in OLD_MODEL_SHORTCUTS:
        msg.warn(
            f"As of spaCy v3.0, shortcuts like '{model}' are deprecated. Please "
            f"use the full pipeline package name '{OLD_MODEL_SHORTCUTS[model]}' instead."
        )
        model_name = OLD_MODEL_SHORTCUTS[model]
    compatibility = get_compatibility()
    version = get_version(model_name, compatibility)
    download_model(dl_tpl.format(m=model_name, v=version, s=suffix), pip_args)
    msg.good(
        "Download and installation successful",
        f"You can now load the package via spacy.load('{model_name}')",
    )
    # If a model is downloaded and then loaded within the same process, our
    # is_package check currently fails, because pkg_resources.working_set
    # is not refreshed automatically (see #3923). We're trying to work
    # around this here be requiring the package explicitly.
    require_package(model_name)
    return spacy.load(model_name, exclude=["parser"])


def require_package(name):
    try:
        import pkg_resources

        pkg_resources.working_set.require(name)
        return True
    except:  # noqa: E722
        return False


CLEANED_CHARS = {
    "\u2019": "'",  # RIGHT SINGLE QUOTATION MARK
    "\u00a0": " ",  # NBSP
    "\u202f": " ",  # NNBSP
    "\u2007": " ",  # FIGURE SPACE
    "\u2060": " ",  # WORD JOINER
}
CLEANED_TRANS = str.maketrans(CLEANED_CHARS)


def nlp_clean(nlp, texts: Union[str, Iterable[str]]):
    cleaned_texts = [texts] if isinstance(texts, str) else texts
    cleaned_texts = [text.translate(CLEANED_TRANS) for text in cleaned_texts]
    docs = nlp.pipe(cleaned_texts)
    return next(docs) if isinstance(texts, str) else docs


def resolve_longform(acro_def, short_form, segment):
    short_text = unidecode(short_form.text)
    acro_upper = [c for c in short_text if c.isupper()]
    # 1. Try all words starting with upper case regardless of their part-of-speech
    seg_upper = {
        i: unidecode(t.text)[0] for i, t in enumerate(segment) if t.text[0].isupper()
    }
    long = compare_signature(acro_def, acro_upper, seg_upper, segment)
    if long:
        return long
    # 2. Try all words ignoring empty words and some punctuations
    seg_upper = {
        i: unidecode(t.text).upper()[0]
        for i, t in enumerate(segment)
        if t.pos_ in ["PUNCT", "NOUN", "ADJ", "VERB", "PROPN", "ADV"]
        and t.text not in [".", "-"]
    }
    long = compare_signature(acro_def, acro_upper, seg_upper, segment)
    if long:
        return long
    logger.warning(f"Can't find long form for {short_form.text} in: {segment.text}")
    return None


def compare_signature(acro_def, acro_upper, seg_upper, segment):
    acro_up = "".join(acro_upper)
    seg_up = "".join(seg_upper.values())
    seg_keys = list(seg_upper.keys())
    idx = seg_up.rfind(acro_up) if acro_def == "long2short" else seg_up.find(acro_up)
    if idx >= 0:
        start = seg_keys[idx]
        end = seg_keys[idx + len(acro_up) - 1] + 1
        long_form = segment[start:end]
        # Accept an insertion of 2 tokens between long and short forms
        if (acro_def == "long2short" and segment.end - long_form.end <= 2) or (
            acro_def == "short2long" and long_form.start - segment.start <= 2
        ):
            return long_form
        else:
            logger.warning(
                f"Long form {long_form.text} too far from short form in: {segment.text}"
            )
    return None


def get_sort_key(m):
    return m[2] - m[1], -m[1]
