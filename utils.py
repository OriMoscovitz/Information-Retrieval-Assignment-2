import os
from file_handler import load_all_documents_raw, query_constructor_raw, write_results, query_constructor_title_and_desc, \
    query_constructor_all_data
from elastic_handler import get_es, index_name, create_index, bulk_index_documents, search_all_queries

def run(lang, run, train, queries_path=None, documents_list=None, output_file=None):
    train_str = "train" if train else "test"

    # get the elastic search session
    es = get_es()
    index = index_name(lang, run, output_file)

    docs = load_all_documents_raw(lang, documents_list, run)
    docnos = list(docs.keys())

    create_index(es, index, lang, run)
    bulk_index_documents(es, index, docs)

    # baseline and constrained
    if run == 0 or run == 1:
        queries = query_constructor_raw(lang, train, queries_path, run)

    # unconstrained
    elif run == 2:
        queries = query_constructor_title_and_desc(lang, train, queries_path)

    results = search_all_queries(es=es, index=index, queries=queries, docnos=docnos, run=run, top_k=1000)

    if output_file is not None:
        filename = os.path.join("outputs", output_file)
    else:
        filename = os.path.join("outputs", f"run-{run}_{train_str}_{lang}.res")

    write_results(results, filename, run)