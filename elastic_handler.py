from collections import Counter
import math

from elasticsearch import Elasticsearch, helpers
from tqdm import tqdm

from elastic_configs import *

def get_es():
    return Elasticsearch("http://localhost:9200")


def index_name(lang, run, output_file):
    return f"a1-{lang}-run-{run}-{output_file}"


def create_index(es, index, lang, run):
    if es.indices.exists(index=index):
        es.indices.delete(index=index)

    if run == 0:
        body = run0_body()

    elif run == 1 or run == 2:
        ### CHANGE THIS BODY TO APPLY DIFFERENT ES CONFIGS
        body = run1_bm25_body(lang)

    else:
        raise ValueError(f"Unsupported run: {run}")

    es.indices.create(index=index, body=body)


def search_all_queries(es, index, queries, docnos, run, top_k=1000):
    results = {}

    # for qid, query_text in queries.items():
    for qid, query_text in tqdm(queries.items(), desc="(ES) Searching queries..."):
        if run == 0:
            results[qid] = search_query_run0(
                es=es,
                index=index,
                query_text=query_text,
                docnos=docnos,
                top_k=top_k
            )
        # # English for en-1 to en-5
        # # Czech for cs-1 to cs-4
        # elif run == 1:
        #     results[qid] = search_query_run0(
        #         es=es,
        #         index=index,
        #         query_text=query_text,
        #         docnos=docnos,
        #         top_k=top_k
        #     )

        # English for en-6 to en-8
        # Czech for cs-5 to cs-7
        # best run-1 configuration
        elif run == 1 or run == 2:
            # without PRF
            results[qid] = search_query_run1(
                es=es,
                index=index,
                query_text=query_text,
                top_k=top_k
            )

            # # with PRF
            # print(f"------ running PRF ------")
            # results[qid] = search_query_run1_prf(
            #     es=es,
            #     index=index,
            #     query_text=query_text,
            #     top_k=top_k
            # )

        else:
            raise ValueError(f"Unsupported run: {run}")

    return results


def bulk_index_documents(es, index, docs):
    actions = [
        {
            "_index": index,
            "_id": docno,
            "_source": {
                "docno": docno,
                "text": text
            }
        }
        for docno, text in docs.items()
    ]

    helpers.bulk(es, actions)
    es.indices.refresh(index=index)


def analyze_query(es, index, query_text):
    response = es.indices.analyze(
        index=index,
        body={
            "field": "text",
            "text": query_text
        }
    )

    return [token["token"] for token in response["tokens"]]


def get_doc_term_vector(es, index, docno):
    response = es.termvectors(
        index=index,
        id=docno,
        fields=["text"],
        term_statistics=False,
        field_statistics=False
    )

    terms = response.get("term_vectors", {}).get("text", {}).get("terms", {})

    return {
        term: data["term_freq"]
        for term, data in terms.items()
    }


def cosine_similarity(query_vec, doc_vec):
    dot = sum(query_vec[term] * doc_vec.get(term, 0) for term in query_vec)

    query_norm = math.sqrt(sum(value * value for value in query_vec.values()))
    doc_norm = math.sqrt(sum(value * value for value in doc_vec.values()))

    if query_norm == 0 or doc_norm == 0:
        return 0.0

    return dot / (query_norm * doc_norm)


def search_query_run0(es, index, query_text, docnos, top_k=1000):
    query_tokens = analyze_query(es, index, query_text)
    query_vec = Counter(query_tokens)

    scores = []

    for docno in docnos:
        doc_vec = get_doc_term_vector(es, index, docno)
        score = cosine_similarity(query_vec, doc_vec)

        if score > 0:
            scores.append((docno, score))

    scores.sort(key=lambda item: item[1], reverse=True)
    return scores[:top_k]


def search_query_run1(es, index, query_text, top_k=1000):
    response = es.search(
        index=index,
        size=top_k,
        query={
            "match": {
                "text": query_text
            }
        }
    )

    return [
        (hit["_source"]["docno"], hit["_score"])
        for hit in response["hits"]["hits"]
    ]


# es doesn't have built in PRF
def pseudo_relevance_feedback_es(es, index, query_text, top_k=10, top_terms=20, expansion_weight=1):
    initial_results = search_query_run1(
        es=es,
        index=index,
        query_text=query_text,
        top_k=top_k
    )

    term_scores = Counter()

    for docno, _ in initial_results:
        doc_vec = get_doc_term_vector(es, index, docno)

        for term, freq in doc_vec.items():
            term_scores[term] += freq

    original_terms = set(analyze_query(es, index, query_text))

    expansion_terms = [
        term
        for term, _ in term_scores.most_common(top_terms + len(original_terms))
        if term not in original_terms
    ][:top_terms]

    expanded_query = query_text + " " + " ".join(
        term for term in expansion_terms
        for _ in range(expansion_weight)
    )

    return expanded_query


def search_query_run1_prf(es, index, query_text, top_k=1000):
    expanded_query = pseudo_relevance_feedback_es(
        es=es,
        index=index,
        query_text=query_text,
        top_k=3,
        top_terms=5,
        expansion_weight=1
    )

    return search_query_run1(
        es=es,
        index=index,
        query_text=expanded_query,
        top_k=top_k
    )

