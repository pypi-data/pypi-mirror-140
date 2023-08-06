import asyncio
import copy
import json
import logging
import os
import re
import zipfile
from collections import defaultdict, Counter
from concurrent.futures import as_completed
from datetime import timedelta
from pathlib import Path
from typing import List, Iterable

import pandas as pd
import pytest
import requests
from httpx._multipart import FileField
from multipart.multipart import parse_options_header
from pyconverters_newsml.newsml import NewsMLConverter, NewsMLParameters, get_mediatopics
from pymongo import MongoClient, UpdateOne
from pymultirole_plugins.util import comma_separated_to_list
from pymultirole_plugins.v1.schema import Document, DocumentList
from requests_cache import CachedSession
from requests_futures.sessions import FuturesSession
from sherpa_client.api.annotate import annotate_format_documents_with_plan_ref
from sherpa_client.client import SherpaClient
from sherpa_client.models import Credentials, InputDocument
from sherpa_client.types import Response, File
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from starlette.datastructures import UploadFile
from tqdm import tqdm


def test_newsml_text():
    model = NewsMLConverter.get_model()
    model_class = model.construct().__class__
    assert model_class == NewsMLParameters
    converter = NewsMLConverter()
    parameters = NewsMLParameters(subjects_as_metadata="afpperson,afporganization,afplocation")
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/text_only.xml')
    with source.open("r") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'text/xml'), parameters)
        assert len(docs) == 1
        doc0 = docs[0]
        assert doc0.metadata['nature'] == 'text'
        assert doc0.metadata['lang'] == 'es'
        assert 'Agence américaine d\'information' in doc0.metadata['afporganization']
        assert 'New York' in doc0.metadata['afplocation']
        assert doc0.categories is None


def test_newsml_pics():
    model = NewsMLConverter.get_model()
    model_class = model.construct().__class__
    assert model_class == NewsMLParameters
    converter = NewsMLConverter()
    parameters = NewsMLParameters(subjects_as_metadata="medtop,afpperson,afporganization,afplocation",
                                  subjects_code=True,
                                  mediatopics_as_categories=True)
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/text_and_pics.xml')
    with source.open("r") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'text/xml'), parameters)
        assert len(docs) == 7
        doc0 = docs[0]
        assert doc0.metadata['nature'] == 'text'
        assert doc0.metadata['lang'] == 'fr'
        assert '20000579:national elections' in doc0.metadata['medtop']
        assert '20000065:civil unrest' in doc0.metadata['medtop']
        cat_labels = [cat.label for cat in doc0.categories]
        assert ['national elections' in cat_label for cat_label in cat_labels]
        assert ['civil unrest' in cat_label for cat_label in cat_labels]
        doc5 = docs[5]
        assert doc5.metadata['nature'] == 'picture'
        assert doc5.metadata['lang'] == 'fr'
        assert '79588:Pascal Affi N\'Guessan' in doc5.metadata['afpperson']
        assert '1894:Abidjan' in doc5.metadata['afplocation']
        cat_labels = [cat.label for cat in doc5.categories]
        assert ['national elections' in cat_label for cat_label in cat_labels]
        assert ['electoral system' in cat_label for cat_label in cat_labels]


def test_newsml_agenda():
    model = NewsMLConverter.get_model()
    model_class = model.construct().__class__
    assert model_class == NewsMLParameters
    converter = NewsMLConverter()
    parameters = NewsMLParameters()
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/agenda.xml')
    with source.open("r") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'text/xml'), parameters)
        assert len(docs) == 1


APP_EF_URI = "https://sherpa-entityfishing.kairntech.com"
APP_EF_URI2 = "https://cloud.science-miner.com/nerd"


class EntityFishingClient:
    def __init__(self, base_url=APP_EF_URI):
        self.base_url = base_url[0:-1] if base_url.endswith('/') else base_url
        self.dsession = requests.Session()
        self.dsession.headers.update({'Content-Type': "application/json", 'Accept': "application/json"})
        self.dsession.verify = False
        self.ksession = CachedSession(
            cache_name='ef_cache', backend='sqlite',
            cache_control=True,  # Use Cache-Control headers for expiration, if available
            expire_after=timedelta(weeks=1),  # Otherwise expire responses after one week
            allowable_methods=['GET']  # Cache POST requests to avoid sending the same data twice
        )
        self.ksession.headers.update({'Content-Type': "application/json", 'Accept': "application/json"})
        self.ksession.verify = False
        self.fsession = FuturesSession(session=self.ksession)
        self.disamb_url = '/service/disambiguate/'
        self.kb_url = '/service/kb/concept/'
        self.term_url = '/service/kb/term/'

    def disamb_query(self, text, lang, minSelectorScore, entities=None, sentences=None, segment=False):
        disamb_query = {
            "text": text.replace('\r\n', ' \n'),
            "entities": entities,
            "sentences": sentences,
            "language": {"lang": lang},
            "mentions": ["wikipedia"],
            "nbest": False,
            "sentence": segment,
            "customisation": "generic",
            "minSelectorScore": minSelectorScore
        }
        try:
            resp = self.dsession.post(self.base_url + self.disamb_url, json=disamb_query, timeout=(60, 300))
            if resp.ok:
                return resp.json()
            else:
                resp.raise_for_status()
        except BaseException:
            logging.warning("An exception was thrown!", exc_info=True)
        return {}

    def disamb_terms_query(self, termVector, lang, minSelectorScore, entities=None, sentences=None, segment=False):
        disamb_query = {
            "termVector": termVector,
            "entities": entities,
            "sentences": sentences,
            "language": {"lang": lang},
            "mentions": ["wikipedia"],
            "nbest": False,
            "sentence": segment,
            "customisation": "generic",
            "minSelectorScore": minSelectorScore
        }
        resp = self.dsession.post(self.base_url + self.disamb_url, json=disamb_query, timeout=(30, 300))
        if resp.ok:
            return resp.json()
        else:
            return {}

    def get_kb_concept(self, qid):
        try:
            resp = self.ksession.get(self.base_url + self.kb_url + qid, timeout=(30, 300))
            if resp.ok:
                return resp.json()
            else:
                resp.raise_for_status()
        except BaseException:
            logging.warning("An exception was thrown!", exc_info=True)
        return {}

    def get_kb_concepts(self, qids: Iterable):
        futures = [self.fsession.get(self.base_url + self.kb_url + qid) for qid in qids]
        concepts = {qid: None for qid in qids}
        for future in as_completed(futures):
            try:
                resp = future.result()
                if resp.ok:
                    concept = resp.json()
                    if 'wikidataId' in concept:
                        concepts[concept['wikidataId']] = concept
                else:
                    resp.raise_for_status()
            except BaseException:
                logging.warning("An exception was thrown!", exc_info=True)
        return concepts

    def compute_fingerprint(self, docid, yeardir, fingerprints):
        jsondir = yeardir / 'json'
        tokens = []
        result = None
        if jsondir.exists():
            filename = docid2filename(docid)
            jsonfile = jsondir / f"{filename}.json"
            if jsonfile.exists():
                with jsonfile.open("r") as jfin:
                    result = json.load(jfin)
            else:
                logging.warning(f"Can't find file {jsonfile}")
        else:
            logging.warning(f"Can't find dir {jsondir}")
            # result = self.disamb_query(text, lang, 0.2, None, None)
        if result is not None:
            entities = [entity for entity in result['entities'] if
                        'wikidataId' in entity] if 'entities' in result else []
            qids = {entity['wikidataId'] for entity in entities}
            concepts = self.get_kb_concepts(qids)
            for entity in entities:
                qid = entity['wikidataId']
                tokens.append(qid)
                concept = concepts[qid]
                if concept is not None:
                    if 'statements' in concept:
                        finger_sts = list(
                            filter(lambda st: st['propertyId'] in fingerprints and isinstance(st['value'], str),
                                   concept['statements']))
                        if finger_sts:
                            fingerprint = {st['value'] for st in finger_sts if st['value'].startswith('Q')}
                            tokens.extend(fingerprint)
            return " ".join(tokens)
        return None


@pytest.mark.skip(reason="Not a test")
def test_parse_xml():
    converter = NewsMLConverter()
    parameters = NewsMLParameters(subjects_as_metadata="medtop,afpperson,afporganization,afplocation",
                                  subjects_code=True,
                                  mediatopics_as_categories=False)
    # parameters = NewsMLParameters(subjects_as_metadata="medtop,afpperson,afporganization,afplocation",
    #                               mediatopics_as_categories=True)
    max_doc_size = 8000
    start_title_filters = [
        "agenda",
        'les grands rendez',
        'prévisions',
        'revised sports calendar',
        'tagesvorschau'
    ]
    end_title_filters = [
        "news agenda",
    ]
    ignore_empty_subjects = True
    ignore_agenda = True
    subjects_filter = comma_separated_to_list(parameters.subjects_as_metadata.strip())
    if 'medtop' in subjects_filter:
        subjects_filter.remove('medtop')

    input_path = Path("/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_FR")
    output_path = Path("/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_FR_QUALITY")
    for year in tqdm(list(input_path.glob("*"))):
        logging.info(f"Year: {year}")
        if year.is_dir():
            for month in tqdm(list(year.iterdir())):
                if len(month.name) == 2:
                    logging.info(f"Month: {month}")
                    data = defaultdict(list)
                    for f in tqdm(list(month.rglob("*.xml"))):
                        with f.open("r") as fin:
                            docs: List[Document] = converter.convert(UploadFile(f.name, fin, 'text/xml'), parameters)
                            for doc in docs:
                                if ignore_empty_subjects:
                                    subjects = []
                                    for subject in subjects_filter:
                                        subjects.extend(doc.metadata.get(subject, []))
                                    if len(subjects) == 0:
                                        logging.info(f"Found empty subjects: {doc.identifier}")
                                        continue
                                if ignore_agenda:
                                    doc_title = doc.title.lower() if doc.title is not None else ""
                                    if doc.metadata.get('genre', None) is not None and \
                                            doc.metadata['genre'].lower() == "agenda":
                                        logging.info(f"Found Agenda: {doc.title}: size={len(doc.text)}")
                                        continue
                                    if list(filter(lambda x: doc_title.startswith(x), start_title_filters)):
                                        logging.info(f"Found Agenda: {doc.title}: size={len(doc.text)}")
                                        continue
                                    if list(filter(lambda x: doc_title.endswith(x), end_title_filters)):
                                        logging.info(f"Found Agenda: {doc.title}: size={len(doc.text)}")
                                        continue
                                    if len(doc.text) > max_doc_size:
                                        logging.info(f"Found big: {doc.title} in {f.name}: size={len(doc.text)}")
                                        continue
                                data[doc.metadata['lang']].append(doc)
                    for lang, ldocs in data.items():
                        output_dir = Path(output_path) / lang / year.name
                        output_dir.mkdir(parents=True, exist_ok=True)
                        dl = DocumentList(__root__=ldocs)
                        output_file = output_dir / Path(month.name).with_suffix(".json")
                        logging.info(f"Write: {output_file}")
                        with output_file.open("w") as fout:
                            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


@pytest.mark.skip(reason="Not a test")
def test_parse_categories():  # noqa
    ef_client = EntityFishingClient()
    # fingerprints = "P31,P279,P361,P106,P452,P1566"
    fingerprints = "P31,P279,P361,P106,P1566"
    compute_fingerprint = True
    compute_txt = False
    compute_sample = False
    input_path = Path("/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_DE_PARSED")
    # input_path = Path("/media/olivier/DATA/corpora/AFP/extract_9ba8e44c-0cfc-45fe-a3ed-9bfa41a52fc4_2-parsed")
    output_path = Path("/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_DE_CAT")
    # output_path = Path("/media/olivier/DATA/corpora/AFP/extract_9ba8e44c-0cfc-45fe-a3ed-9bfa41a52fc4_2-categ")
    for lang in tqdm(list(input_path.glob("*"))):
        lang_docs = []
        if lang.is_dir():
            for year in tqdm(list(lang.iterdir())):
                if len(year.name) > 4:
                    continue
                jsondir = year / 'json'
                if compute_fingerprint and not jsondir.exists():
                    continue
                for f in tqdm(list(year.glob("*.json"))):
                    if len(f.stem) > 2:
                        continue
                    with f.open("r") as fin:
                        jdocs = json.load(fin)
                        docs: List[Document] = [Document(**jdoc) for jdoc in jdocs]
                        lvl_docs = defaultdict(list)
                        for doc in docs:
                            if compute_fingerprint and jsondir.exists() and doc.metadata['lang'] in ['en', 'fr', 'de']:
                                doc.metadata['fingerprint'] = ef_client.compute_fingerprint(doc.identifier, year,
                                                                                            fingerprints)
                            lvl_categories = defaultdict(list)
                            if doc.categories:
                                lnames = [c.labelName.split('_') for c in doc.categories]
                                level1 = [codes[0] for codes in lnames if len(codes) == 1]
                                lvl_categories['_'] = [c for c in doc.categories if c.labelName in level1]
                                for lvl1 in level1:
                                    lvl_categories[lvl1] = [c for c in doc.categories if
                                                            c.labelName.startswith(f"{lvl1}_")]
                                for lvl, cats in lvl_categories.items():
                                    newdoc = copy.deepcopy(doc)
                                    newdoc.categories = cats
                                    lvl_docs[lvl].append(newdoc)
                        for lvl, ldocs in lvl_docs.items():
                            if len(ldocs) > 0:
                                output_dir = Path(output_path) / lang.name / year.name / lvl
                                output_dir.mkdir(parents=True, exist_ok=True)
                                dl = DocumentList(__root__=ldocs)
                                output_file = output_dir / Path(f.name).with_suffix(".json")
                                logging.info(f"Write: {output_file}")
                                with output_file.open("w") as fout:
                                    print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
                                if lvl == '_':
                                    if compute_sample:
                                        lang_docs.extend(ldocs)
                                    if compute_txt:
                                        output_dir = Path(output_path) / lang.name / year.name / 'txt'
                                        output_dir.mkdir(parents=True, exist_ok=True)
                                        for ldoc in ldocs:
                                            filename = docid2filename(ldoc.identifier)
                                            output_file = output_dir / f"{filename}.txt"
                                            with output_file.open("w", encoding="utf-8") as fout:
                                                fout.write(ldoc.text)
        if compute_sample and len(lang_docs) > 5000:
            logging.info(f"Nb docs for {lang}: {len(lang_docs)}")
            keep5000, _ = train_test_split(lang_docs, train_size=5000, shuffle=True)
            dl = DocumentList(__root__=keep5000)
            output_file = Path(output_path) / lang.name / "sample_5000.json"
            with output_file.open("w", encoding="utf-8") as fout:
                print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
            keep50, _ = train_test_split(keep5000, train_size=50, shuffle=True)
            dl = DocumentList(__root__=keep50)
            output_file = Path(output_path) / lang.name / "sample_50.json"
            with output_file.open("w", encoding="utf-8") as fout:
                print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


def docid2filename(docid):  # noqa
    if docid.startswith('urn:'):
        parts = docid.split(':')
        filename = parts[-1]
    elif docid.startswith('http:'):
        parts = docid.split('/')
        filename = parts[-1]
    else:
        filename = None
    return filename


@pytest.mark.skip(reason="Not a test")
def test_consolidate_cats():  # noqa
    dbname = 'afp_iptc_economy'
    root = '04000000'
    topics = get_mediatopics()
    count_min = 50
    root_topics = {k: v for k, v in topics.items() if v.levels[0] == root}
    counts = defaultdict(int)
    mongo_uri = "mongodb://localhost:27017/"
    mongo = MongoClient(mongo_uri)
    db = mongo[dbname]
    for doc in db.documents.find():
        if doc['categories']:
            for cat in doc['categories']:
                labels = cat['labelName'].split('_')
                for label in labels:
                    counts[label] += 1
    for level in range(5, 1, -1):
        logging.info(f"Consolidating level {level}")
        level_topics = {k: v for k, v in root_topics.items() if len(v.levels) == level}
        level_conso = []
        for code in level_topics:
            topic = level_topics[code]
            count = counts[code]
            if 0 < count < count_min:
                level_conso.append(topic)
        for t in level_conso:
            logging.info(f"Dropping {t.label}")
            # topicCode = t.levels[-1]
            parentCode = t.levels[-2]
            parent = root_topics[parentCode]
            parentName = '_'.join(parent.levels)
            # parentLabel = f"{parentName} ({parent.label})"
            labelName = '_'.join(t.levels)
            cat_filter = {'categories.labelName': labelName}
            cat_rename = {'$set': {"categories.$.labelName": parentName}}
            result = db.documents.update_many(cat_filter, cat_rename)
            if result.acknowledged:
                logging.info("%d document categories consolidated" % result.modified_count)


@pytest.mark.skip(reason="Not a test")
def test_downsampling_cats():  # noqa
    dbname = 'afp_iptc_politics'
    mongo_uri = "mongodb://localhost:27017/"
    mongo = MongoClient(mongo_uri)
    db = mongo[dbname]
    nb_docs, counter = count_documents_per_cats(db)
    # max_docs = int(nb_docs / 10)
    max_docs = 1000

    big_cats = [k for (k, v) in counter.most_common(50) if v > max_docs]
    for label in big_cats:
        nb = counter[label]
        if nb > max_docs:
            delete_topcat_if_leave(db, label)
            # delete_documents_for_cat(db, label, (nb - max_docs))
            nb_docs, counter = count_documents_per_cats(db)


@pytest.mark.skip(reason="Not a test")
def test_downsampling_kw():  # noqa
    dbname = 'afp_iptc_health'
    mongo_uri = "mongodb://localhost:27017/"
    mongo = MongoClient(mongo_uri)
    db = mongo[dbname]
    pipeline = [
        {
            '$match': {
                'text': re.compile(r"covid|coronavirus(?i)")
            }
        }, {
            '$match': {
                'categories.labelName': {
                    '$in': [
                        '07000000_20000446_20000448_20000451', '07000000_20000446_20000448_20000449_20001218',
                        '07000000_20000446_20000448_20000449', '07000000_20000446_20000448_20000451'
                    ]
                }
            }
        },
        {
            '$project': {
                'identifier': 1
            }
        },
        {
            '$limit': 5000
        }
    ]
    cursor = db.documents.aggregate(pipeline)
    rows = pd.DataFrame(list(cursor))
    if len(rows):
        to_remove = list(rows['_id'])
        result = db.documents.delete_many({"_id": {"$in": to_remove}})
        if result.acknowledged:
            logging.info(f"{result.deleted_count} docs deleted")
    del rows
    cursor.close()


@pytest.mark.skip(reason="Not a test")
def test_compute_fingerprint():  # noqa
    ef_client = EntityFishingClient()
    fingerprints = "P31,P279,P361,P106,P452,P1566"
    # fingerprints = "P31,P279,P361,P106,P1566"
    dbname = 'afp_iptc_arts'
    mongo_uri = "mongodb://localhost:27017/"
    mongo = MongoClient(mongo_uri)
    db = mongo[dbname]
    nb_docs = db.documents.count_documents({'metadata.lang': 'fr'})

    def compute_fingerprint(row):
        lang = row.lang
        year = row.year
        docid = row.identifier
        yeardir = Path(
            f"/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_{lang.upper()}_PARSED/{lang}/{year}")
        if yeardir.exists() and lang in ['en', 'fr', 'de']:
            fingerprint = ef_client.compute_fingerprint(docid, yeardir, fingerprints)
            return fingerprint
        else:
            logging.error(f"Year dir {str(yeardir)} does not exist")
        return pd.NA

    start_at = 0
    for skip in tqdm(range(start_at, nb_docs, 100)):
        pipeline = [
            {
                '$match': {
                    'metadata.lang': {'$in': ['en', 'fr', 'de']}
                }
            },
            {
                '$project': {
                    'identifier': 1,
                    'lang': '$metadata.lang',
                    'year': {
                        '$substr': [
                            '$metadata.versionCreated', 0, 4
                        ]
                    }
                }
            },
            {
                '$sort': {'_id': 1}
            },
            {
                '$skip': skip
            },
            {
                '$limit': 100
            }
        ]
        cursor = db.documents.aggregate(pipeline)
        rows = pd.DataFrame(list(cursor))
        rows['fingerprint'] = rows.apply(lambda x: compute_fingerprint(x), axis=1)
        updates = []
        for i, doc in rows.iterrows():
            if not pd.isna(doc.fingerprint):
                updates.append(UpdateOne({"_id": doc._id}, {'$set': {"metadata.fingerprint": doc.fingerprint}}))
        if updates:
            db.documents.bulk_write(updates, ordered=False)
            # result = db.documents.bulk_write(updates, ordered=False)
            # logging.info("%d documents modified" % (result.modified_count + result.upserted_count,))
        del rows
        cursor.close()
        print(skip)


def chunks(seq, size=1000):  # noqa
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def count_documents_per_cats(db):  # noqa
    nb_docs = 0
    counts = defaultdict(int)
    for doc in db.documents.find():
        if doc['categories']:
            nb_docs += 1
            for cat in doc['categories']:
                label = cat['labelName']
                counts[label] += 1
    return nb_docs, Counter(counts)


def delete_documents_for_cat(db, label, limit):  # noqa
    aggreg = [
        {
            '$match': {
                'categories.labelName': label
            }
        }, {
            '$project': {
                'nb_cats': {
                    '$size': '$categories'
                }
            }
        }, {
            '$sort': {
                'nb_cats': 1
            }
        }, {
            '$match': {
                'nb_cats': 1
            }
        }, {
            '$limit': limit
        }
    ]
    results = list(db.documents.aggregate(aggreg))
    if results:
        to_remove = [d['_id'] for d in results]
        result = db.documents.delete_many({"_id": {"$in": to_remove}})
        if result.acknowledged:
            logging.info(f"{result.deleted_count} docs deleted for category {label}")


def delete_topcat_if_leave(db, label):  # noqa
    aggreg = [
        {
            '$match': {
                'categories.labelName': re.compile(r"^" + label + "_")
            }
        },
        {
            '$match': {
                'categories.labelName': label
            }
        }, {
            '$project': {
                '_id': 1,
                'categories': 1,
                'nb_cats': {
                    '$size': '$categories'
                }
            }
        }, {
            '$sort': {
                'nb_cats': 1
            }
        }
    ]
    results = list(db.documents.aggregate(aggreg))
    if results:
        updates = []
        for doc in results:
            categories = [cat for cat in doc['categories'] if cat['labelName'] != label]
            updates.append(UpdateOne({"_id": doc['_id']}, {'$set': {"categories": categories}}))
        if updates:
            result = db.documents.bulk_write(updates, ordered=False)
            logging.info("%d documents modified" % (result.modified_count + result.upserted_count,))


@pytest.mark.skip(reason="Not a test")
@pytest.mark.asyncio
async def test_annotate_xml():  # noqa
    SHERPA_URL = os.environ.get('SHERPA_URL')
    SHERPA_USER = os.environ.get('SHERPA_USER')
    SHERPA_PWD = os.environ.get('SHERPA_PWD')
    client = SherpaClient(base_url=f"{SHERPA_URL}/api", verify_ssl=False, timeout=100)
    client.login_with_token(Credentials(email=SHERPA_USER, password=SHERPA_PWD))
    PNAME = "afp_iptc_root"
    ANAME = "afp_fr"
    input_path = Path("/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_FR_QUALITY/fr")
    output_path = Path("/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_FR_REPORT")
    done_files = [f.stem for f in output_path.rglob("*.done")]
    for year in tqdm(list(input_path.glob("*"))):
        logging.info(f"Year: {year}")
        if year.is_dir():
            for jfile in list(year.rglob("*.json")):
                with jfile.open("r") as fin:
                    data = json.load(fin)
                    filtered_data = [d for d in data if docid2filename(d['identifier']) not in done_files]
                    for docs in chunks(filtered_data, 10):
                        tasks = {}
                        for doc in docs:
                            del doc['properties']
                            input = InputDocument.from_dict(doc)
                            tasks[input.identifier] = asyncio.ensure_future(
                                annotate_format_documents_with_plan_ref.asyncio_detailed(PNAME, ANAME,
                                                                                         json_body=[input],
                                                                                         client=client))
                        resps_or_excs = await asyncio.gather(*(tasks.values()), return_exceptions=True)
                        for docid, resp_or_exc in zip(tasks.keys(), resps_or_excs):
                            try:
                                if isinstance(resp_or_exc, Response):
                                    if resp_or_exc.is_success:
                                        file = _file_from_response(resp_or_exc)
                                        content_path = Path(file.file_name)
                                        if content_path.suffix == '.zip':
                                            with zipfile.ZipFile(file.payload, 'r') as zipped:
                                                entrynames = set(zipped.namelist())
                                                for entryname in entrynames:
                                                    with zipped.open(entryname, "r") as xslx_file:
                                                        output_file = output_path / entryname
                                                        done_file = output_file.with_suffix(".done")
                                                        with output_file.open("wb") as fout:
                                                            fout.write(xslx_file.read())
                                                            done_file.touch()
                                        else:
                                            output_file = (output_path / docid2filename(docid)).with_suffix(
                                                content_path.suffix)
                                            done_file = output_file.with_suffix(".done")
                                            with output_file.open("wb") as fout:
                                                fout.write(file.payload.read())
                                                done_file.touch()
                                        pass
                                    else:
                                        resp_or_exc.raise_for_status()
                                else:
                                    if hasattr(resp_or_exc, 'request'):
                                        req = resp_or_exc.request
                                        if hasattr(req, 'stream'):
                                            mp_stream = req.stream
                                            if mp_stream.fields and isinstance(mp_stream.fields[0], FileField):
                                                logging.warning(f"Exception for file {mp_stream.fields[0].filename}")
                                    raise resp_or_exc
                            except BaseException:
                                pass
                                # logging.warning("Exception thrown", exc_info=True)


def _file_from_response(r: Response):
    file: File = r.parsed
    file.mime_type = r.headers.get('Content-Type', 'application/octet-stream')
    if 'Content-Disposition' in r.headers:
        content_type, content_parameters = parse_options_header(r.headers['Content-Disposition'])
        # file.mime_type = content_type
        if b'filename' in content_parameters:
            file.file_name = content_parameters[b'filename'].decode("utf-8")
    return file


@pytest.mark.skip(reason="Not a test")
def test_compute_quality():  # noqa
    input_path = Path("/media/olivier/DATA/corpora/AFP/POC/POC_KAIRNTECH_CORPUS_FR_REPORT")
    total = defaultdict(pd.DataFrame)
    for excel_file in tqdm(list(input_path.glob("*.xlsx"))):
        with pd.ExcelFile(excel_file) as xls:
            for sheet in ['medtop', 'afpperson', 'afplocation', 'afporganization']:
                df = pd.read_excel(xls, sheet)
                total[sheet] = total[sheet].append(df, ignore_index=True)
    for sheet, df in total.items():
        p, r, f1, s = precision_recall_fscore_support(df['True'].tolist(), df['Pred'].tolist())
        print(sheet)
        print('-----------------')
        print(f"p={p[1]}")
        print(f"r={r[1]}")
        print(f"f1={f1[1]}")
        print('=================================')
