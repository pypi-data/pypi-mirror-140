import json
from pathlib import Path

import pytest
from pymultirole_plugins.v1.schema import Document, Annotation

from pyprocessors_afp_entities.afp_entities import AFPEntitiesProcessor, AFPEntitiesParameters, ConsolidationType, \
    group_annotations


def test_model():
    model = AFPEntitiesProcessor.get_model()
    model_class = model.construct().__class__
    assert model_class == AFPEntitiesParameters


# Arrange
@pytest.fixture
def original_doc():
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/afp_ner_fr-document-test.json')
    with source.open("r") as fin:
        doc = json.load(fin)
        original_doc = Document(**doc)
        return original_doc


def by_linking(a: Annotation):
    if a.terms:
        links = sorted({t.lexicon.split('_')[0] for t in a.terms})
        return '+'.join(links)
    else:
        return 'candidate'


def test_afp_entities_linker(original_doc):
    # linker
    doc = original_doc.copy(deep=True)
    processor = AFPEntitiesProcessor()
    parameters = AFPEntitiesParameters(type=ConsolidationType.linker)
    docs = processor.process([doc], parameters)
    conso: Document = docs[0]
    assert len(conso.annotations) < len(original_doc.annotations)
    conso_groups = group_annotations(conso, by_linking)
    assert len(conso_groups['candidate']) == 8
    assert len(conso_groups['person']) == 2
    assert len(conso_groups['wikidata']) == 10
    assert len(conso_groups['location+wikidata']) == 1
    assert len(conso_groups['organization+wikidata']) == 2
