import os
import xml.etree.ElementTree as ET

from tqdm import tqdm
from xml_handler import clean_xml, extract_valid_xml

import re
import nltk
from nltk import WordNetLemmatizer
from nltk.corpus import wordnet
from ufal.morphodita import Tagger, Forms, TaggedLemmas, TokenRanges

lemmatizer_en = WordNetLemmatizer()

MORPHODITA_MODEL_PATH = os.path.join(
    "morfflex",
    "czech-morfflex2.0-pdtc1.0-220710.tagger"
)
tagger = Tagger.load(MORPHODITA_MODEL_PATH)
tokenizer = tagger.newTokenizer()

nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')

def get_wordnet_pos(tag):
    if tag.startswith("J"): return wordnet.ADJ
    if tag.startswith("V"): return wordnet.VERB
    if tag.startswith("N"): return wordnet.NOUN
    if tag.startswith("R"): return wordnet.ADV
    return wordnet.NOUN  # default to noun if unknown

def lemmatize_text_en(text):
    tokens = re.split(r"[^\w]+", text)
    pos_tags = nltk.pos_tag(tokens)
    lemmas = [
        lemmatizer_en.lemmatize(token.lower(), pos=get_wordnet_pos(tag))
        for token, tag in pos_tags
    ]
    return " ".join(lemmas)

def lemmatize_text_cs(text):
    forms = Forms()
    lemmas = TaggedLemmas()
    token_ranges = TokenRanges()

    tokenizer.setText(text)

    result = []

    while tokenizer.nextSentence(forms, token_ranges):
        tagger.tag(forms, lemmas)

        for i in range(len(lemmas)):
            clean = lemmas[i].lemma.split("_")[0].split("-")[0].strip()
            if clean:
                result.append(clean)

    return " ".join(result)

def lemmatize_text(text, lang):
    if lang == "en":
        return lemmatize_text_en(text)
    elif lang == "cs":
        return lemmatize_text_cs(text)
    else:
        return text

def read_documents_list(lst_name=None):
    lst_path = os.path.join("A1", lst_name)

    filenames = []
    with open(lst_path, "r", encoding="utf-8") as f:
        for line in f:
            filename = line.strip()
            if filename:
                filenames.append(filename)

    return filenames


def query_constructor_all_data(lang, train, queries_path=None):
    if queries_path:
        path = os.path.join(os.getcwd(), "A1", queries_path)
    else:
        xml_path = f"topics-train_{lang}.xml" if train else f"topics-test_{lang}.xml"
        path = os.path.join(os.getcwd(), "A1", xml_path)

    queries = {}

    tree = ET.parse(path)
    root = tree.getroot()

    for topic in tqdm(root.findall("top"), desc="Constructing queries..."):
        qid = topic.find("num").text.strip()

        title = topic.findtext("title", default="").strip()
        desc = topic.findtext("desc", default="").strip()
        narr = topic.findtext("narr", default="").strip()

        # combine title + description
        query_text = f"{title} {desc} {narr}".strip()

        queries[qid] = lemmatize_text(query_text, lang)

    print("Finished constructing queries.")
    return queries


def query_constructor_title_and_desc(lang, train, queries_path=None):
    if queries_path:
        path = os.path.join(os.getcwd(), "A1", queries_path)
    else:
        xml_path = f"topics-train_{lang}.xml" if train else f"topics-test_{lang}.xml"
        path = os.path.join(os.getcwd(), "A1", xml_path)

    queries = {}

    tree = ET.parse(path)
    root = tree.getroot()

    for topic in tqdm(root.findall("top"), desc="Constructing queries..."):
        qid = topic.find("num").text.strip()

        title = topic.findtext("title", default="").strip()
        desc = topic.findtext("desc", default="").strip()

        # combine title + description
        query_text = f"{title} {desc}".strip()

        # run-2
        queries[qid] = lemmatize_text(query_text, lang)

    print("Finished constructing queries.")
    return queries


def query_constructor_raw(lang, train, queries_path=None, run=None):
    # print("Constructing queries...")

    if queries_path:
        path = os.path.join(os.getcwd(), "A1", queries_path)
    else:
        xml_path = f"topics-train_{lang}.xml" if train else f"topics-test_{lang}.xml"
        path = os.path.join(os.getcwd(), "A1", xml_path)

    queries = {}

    tree = ET.parse(path)
    root = tree.getroot()

    # for topic in root.findall("top"):
    for topic in tqdm(root.findall("top"), desc="Constructing queries..."):
        qid = topic.find("num").text.strip()
        title = topic.find("title").text.strip()

        if run == 0:
            queries[qid] = title

        else:
            # # for runs 1 and 2
            # queries[qid] = title

            # for run 3+
            queries[qid] = lemmatize_text(title, lang)


    print("Finished constructing queries.")
    return queries

def parse_single_doc_text(doc):
    docno = None
    parts = []

    for child in doc:
        tag = child.tag
        text = (child.text or "").strip()

        if not text:
            continue

        if tag == "DOCNO":
            docno = text
        else:
            parts.append(text)

    if docno is None:
        return None

    return docno, " ".join(parts)

def load_all_documents_raw(language, documents_list=None, run=None):
    print("Loading all documents...")

    docs_dir = os.path.join("A1", f"documents_{language}")
    parsed_docs = {}

    if documents_list:
        filenames = read_documents_list(documents_list)
    else:
        filenames = [f for f in os.listdir(docs_dir) if f.endswith(".xml")]

    for filename in tqdm(filenames, desc="Loading documents"):
        if not filename.endswith(".xml"):
            continue

        path = os.path.join(docs_dir, filename)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        content = clean_xml(content)
        content = extract_valid_xml(content)

        try:
            root = ET.fromstring(content)

            for doc in root.findall(".//DOC"):
                result = parse_single_doc_text(doc)

                if not result:
                    continue

                docno, text = result

                if docno in parsed_docs:
                    print(f"Duplicate key: {docno}")
                    continue

                if run == 0:
                    parsed_docs[docno] = text

                else:
                    # # for runs 1 and 2
                    # parsed_docs[docno] = text

                    # for run 3+
                    parsed_docs[docno] = lemmatize_text(text, language)


        except ET.ParseError as e:
            print(f"Skipping {filename}. error: {e}")

    print("Finished loading all documents.")
    return parsed_docs

def write_results(results, output_file, run):
    print("Writing results to " + output_file)

    with open(output_file, "w", encoding="iso-8859-1") as f:
        for qid, ranked_docs in results.items():
            for rank, (docno, score) in enumerate(ranked_docs, start=1):
                f.write(f"{qid}\t0\t{docno}\t{rank}\t{score:.6f}\t{run}\n")