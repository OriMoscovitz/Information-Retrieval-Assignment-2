EN_EQU = [
    "u.s., u_s, usa",
    "u.k., britain, england, uk",
    "ussr, soviet, russia",
    "eu, european, europe",
    "govt, gov, government",
    "corp, inc, ltd, corporation",
    "dept, department",
    "vs, versus",
    "dr, doctor",
    "mr, mister",
    "mrs, missus",
    "jan, january",
    "feb, february",
    "apr, april",
    "jun, june",
    "jul, july",
    "oct, october",
    "nov, november",
    "dec, december"
]

CS_EQU = [
    "čr, česká republika, česko",
    "slovenská republika, slovensko",
    "usa, spojené státy, amerika",
    "eu, evropská unie, evropa",
    "vl, vláda",
    "č, číslo",
    "mld, miliarda",
    "mil, milion",
    "tis, tisíc",
    "tzv, takzvaný",
    "např, například",
]

# baseline (en-0, cs-0) - experiment 0
def run0_body():
    return {
        "settings": {
            "analysis": {
                "analyzer": {
                    "baseline_analyzer": {
                        "type": "custom",
                        "tokenizer": "baseline_tokenizer",
                        "filter": []
                    }
                },
                "tokenizer": {
                    "baseline_tokenizer": {
                        "type": "pattern",
                        "pattern": "[\\s\\p{Punct}]+"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "docno": {"type": "keyword"},
                "text": {
                    "type": "text",
                    "analyzer": "baseline_analyzer",
                    "search_analyzer": "baseline_analyzer",
                    "term_vector": "yes"
                }
            }
        }
    }

# es built-in tokenizer that recognizes real word boundaries based on the Unicode Text Segmentation algorithm (en-1, cs-1) experiment 1
def run1_smart_tokenizer(lang):
    return {
        "settings": {
            "analysis": {
                "analyzer": {
                    "baseline_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": []
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "docno": {"type": "keyword"},
                "text": {
                    "type": "text",
                    "analyzer": "baseline_analyzer",
                    "search_analyzer": "baseline_analyzer",
                    "term_vector": "yes"
                }
            }
        }
    }

# removing stopwords (en-2, cs-2) experiment 2
def run1_stopwords_body(lang):
    if lang == "en":
        stop_filter = "english_stop"
    elif lang == "cs":
        stop_filter = "czech_stop"
    else:
        raise ValueError(f"Unsupported language: {lang}")

    return {
        "settings": {
            "analysis": {
                "analyzer": {
                    "improved_tokenization_analyzer": {
                        "type": "custom",
                        "tokenizer": "improved_tokenization_tokenizer",
                        "filter": [stop_filter]
                    }
                },
                "tokenizer": {
                    "improved_tokenization_tokenizer": {
                        "type": "pattern",
                        "pattern": "[\\s\\p{Punct}]+"
                    }
                },
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_"
                    },
                    "czech_stop": {
                        "type": "stop",
                        "stopwords": "_czech_"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "docno": {"type": "keyword"},
                "text": {
                    "type": "text",
                    "analyzer": "improved_tokenization_analyzer",
                    "search_analyzer": "improved_tokenization_analyzer",
                    "term_vector": "yes"
                }
            }
        }
    }

# add lemmatization (en-3, cs-3) experiment 3
def run1_lemmatization_body(lang):
    if lang == "en":
        stop_filter = "english_stop"
    elif lang == "cs":
        stop_filter = "czech_stop"
    else:
        raise ValueError(f"Unsupported language: {lang}")

    return {
        "settings": {
            "analysis": {
                "analyzer": {
                    "lemmatized_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [stop_filter]
                    }
                },
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_"
                    },
                    "czech_stop": {
                        "type": "stop",
                        "stopwords": "_czech_"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "docno": {"type": "keyword"},
                "text": {
                    "type": "text",
                    "analyzer": "lemmatized_analyzer",
                    "search_analyzer": "lemmatized_analyzer",
                    "term_vector": "yes"
                }
            }
        }
    }

# add stemming for English only
def run1_stemming_body(lang):
    if lang == "en":
        filters = ["english_stop", "english_stemmer"]
    elif lang == "cs":
        filters = ["czech_stop"]
    else:
        raise ValueError(f"Unsupported language: {lang}")

    return {
        "settings": {
            "analysis": {
                "analyzer": {
                    "lemmatized_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": filters
                    }
                },
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_"
                    },
                    "czech_stop": {
                        "type": "stop",
                        "stopwords": "_czech_"
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "docno": {"type": "keyword"},
                "text": {
                    "type": "text",
                    "analyzer": "lemmatized_analyzer",
                    "search_analyzer": "lemmatized_analyzer",
                    "term_vector": "yes"
                }
            }
        }
    }

# add equivalence classes normalization
def run1_equivalence_body(lang):
    if lang == "en":
        filters = ["lowercase", "english_equivalence", "english_stop", "english_stemmer"]
        equivalences = EN_EQU

    elif lang == "cs":
        filters = ["lowercase", "czech_equivalence", "czech_stop"]
        equivalences = CS_EQU

    else:
        raise ValueError(f"Unsupported language: {lang}")

    return {
        "settings": {
            "analysis": {
                "analyzer": {
                    "equivalence_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": filters
                    }
                },
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_"
                    },
                    "czech_stop": {
                        "type": "stop",
                        "stopwords": "_czech_"
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english"
                    },
                    "english_equivalence": {
                        "type": "synonym",
                        "synonyms": equivalences
                    },
                    "czech_equivalence": {
                        "type": "synonym",
                        "synonyms": equivalences
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "docno": {"type": "keyword"},
                "text": {
                    "type": "text",
                    "analyzer": "equivalence_analyzer",
                    "search_analyzer": "equivalence_analyzer",
                    "term_vector": "yes"
                }
            }
        }
    }

def run1_dfr_body(lang):
    if lang == "en":
        filters = ["lowercase", "english_equivalence", "english_stop", "english_stemmer"]
        equivalences = EN_EQU
    elif lang == "cs":
        filters = ["lowercase", "czech_equivalence", "czech_stop"]
        equivalences = CS_EQU
    else:
        raise ValueError(f"Unsupported language: {lang}")

    return {
        "settings": {
            "index": {
                "similarity": {
                    "default": {
                        "type": "DFR",
                        "basic_model": "g",
                        "after_effect": "l",
                        "normalization": "h2",
                        "normalization.h2.c": "3.0"
                    }
                }
            },
            "analysis": {
                "analyzer": {
                    "dfr_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": filters
                    }
                },
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_"
                    },
                    "czech_stop": {
                        "type": "stop",
                        "stopwords": "_czech_"
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english"
                    },
                    "english_equivalence": {
                        "type": "synonym",
                        "synonyms": equivalences
                    },
                    "czech_equivalence": {
                        "type": "synonym",
                        "synonyms": equivalences
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "docno": {"type": "keyword"},
                "text": {
                    "type": "text",
                    "analyzer": "dfr_analyzer",
                    "search_analyzer": "dfr_analyzer",
                    "term_vector": "yes"
                }
            }
        }
    }

# final configuration
def run1_bm25_body(lang):
    if lang == "cs":
        analyzer = "czech_analyzer"
        k1, b = 1.5, 0.6
    else:
        analyzer = "english"
        k1, b = 1.2, 0.75

    return {
            "settings": {
                "index": {
                    "similarity": {
                        "default": {
                            "type": "BM25",
                            "k1": k1,
                            "b": b
                        }
                    }
                },
                "analysis": {
                    "analyzer": {
                        "czech_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "czech_stop", "czech_stemmer"]
                        }
                    },
                    "filter": {
                        "czech_stop": {
                            "type": "stop",
                            "stopwords": "_czech_"
                        },
                        "czech_stemmer": {
                            "type": "stemmer",
                            "language": "czech"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "docno": {"type": "keyword"},
                    "text": {
                        "type": "text",
                        "analyzer": analyzer,
                        "search_analyzer": analyzer,
                        "term_vector": "yes"
                    }
                }
            }
        }