#
# Pyserini: Reproducible IR research with sparse and dense representations
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

TF_INDEX_INFO = {
    "cacm": {
        "description": "Lucene index of the CACM corpus",
        "filename": "lucene-index.cacm.tar.gz",
        "urls": [
            "https://github.com/castorini/anserini-data/raw/master/CACM/lucene-index.cacm.tar.gz",
        ],
        "md5": "e47164fbd18aab72cdc18aecc0744bb1",
        "size compressed (bytes)": 2372903,
        "total_terms": 320968,
        "documents": 3204,
        "unique_terms": 14363,
    },
    "robust04": {
        "description": "Lucene index of TREC Disks 4 & 5 (minus Congressional Records), used in the TREC 2004 Robust Track",
        "filename": "index-robust04-20191213.tar.gz",
        "readme": "index-robust04-20191213-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-robust04-20191213.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/eqFacNeSGc4pLLH/download"
        ],
        "md5": "15f3d001489c97849a010b0a4734d018",
        "size compressed (bytes)": 1821814915,
        "total_terms": 174540872,
        "documents": 528030,
        "unique_terms": 923436,
    },

    "msmarco-passage-ltr": {
        "description": "Lucene index of the MS MARCO passage corpus with four extra preprocessed fields for LTR",
        "filename": "index-msmarco-passage-ltr-20210519-e25e33f.tar.gz",
        "readme": "index-msmarco-passage-ltr-20210519-e25e33f-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-msmarco-passage-ltr-20210519-e25e33f.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/8qFCaCtwabRfYQD/download"
        ],
        "md5": "a5de642c268ac1ed5892c069bdc29ae3",
        "size compressed (bytes)": 14073966046,
        "total_terms": 352316036,
        "documents": 8841823,
        "unique_terms": 2660824,
        "downloaded": False
    },
    "msmarco-doc-per-passage-ltr": {
        "description": "Lucene index of the MS MARCO document per-passage corpus with four extra preprocessed fields for LTR",
        "filename": "index-msmarco-doc-per-passage-ltr-20211031-33e4151.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-msmarco-doc-per-passage-ltr-20211031-33e4151.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/kNdXMWXEsTt3fT8/download"
        ],
        "md5": "bd60e89041b4ebbabc4bf0cfac608a87",
        "size compressed (bytes)": 45835520960,
        "total_terms": 1232004740,
        "documents": 20545628,
        "unique_terms": 10123678,
        "downloaded": False
    },

    # MS MARCO V1 document corpus, three indexes with different amounts of information (and sizes).
    "msmarco-v1-doc": {
        "description": "Lucene index of the MS MARCO V1 document corpus.",
        "filename": "lucene-index.msmarco-v1-doc.20220131.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-doc.20220131.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-doc.20220131.9ea315.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/aDRAfyZytQsQ9T3/download"
        ],
        "md5": "43b60b3fc75324c648a02375772e7fe8",
        "size compressed (bytes)": 13757573401,
        "total_terms": 2742209690,
        "documents": 3213835,
        "unique_terms": 29820456,
        "downloaded": False
    },
    "msmarco-v1-doc-slim": {
        "description": "Lucene index of the MS MARCO V1 document corpus ('slim' version).",
        "filename": "lucene-index.msmarco-v1-doc-slim.20220131.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-doc-slim.20220131.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-doc-slim.20220131.9ea315.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/iCnysqnaG9SL9pA/download"
        ],
        "md5": "17a7b079e9d527492904c7697a9cae59",
        "size compressed (bytes)": 1811599007,
        "total_terms": 2742209690,
        "documents": 3213835,
        "unique_terms": 29820456,
        "downloaded": False
    },
    "msmarco-v1-doc-full": {
        "description": "Lucene index of the MS MARCO V1 document corpus ('full' version).",
        "filename": "lucene-index.msmarco-v1-doc-full.20220131.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-doc-full.20220131.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-doc-full.20220131.9ea315.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/KsqZ2AwkSrTM8yS/download"
        ],
        "md5": "ef60d7f8afa3919cdeedc6fea89aa3f7",
        "size compressed (bytes)": 25548064269,
        "total_terms": 2742209690,
        "documents": 3213835,
        "unique_terms": 29820456,
        "downloaded": False
    },

    # MS MARCO V1 document corpus, doc2query-T5 expansions.
    "msmarco-v1-doc-d2q-t5": {
        "description": "Lucene index of the MS MARCO V1 document corpus, with doc2query-T5 expansions.",
        "filename": "lucene-index.msmarco-v1-doc-d2q-t5.20220201.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-doc-d2q-t5.20220201.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-doc-d2q-t5.20220201.9ea315.tar.gz"
        ],
        "md5": "37c639c9c26a34d2612ea6549fb866df",
        "size compressed (bytes)": 1904879520,
        "total_terms": 3748333319,
        "documents": 3213835,
        "unique_terms": 30627687,
        "downloaded": False
    },

    # MS MARCO V1 segmented document corpus, three indexes with different amounts of information (and sizes).
    "msmarco-v1-doc-segmented": {
        "description": "Lucene index of the MS MARCO V1 segmented document corpus.",
        "filename": "lucene-index.msmarco-v1-doc-segmented.20220131.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-doc-segmented.20220131.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-doc-segmented.20220131.9ea315.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/FKniAWGJjZHy3TF/download"
        ],
        "md5": "611bb83e043c0d6febe0fa3508d1d7f9",
        "size compressed (bytes)": 17091132803,
        "total_terms": 3200515914,
        "documents": 20545677,
        "unique_terms": 21190687,
        "downloaded": False
    },
    "msmarco-v1-doc-segmented-slim": {
        "description": "Lucene index of the MS MARCO V1 segmented document corpus ('slim' version).",
        "filename": "lucene-index.msmarco-v1-doc-segmented-slim.20220131.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-doc-segmented-slim.20220131.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-doc-segmented-slim.20220131.9ea315.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/QNYpaAcLXERr74y/download"
        ],
        "md5": "d42113cfeeea862b51765329795948ad",
        "size compressed (bytes)": 3408754542,
        "total_terms": 3200515914,
        "documents": 20545677,
        "unique_terms": 21190687,
        "downloaded": False
    },
    "msmarco-v1-doc-segmented-full": {
        "description": "Lucene index of the MS MARCO V1 segmented document corpus ('full' version).",
        "filename": "lucene-index.msmarco-v1-doc-segmented-full.20220131.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-doc-segmented-full.20220131.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-doc-segmented-full.20220131.9ea315.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/RzRBC6xkmaTsmX9/download"
        ],
        "md5": "2ed7457c8804d2d6370a1a7f604eb360",
        "size compressed (bytes)": 30771630666,
        "total_terms": 3200515914,
        "documents": 20545677,
        "unique_terms": 21190687,
        "downloaded": False
    },

    # MS MARCO V1 segmented document corpus, doc2query-T5 expansions.
    "msmarco-v1-doc-segmented-d2q-t5": {
        "description": "Lucene index of the MS MARCO V1 segmented document corpus, with doc2query-T5 expansions.",
        "filename": "lucene-index.msmarco-v1-doc-segmented-d2q-t5.20220201.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-doc-segmented-d2q-t5.20220201.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-doc-segmented-d2q-t5.20220201.9ea315.tar.gz"
        ],
        "md5": "6c1f86ee4f7175eed4d3a7acc3d567b8",
        "size compressed (bytes)": 3638703522,
        "total_terms": 4206639543,
        "documents": 20545677,
        "unique_terms": 22054207,
        "downloaded": False
    },

    # MS MARCO V1 passage corpus, three indexes with different amounts of information (and sizes).
    "msmarco-v1-passage": {
        "description": "Lucene index of the MS MARCO V1 passage corpus.",
        "filename": "lucene-index.msmarco-v1-passage.20220131.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-passage.20220131.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-passage.20220131.9ea315.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/L7yNfCXpqK5yf8e/download"
        ],
        "md5": "4d8fdbdcd119c1f47a4cc5d01a45dad3",
        "size compressed (bytes)": 2178557129,
        "total_terms": 352316036,
        "documents": 8841823,
        "unique_terms": 2660824,
        "downloaded": False
    },
    "msmarco-v1-passage-slim": {
        "description": "Lucene index of the MS MARCO V1 passage corpus ('slim' version).",
        "filename": "lucene-index.msmarco-v1-passage-slim.20220131.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-passage-slim.20220131.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-passage-slim.20220131.9ea315.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/swtPDQAGg6oHD8m/download"
        ],
        "md5": "2f1e50d60a0df32a50111a986159de51",
        "size compressed (bytes)": 498355616,
        "total_terms": 352316036,
        "documents": 8841823,
        "unique_terms": 2660824,
        "downloaded": False
    },
    "msmarco-v1-passage-full": {
        "description": "Lucene index of the MS MARCO V1 passage corpus ('full' version).",
        "filename": "lucene-index.msmarco-v1-passage-full.20220131.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-passage-full.20220131.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-passage-full.20220131.9ea315.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/wzGLFMQyKAc2TTC/download"
        ],
        "md5": "3283069c6e8451659c8ea83e2140d739",
        "size compressed (bytes)": 3781721749,
        "total_terms": 352316036,
        "documents": 8841823,
        "unique_terms": 2660824,
        "downloaded": False
    },

    # MS MARCO V1 passage corpus, doc2query-T5 expansions.
    "msmarco-v1-passage-d2q-t5": {
        "description": "Lucene index of the MS MARCO V1 passage corpus, with doc2query-T5 expansions.",
        "filename": "lucene-index.msmarco-v1-passage-d2q-t5.20220201.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v1-passage-d2q-t5.20220201.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-passage-d2q-t5.20220201.9ea315.tar.gz"
        ],
        "md5": "136205f35bd895077c0874eaa063376c",
        "size compressed (bytes)": 819441969,
        "total_terms": 1986612263,
        "documents": 8841823,
        "unique_terms": 3929111,
        "downloaded": False
    },

    # MS MARCO V2 document corpus, three indexes with different amounts of information (and sizes).
    "msmarco-v2-doc": {
        "description": "Lucene index of the MS MARCO V2 document corpus.",
        "filename": "lucene-index.msmarco-v2-doc.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-doc.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-doc.20220111.06fb4f.tar.gz"
        ],
        "md5": "3ca8b924f00f11e51e337c5421e55d96",
        "size compressed (bytes)": 63719115316,
        "total_terms": 14165661202,
        "documents": 11959635,
        "unique_terms": 44855557,
        "downloaded": False
    },
    "msmarco-v2-doc-slim": {
        "description": "Lucene index of the MS MARCO V2 document corpus ('slim' version).",
        "filename": "lucene-index.msmarco-v2-doc-slim.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-doc-slim.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-doc-slim.20220111.06fb4f.tar.gz"
        ],
        "md5": "502c4c96ecd95e4113a7a26a06065ecf",
        "size compressed (bytes)": 7306072104,
        "total_terms": 14165661202,
        "documents": 11959635,
        "unique_terms": 44855557,
        "downloaded": False
    },
    "msmarco-v2-doc-full": {
        "description": "Lucene index of the MS MARCO V2 document corpus ('full' version).",
        "filename": "lucene-index.msmarco-v2-doc-full.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-doc-full.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-doc-full.20220111.06fb4f.tar.gz"
        ],
        "md5": "cdb600adceccd327cb97c4277f910150",
        "size compressed (bytes)": 119577632837,
        "total_terms": 14165661202,
        "documents": 11959635,
        "unique_terms": 44855557,
        "downloaded": False
    },

    # MS MARCO V2 document corpus, doc2query-T5 expansions.
    "msmarco-v2-doc-d2q-t5": {
        "description": "Lucene index of the MS MARCO V2 document corpus, with doc2query-T5 expansions.",
        "filename": "lucene-index.msmarco-v2-doc-d2q-t5.20220201.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v2-doc-d2q-t5.20220201.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-doc-d2q-t5.20220201.9ea315.tar.gz"
        ],
        "md5": "431391554854c51f347ba38c5e07ef94",
        "size compressed (bytes)": 8254297093,
        "total_terms": 19760777295,
        "documents": 11959635,
        "unique_terms": 54143053,
        "downloaded": False
    },

    # MS MARCO V2 segmented document corpus, three indexes with different amounts of information (and sizes).
    "msmarco-v2-doc-segmented": {
        "description": "Lucene index of the MS MARCO V2 segmented document corpus.",
        "filename": "lucene-index.msmarco-v2-doc-segmented.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-doc-segmented.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-doc-segmented.20220111.06fb4f.tar.gz"
        ],
        "md5": "cb37211851bd0053227b8db1dd0a3853",
        "size compressed (bytes)": 105646039864,
        "total_terms": 24780915974,
        "documents": 124131414,
        "unique_terms": 29263590,
        "downloaded": False
    },
    "msmarco-v2-doc-segmented-slim": {
        "description": "Lucene index of the MS MARCO V2 segmented document corpus ('slim' version).",
        "filename": "lucene-index.msmarco-v2-doc-segmented-slim.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-doc-segmented-slim.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-doc-segmented-slim.20220111.06fb4f.tar.gz"
        ],
        "md5": "448c1e0e49c38364abbc4d880e865ee5",
        "size compressed (bytes)": 21004046043,
        "total_terms": 24780915974,
        "documents": 124131414,
        "unique_terms": 29263590,
        "downloaded": False
    },
    "msmarco-v2-doc-segmented-full": {
        "description": "Lucene index of the MS MARCO V2 segmented document corpus ('full' version).",
        "filename": "lucene-index.msmarco-v2-doc-segmented-full.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-doc-segmented-full.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-doc-segmented-full.20220111.06fb4f.tar.gz"
        ],
        "md5": "bb597b3d03eba00653387ffab8c01998",
        "size compressed (bytes)": 186377654091,
        "total_terms": 24780915974,
        "documents": 124131414,
        "unique_terms": 29263590,
        "downloaded": False
    },

    # MS MARCO V2 segmented document corpus, doc2query-T5 expansions.
    "msmarco-v2-doc-segmented-d2q-t5": {
        "description": "Lucene index of the MS MARCO V2 segmented document corpus, with doc2query-T5 expansions.",
        "filename": "lucene-index.msmarco-v2-doc-segmented-d2q-t5.20220201.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v2-doc-segmented-d2q-t5.20220201.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-doc-segmented-d2q-t5.20220201.9ea315.tar.gz"
        ],
        "md5": "3ce9eaca885e1e8a79466bee5e6a4084",
        "size compressed (bytes)": 24125355549,
        "total_terms": 30376032067,
        "documents": 124131414,
        "unique_terms": 38930475,
        "downloaded": False
    },

    # MS MARCO V2 passage corpus, three indexes with different amounts of information (and sizes).
    "msmarco-v2-passage": {
        "description": "Lucene index of the MS MARCO V2 passage corpus.",
        "filename": "lucene-index.msmarco-v2-passage.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage.20220111.06fb4f.tar.gz"
        ],
        "md5": "5990b4938dfdd092888ce9c9dfb6a90c",
        "size compressed (bytes)": 38013278576,
        "total_terms": 4673266762,
        "documents": 138364198,
        "unique_terms": 11885026,
        "downloaded": False
    },
    "msmarco-v2-passage-slim": {
        "description": "Lucene index of the MS MARCO V2 passage corpus ('slim' version).",
        "filename": "lucene-index.msmarco-v2-passage-slim.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage-slim.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage-slim.20220111.06fb4f.tar.gz"
        ],
        "md5": "b9a6fdf88775b0b546907d4cd84c4a58",
        "size compressed (bytes)": 8174630082,
        "total_terms": 4673266762,
        "documents": 138364198,
        "unique_terms": 11885026,
        "downloaded": False
    },
    "msmarco-v2-passage-full": {
        "description": "Lucene index of the MS MARCO V2 passage corpus ('full' version).",
        "filename": "lucene-index.msmarco-v2-passage-full.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage-full.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage-full.20220111.06fb4f.tar.gz"
        ],
        "md5": "a233873bef304dd87adef35f54c7a436",
        "size compressed (bytes)": 59658189636,
        "total_terms": 4673266762,
        "documents": 138364198,
        "unique_terms": 11885026,
        "downloaded": False
    },

    # MS MARCO V2 passage corpus, doc2query-T5 expansions.
    "msmarco-v2-passage-d2q-t5": {
        "description": "Lucene index of the MS MARCO V2 passage corpus, with doc2query-T5 expansions.",
        "filename": "lucene-index.msmarco-v2-passage-d2q-t5.20220201.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage-d2q-t5.20220201.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage-d2q-t5.20220201.9ea315.tar.gz"
        ],
        "md5": "72f3f0f56b9c7a1bdff836419f2f30bd",
        "size compressed (bytes)": 14431987438,
        "total_terms": 16961479226,
        "documents": 138364198,
        "unique_terms": 36650715,
        "downloaded": False
    },

    # MS MARCO V2 augmented passage corpus, three indexes with different amounts of information (and sizes).
    "msmarco-v2-passage-augmented": {
        "description": "Lucene index of the MS MARCO V2 augmented passage corpus.",
        "filename": "lucene-index.msmarco-v2-passage-augmented.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage-augmented.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage-augmented.20220111.06fb4f.tar.gz"
        ],
        "md5": "975f6be8d49238fe1d47e2895d26f99e",
        "size compressed (bytes)": 65574361728,
        "total_terms": 15272964956,
        "documents": 138364198,
        "unique_terms": 16579071,
        "downloaded": False
    },
    "msmarco-v2-passage-augmented-slim": {
        "description": "Lucene index of the MS MARCO V2 augmented passage corpus ('slim' version).",
        "filename": "lucene-index.msmarco-v2-passage-augmented-slim.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage-augmented-slim.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage-augmented-slim.20220111.06fb4f.tar.gz"
        ],
        "md5": "af893e56d050a98b6646ce2ca063d3f4",
        "size compressed (bytes)": 117322378611,
        "total_terms": 15272964956,
        "documents": 138364198,
        "unique_terms": 16579071,
        "downloaded": False
    },
    "msmarco-v2-passage-augmented-full": {
        "description": "Lucene index of the MS MARCO V2 augmented passage corpus ('full' version).",
        "filename": "lucene-index.msmarco-v2-passage-augmented-full.20220111.06fb4f.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage-augmented-full.20220111.06fb4f.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage-augmented-full.20220111.06fb4f.tar.gz"
        ],
        "md5": "e99f99503b9e030424546d59239f0cb5",
        "size compressed (bytes)": 14819003760,
        "total_terms": 15272964956,
        "documents": 138364198,
        "unique_terms": 16579071,
        "downloaded": False
    },

    # MS MARCO V2 augmented passage corpus, doc2query-T5 expansions.
    "msmarco-v2-passage-augmented-d2q-t5": {
        "description": "Lucene index of the MS MARCO V2 augmented passage corpus, with doc2query-T5 expansions.",
        "filename": "lucene-index.msmarco-v2-passage-augmented-d2q-t5.20220201.9ea315.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage-augmented-d2q-t5.20220201.9ea315.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage-augmented-d2q-t5.20220201.9ea315.tar.gz"
        ],
        "md5": "f248becbe3ef3fffc39680cff417791d",
        "size compressed (bytes)": 20940452572,
        "total_terms": 27561177420,
        "documents": 138364198,
        "unique_terms": 41176227,
        "downloaded": False
    },

    "enwiki-paragraphs": {
        "description": "Lucene index of English Wikipedia for BERTserini",
        "filename": "lucene-index.enwiki-20180701-paragraphs.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.enwiki-20180701-paragraphs.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/WHKMSCbwQfDXyHt/download"
        ],
        "md5": "77d1cd530579905dad2ee3c2bda1b73d",
        "size compressed (bytes)": 17725958785,
        "total_terms": 1498980668,
        "documents": 39880064,
        "unique_terms": -1,
        "downloaded": False
    },
    "zhwiki-paragraphs": {
        "description": "Lucene index of Chinese Wikipedia for BERTserini",
        "filename": "lucene-index.zhwiki-20181201-paragraphs.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.zhwiki-20181201-paragraphs.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/6kEjQZaRYtnb8A6/download"
        ],
        "md5": "c005af4036296972831288c894918a92",
        "size compressed (bytes)": 3284531213,
        "total_terms": 320776789,
        "documents": 4170312,
        "unique_terms": -1,
        "downloaded": False
    },
    "trec-covid-r5-abstract": {
        "description": "Lucene index for TREC-COVID Round 5: abstract index",
        "filename": "lucene-index-cord19-abstract-2020-07-16.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-07-16/lucene-index-cord19-abstract-2020-07-16.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/c37JxKYQ7Hogs72/download"
        ],
        "md5": "c883571ccc78b4c2ce05b41eb07f5405",
        "size compressed (bytes)": 2796524,
        "total_terms": 22100404,
        "documents": 192459,
        "unique_terms": 195875,
        "downloaded": False
    },
    "trec-covid-r5-full-text": {
        "description": "Lucene index for TREC-COVID Round 5: full-text index",
        "filename": "lucene-index-cord19-full-text-2020-07-16.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-07-16/lucene-index-cord19-full-text-2020-07-16.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/c7CcxRbFWfiFnFq/download"
        ],
        "md5": "23cfad89b4c206d66125f5736f60248f",
        "size compressed (bytes)": 5351744,
        "total_terms": 275238847,
        "documents": 192460,
        "unique_terms": 1843368,
        "downloaded": False
    },
    "trec-covid-r5-paragraph": {
        "description": "Lucene index for TREC-COVID Round 5: paragraph index",
        "filename": "lucene-index-cord19-paragraph-2020-07-16.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-07-16/lucene-index-cord19-paragraph-2020-07-16.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/HXigraF5KJL3xS8/download"
        ],
        "md5": "c2c6ac832f8a1fcb767d2356d2b1e1df",
        "size compressed (bytes)": 11352968,
        "total_terms": 627083574,
        "documents": 3010497,
        "unique_terms": 1843368,
        "downloaded": False
    },
    "trec-covid-r4-abstract": {
        "description": "Lucene index for TREC-COVID Round 4: abstract index",
        "filename": "lucene-index-cord19-abstract-2020-06-19.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-06-19/lucene-index-cord19-abstract-2020-06-19.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/fBta6sAt4MdaHQX/download"
        ],
        "md5": "029bd55daba8800fbae2be9e5fcd7b33",
        "size compressed (bytes)": 2584264,
        "total_terms": 18724353,
        "documents": 158226,
        "unique_terms": 179937,
        "downloaded": False
    },
    "trec-covid-r4-full-text": {
        "description": "Lucene index for TREC-COVID Round 4: full-text index",
        "filename": "lucene-index-cord19-full-text-2020-06-19.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-06-19/lucene-index-cord19-full-text-2020-06-19.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/yErSHZHD38jcDSY/download"
        ],
        "md5": "3d0eb12094a24cff9bcacd1f17c3ea1c",
        "size compressed (bytes)": 4983900,
        "total_terms": 254810123,
        "documents": 158227,
        "unique_terms": 1783089,
        "downloaded": False
    },
    "trec-covid-r4-paragraph": {
        "description": "Lucene index for TREC-COVID Round 4: paragraph index",
        "filename": "lucene-index-cord19-paragraph-2020-06-19.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-06-19/lucene-index-cord19-paragraph-2020-06-19.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/7md4kwNNgy3oxiH/download"
        ],
        "md5": "5cd8cd6998177bed7a3e0057ef8b3595",
        "size compressed (bytes)": 10382704,
        "total_terms": 567579834,
        "documents": 2781172,
        "unique_terms": 1783089,
        "downloaded": False
    },
    "trec-covid-r3-abstract": {
        "description": "Lucene index for TREC-COVID Round 3: abstract index",
        "filename": "lucene-index-cord19-abstract-2020-05-19.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-05-19/lucene-index-cord19-abstract-2020-05-19.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/Zg9p2D5tJgiTGx2/download"
        ],
        "md5": "37bb97d0c41d650ba8e135fd75ae8fd8",
        "size compressed (bytes)": 2190328,
        "total_terms": 16278419,
        "documents": 128465,
        "unique_terms": 168291,
        "downloaded": False
    },
    "trec-covid-r3-full-text": {
        "description": "Lucene index for TREC-COVID Round 3: full-text index",
        "filename": "lucene-index-cord19-full-text-2020-05-19.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-05-19/lucene-index-cord19-full-text-2020-05-19.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/BTzaQgZ55898dXM/download"
        ],
        "md5": "f5711915a66cd2b511e0fb8d03e4c325",
        "size compressed (bytes)": 4233300,
        "total_terms": 215806519,
        "documents": 128465,
        "unique_terms": 1620335,
        "downloaded": False
    },
    "trec-covid-r3-paragraph": {
        "description": "Lucene index for TREC-COVID Round 3: paragraph index",
        "filename": "lucene-index-cord19-paragraph-2020-05-19.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-05-19/lucene-index-cord19-paragraph-2020-05-19.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/nPyMYTys6NkmEdN/download"
        ],
        "md5": "012ab1f804382b2275c433a74d7d31f2",
        "size compressed (bytes)": 9053524,
        "total_terms": 485309568,
        "documents": 2297201,
        "unique_terms": 1620335,
        "downloaded": False
    },
    "trec-covid-r2-abstract": {
        "description": "Lucene index for TREC-COVID Round 2: abstract index",
        "filename": "lucene-index-cord19-abstract-2020-05-01.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-05-01/lucene-index-cord19-abstract-2020-05-01.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/3YZE65FSypwfnQQ/download"
        ],
        "md5": "a06e71a98a68d31148cb0e97e70a2ee1",
        "size compressed (bytes)": 1575804,
        "total_terms": 7651125,
        "documents": 59873,
        "unique_terms": 109750,
        "downloaded": False
    },
    "trec-covid-r2-full-text": {
        "description": "Lucene index for TREC-COVID Round 2: full-text index",
        "filename": "lucene-index-cord19-full-text-2020-05-01.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-05-01/lucene-index-cord19-full-text-2020-05-01.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/NdPEB7swXeZnq3o/download"
        ],
        "md5": "e7eca1b976cdf2cd80e908c9ac2263cb",
        "size compressed (bytes)": 3088540,
        "total_terms": 154736295,
        "documents": 59876,
        "unique_terms": 1214374,
        "downloaded": False
    },
    "trec-covid-r2-paragraph": {
        "description": "Lucene index for TREC-COVID Round 2: paragraph index",
        "filename": "lucene-index-cord19-paragraph-2020-05-01.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-05-01/lucene-index-cord19-paragraph-2020-05-01.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/Mz7n5FAt7rmnYCY/download"
        ],
        "md5": "8f9321757a03985ac1c1952b2fff2c7d",
        "size compressed (bytes)": 6881696,
        "total_terms": 360119048,
        "documents": 1758168,
        "unique_terms": 1214374,
        "downloaded": False
    },
    "trec-covid-r1-abstract": {
        "description": "Lucene index for TREC-COVID Round 1: abstract index",
        "filename": "lucene-index-covid-2020-04-10.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-04-10/lucene-index-covid-2020-04-10.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/Rz8AEmsFo9NWGP6/download"
        ],
        "md5": "ec239d56498c0e7b74e3b41e1ce5d42a",
        "size compressed (bytes)": 1621440,
        "total_terms": 6672525,
        "documents": 51069,
        "unique_terms": 104595,
        "downloaded": False
    },
    "trec-covid-r1-full-text": {
        "description": "Lucene index for TREC-COVID Round 1: full-text index",
        "filename": "lucene-index-covid-full-text-2020-04-10.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-04-10/lucene-index-covid-full-text-2020-04-10.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/oQzSoxrT3grGmBe/download"
        ],
        "md5": "401a6f5583b0f05340c73fbbeb3279c8",
        "size compressed (bytes)": 4471820,
        "total_terms": 315624154,
        "documents": 51071,
        "unique_terms": 1812522,
        "downloaded": False
    },
    "trec-covid-r1-paragraph": {
        "description": "Lucene index for TREC-COVID Round 1: paragraph index",
        "filename": "lucene-index-covid-paragraph-2020-04-10.tar.gz",
        "urls": [
            "https://git.uwaterloo.ca/jimmylin/cord19-indexes/raw/master/2020-04-10/lucene-index-covid-paragraph-2020-04-10.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/HDtb5Ys7MYBkePC/download"
        ],
        "md5": "8b87a2c55bc0a15b87f11e796860216a",
        "size compressed (bytes)": 5994192,
        "total_terms": 330715243,
        "documents": 1412648,
        "unique_terms": 944574,
        "downloaded": False
    },
    "cast2019": {
        "description": "Lucene index for TREC 2019 CaST",
        "filename": "index-cast2019.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-cast2019.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/56LcDcRPopdQc4d/download"
        ],
        "md5": "36e604d7f5a4e08ade54e446be2f6345",
        "size compressed (bytes)": 21266884884,
        "total_terms": 1593628213,
        "documents": 38429835,
        "unique_terms": -1,
        "downloaded": False
    },
    "wikipedia-dpr": {
        "description": "Lucene index of Wikipedia with DPR 100-word splits",
        "filename": "index-wikipedia-dpr-20210120-d1b9e6.tar.gz",
        "readme": "index-wikipedia-dpr-20210120-d1b9e6-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-wikipedia-dpr-20210120-d1b9e6.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/t6tDJmpoxPw9tH8/download"
        ],
        "md5": "c28f3a56b2dfcef25bf3bf755c264d04",
        "size compressed (bytes)": 9177942656,
        "total_terms": 1512973270,
        "documents": 21015324,
        "unique_terms": 5345463,
        "downloaded": False
    },
    "wikipedia-dpr-slim": {
        "description": "Lucene index of Wikipedia with DPR 100-word splits (slim version, document text not stored)",
        "filename": "index-wikipedia-dpr-slim-20210120-d1b9e6.tar.gz",
        "readme": "index-wikipedia-dpr-slim-20210120-d1b9e6-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-wikipedia-dpr-slim-20210120-d1b9e6.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/Gk2sfTyJCyaTrYH/download"
        ],
        "md5": "7d40604a824b5df37a1ae9d25ea38071",
        "size compressed (bytes)": 1810342390,
        "total_terms": 1512973270,
        "documents": 21015324,
        "unique_terms": 5345463,
        "downloaded": False
    },
    "wikipedia-kilt-doc": {
        "description": "Lucene index of Wikipedia snapshot used as KILT's knowledge source.",
        "filename": "index-wikipedia-kilt-doc-20210421-f29307.tar.gz",
        "readme": "index-wikipedia-kilt-doc-20210421-f29307-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-wikipedia-kilt-doc-20210421-f29307.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/RqtLg3CZT38k32c/download"
        ],
        "md5": "b8ec8feb654f7aaa86f9901dc6c804a8",
        "size compressed (bytes)": 10901127209,
        "total_terms": 1915061164,
        "documents": 5903530,
        "unique_terms": 8722502,
        "downloaded": False
    },
    "mrtydi-v1.1-arabic": {
        "description": "Lucene index for Mr.TyDi v1.1 (Arabic).",
        "filename": "lucene-index.mrtydi-v1.1-arabic.20220108.6fcb89.tar.gz",
        "readme": "lucene-index.mrtydi-v1.1-arabic.20220108.6fcb89.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.mrtydi-v1.1-arabic.20220108.6fcb89.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/7oDFnq8FmTazf2a/download"
        ],
        "md5": "0129b01cc88524e13a9ff3e398e988a5",
        "size compressed (bytes)": 1172153418,
        "total_terms": 92529014,
        "documents": 2106586,
        "unique_terms": 1284712,
        "downloaded": False
    },
    "mrtydi-v1.1-bengali": {
        "description": "Lucene index for Mr.TyDi v1.1 (Bengali).",
        "filename": "lucene-index.mrtydi-v1.1-bengali.20220108.6fcb89.tar.gz",
        "readme": "lucene-index.mrtydi-v1.1-bengali.20220108.6fcb89.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.mrtydi-v1.1-bengali.20220108.6fcb89.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/HaPaz2wFbRMP2LK/download"
        ],
        "md5": "756a686cc5723791eb5ab5357271be10",
        "size compressed (bytes)": 240371052,
        "total_terms": 15236598,
        "documents": 304059,
        "unique_terms": 520694,
        "downloaded": False
    },
    "mrtydi-v1.1-english": {
        "description": "Lucene index for Mr.TyDi v1.1 (English).",
        "filename": "lucene-index.mrtydi-v1.1-english.20220108.6fcb89.tar.gz",
        "readme": "lucene-index.mrtydi-v1.1-english.20220108.6fcb89.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.mrtydi-v1.1-english.20220108.6fcb89.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/w4ccMwH5BLnXQ3j/download"
        ],
        "md5": "804c7626b5a36f06f75e0a04c6ec4fe1",
        "size compressed (bytes)": 16772744114,
        "total_terms": 1507060955,
        "documents": 32907100,
        "unique_terms": 6189349,
        "downloaded": False
    },
    "mrtydi-v1.1-finnish": {
        "description": "Lucene index for Mr.TyDi v1.1 (Finnish).",
        "filename": "lucene-index.mrtydi-v1.1-finnish.20220108.6fcb89.tar.gz",
        "readme": "lucene-index.mrtydi-v1.1-finnish.20220108.6fcb89.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.mrtydi-v1.1-finnish.20220108.6fcb89.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/Pgd3mqjy77a6FR8/download"
        ],
        "md5": "65361258d1a318447f364ccae90c293a",
        "size compressed (bytes)": 908904453,
        "total_terms": 69431615,
        "documents": 1908757,
        "unique_terms": 1709590,
        "downloaded": False
    },
    "mrtydi-v1.1-indonesian": {
        "description": "Lucene index for Mr.TyDi v1.1 (Indonesian).",
        "filename": "lucene-index.mrtydi-v1.1-indonesian.20220108.6fcb89.tar.gz",
        "readme": "lucene-index.mrtydi-v1.1-indonesian.20220108.6fcb89.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.mrtydi-v1.1-indonesian.20220108.6fcb89.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/tF8NE7pWZ2xGix7/download"
        ],
        "md5": "ca62d690401b84a493c70693ee2626c3",
        "size compressed (bytes)": 564741230,
        "total_terms": 52493134,
        "documents": 1469399,
        "unique_terms": 942550,
        "downloaded": False
    },
    "mrtydi-v1.1-japanese": {
        "description": "Lucene index for Mr.TyDi v1.1 (Japanese).",
        "filename": "lucene-index.mrtydi-v1.1-japanese.20220108.6fcb89.tar.gz",
        "readme": "lucene-index.mrtydi-v1.1-japanese.20220108.6fcb89.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.mrtydi-v1.1-japanese.20220108.6fcb89.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/ema8i83zqJr7n48/download"
        ],
        "md5": "d05aefed5f79bfc151a9f4815d3693d8",
        "size compressed (bytes)": 3670762373,
        "total_terms": 303640353,
        "documents": 7000027,
        "unique_terms": 1708155,
        "downloaded": False
    },
    "mrtydi-v1.1-korean": {
        "description": "Lucene index for Mr.TyDi v1.1 (Korean).",
        "filename": "lucene-index.mrtydi-v1.1-korean.20220108.6fcb89.tar.gz",
        "readme": "lucene-index.mrtydi-v1.1-korean.20220108.6fcb89.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.mrtydi-v1.1-korean.20220108.6fcb89.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/igmEHCTjTwNi3de/download"
        ],
        "md5": "4ecc408de4c749f25865859ea97278bd",
        "size compressed (bytes)": 1141503582,
        "total_terms": 122217290,
        "documents": 1496126,
        "unique_terms": 1517175,
        "downloaded": False
    },
    "mrtydi-v1.1-russian": {
        "description": "Lucene index for Mr.TyDi v1.1 (Russian).",
        "filename": "lucene-index.mrtydi-v1.1-russian.20220108.6fcb89.tar.gz",
        "readme": "lucene-index.mrtydi-v1.1-russian.20220108.6fcb89.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.mrtydi-v1.1-russian.20220108.6fcb89.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/Pbi9xrD7jSYaxnX/download"
        ],
        "md5": "9e229b33f4ddea411477d2f00c25be72",
        "size compressed (bytes)": 5672456411,
        "total_terms": 346329152,
        "documents": 9597504,
        "unique_terms": 3059773,
        "downloaded": False
    },
    "mrtydi-v1.1-swahili": {
        "description": "Lucene index for Mr.TyDi v1.1 (Swahili).",
        "filename": "lucene-index.mrtydi-v1.1-swahili.20220108.6fcb89.tar.gz",
        "readme": "lucene-index.mrtydi-v1.1-swahili.20220108.6fcb89.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.mrtydi-v1.1-swahili.20220108.6fcb89.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/SWqajDQgq8wppf6/download"
        ],
        "md5": "ec88a5b39c2506b8cd61e6e47b8044e7",
        "size compressed (bytes)": 47689785,
        "total_terms": 4937051,
        "documents": 136689,
        "unique_terms": 385711,
        "downloaded": False
    },
    "mrtydi-v1.1-telugu": {
        "description": "Lucene index for Mr.TyDi v1.1 (Telugu).",
        "filename": "lucene-index.mrtydi-v1.1-telugu.20220108.6fcb89.tar.gz",
        "readme": "lucene-index.mrtydi-v1.1-telugu.20220108.6fcb89.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.mrtydi-v1.1-telugu.20220108.6fcb89.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/DAB6ba5ZF98awH6/download"
        ],
        "md5": "2704b725c0418905037a45b6301e8666",
        "size compressed (bytes)": 452906283,
        "total_terms": 27173644,
        "documents": 548224,
        "unique_terms": 1892900,
        "downloaded": False
    },
    "mrtydi-v1.1-thai": {
        "description": "Lucene index for Mr.TyDi v1.1 (Thai).",
        "filename": "lucene-index.mrtydi-v1.1-thai.20220108.6fcb89.tar.gz",
        "readme": "lucene-index.mrtydi-v1.1-thai.20220108.6fcb89.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.mrtydi-v1.1-thai.20220108.6fcb89.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/2Ady6AwBwNbYLpg/download"
        ],
        "md5": "9756502f1aeeee035c37975202787538",
        "size compressed (bytes)": 452244053,
        "total_terms": 31550936,
        "documents": 568855,
        "unique_terms": 663628,
        "downloaded": False
    },

    # These MS MARCO V1 indexes are deprecated, but keeping around for archival reasons
    "msmarco-passage": {
        "description": "Lucene index of the MS MARCO passage corpus (deprecated; use msmarco-v1-passage instead).",
        "filename": "index-msmarco-passage-20201117-f87c94.tar.gz",
        "readme": "index-msmarco-passage-20201117-f87c94-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-msmarco-passage-20201117-f87c94.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/QQsZMFG8MpF4P8M/download"
        ],
        "md5": "1efad4f1ae6a77e235042eff4be1612d",
        "size compressed (bytes)": 2218470796,
        "total_terms": 352316036,
        "documents": 8841823,
        "unique_terms": 2660824,
        "downloaded": False
    },
    "msmarco-passage-slim": {
        "description": "Lucene index of the MS MARCO passage corpus (slim version, document text not stored) (deprecated; use msmarco-v1-passage-slim instead).",
        "filename": "index-msmarco-passage-slim-20201202-ab6e28.tar.gz",
        "readme": "index-msmarco-passage-slim-20201202-ab6e28-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-msmarco-passage-slim-20201202-ab6e28.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/Kx6K9NJFmwnaAP8/download"
        ],
        "md5": "5e11da4cebd2e8dda2e73c589ffb0b4c",
        "size compressed (bytes)": 513566686,
        "total_terms": 352316036,
        "documents": 8841823,
        "unique_terms": 2660824,
        "downloaded": False
    },
    "msmarco-doc": {
        "description": "Lucene index of the MS MARCO document corpus (deprecated; use msmarco-v1-doc instead).",
        "filename": "index-msmarco-doc-20201117-f87c94.tar.gz",
        "readme": "index-msmarco-doc-20201117-f87c94-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-msmarco-doc-20201117-f87c94.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/5NC7A2wAL7opJKH/download"
        ],
        "md5": "ac747860e7a37aed37cc30ed3990f273",
        "size compressed (bytes)": 13642330935,
        "total_terms": 2748636047,
        "documents": 3213835,
        "unique_terms": 29823078,
        "downloaded": False
    },
    "msmarco-doc-slim": {
        "description": "Lucene index of the MS MARCO document corpus (slim version, document text not stored) (deprecated; use msmarco-v1-doc-slim instead).",
        "filename": "index-msmarco-doc-slim-20201202-ab6e28.tar.gz",
        "readme": "index-msmarco-doc-slim-20201202-ab6e28-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-msmarco-doc-slim-20201202-ab6e28.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/BMZ6oYBoEPgTFqs/download"
        ],
        "md5": "c56e752f7992bf6149761097641d515a",
        "size compressed (bytes)": 1874471867,
        "total_terms": 2748636047,
        "documents": 3213835,
        "unique_terms": 29823078,
        "downloaded": False
    },
    "msmarco-doc-per-passage": {
        "description": "Lucene index of the MS MARCO document corpus segmented into passages (deprecated; use msmarco-v1-doc-segmented instead).",
        "filename": "index-msmarco-doc-per-passage-20201204-f50dcc.tar.gz",
        "readme": "index-msmarco-doc-per-passage-20201204-f50dcc-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-msmarco-doc-per-passage-20201204-f50dcc.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/q6sAxE6q57q2TBo/download"
        ],
        "md5": "797367406a7542b649cefa6b41cf4c33",
        "size compressed (bytes)": 11602951258,
        "total_terms": 3197886407,
        "documents": 20544550,
        "unique_terms": 21173582,
        "downloaded": False
    },
    "msmarco-doc-per-passage-slim": {
        "description": "Lucene index of the MS MARCO document corpus segmented into passages (slim version, document text not stored) (deprecated; use msmarco-v1-doc-segmented-slim instead).",
        "filename": "index-msmarco-doc-per-passage-slim-20201204-f50dcc.tar.gz",
        "readme": "index-msmarco-doc-per-passage-slim-20201204-f50dcc-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-msmarco-doc-per-passage-slim-20201204-f50dcc.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/mKTjbTKMwWF9kY3/download"
        ],
        "md5": "77c2409943a8c9faffabf57cb6adca69",
        "size compressed (bytes)": 2834865200,
        "total_terms": 3197886407,
        "documents": 20544550,
        "unique_terms": 21173582,
        "downloaded": False
    },

    # These MS MARCO V1 doc2query expansion indexes are deprecated, but keeping around for archival reasons
    "msmarco-passage-expanded": {
        "description": "Lucene index of the MS MARCO passage corpus with docTTTTTquery expansions (deprecated; use msmarco-v1-passage-d2q-t5 instead)",
        "filename": "index-msmarco-passage-expanded-20201121-e127fb.tar.gz",
        "readme": "index-msmarco-passage-expanded-20201121-e127fb-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-msmarco-passage-expanded-20201121-e127fb.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/pm7cisJtRxiAMHd/download"
        ],
        "md5": "e5762e9e065b6fe5000f9c18da778565",
        "size compressed (bytes)": 816438546,
        "total_terms": 1986612263,
        "documents": 8841823,
        "unique_terms": 3929111,
        "downloaded": False
    },
    "msmarco-doc-expanded-per-doc": {
        "description": "Lucene index of the MS MARCO document corpus with per-doc docTTTTTquery expansions (deprecated; use msmarco-v1-doc-d2q-t5 instead)",
        "filename": "index-msmarco-doc-expanded-per-doc-20201126-1b4d0a.tar.gz",
        "readme": "index-msmarco-doc-expanded-per-doc-20201126-1b4d0a-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-msmarco-doc-expanded-per-doc-20201126-1b4d0a.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/3BQz6ZAXAxtfne8/download"
        ],
        "md5": "f7056191842ab77a01829cff68004782",
        "size compressed (bytes)": 1978837253,
        "total_terms": 3748333319,
        "documents": 3213835,
        "unique_terms": 30627687,
        "downloaded": False
    },
    "msmarco-doc-expanded-per-passage": {
        "description": "Lucene index of the MS MARCO document corpus with per-passage docTTTTTquery expansions (deprecated; use msmarco-v1-doc-segmented-d2q-t5 instead)",
        "filename": "index-msmarco-doc-expanded-per-passage-20201126-1b4d0a.tar.gz",
        "readme": "index-msmarco-doc-expanded-per-passage-20201126-1b4d0a-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/index-msmarco-doc-expanded-per-passage-20201126-1b4d0a.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/eZLbPWcnB7LzKnQ/download"
        ],
        "md5": "54ea30c64515edf3c3741291b785be53",
        "size compressed (bytes)": 3069280946,
        "total_terms": 4203956960,
        "documents": 20544550,
        "unique_terms": 22037213,
        "downloaded": False
    }
}

IMPACT_INDEX_INFO = {
    "msmarco-v1-passage-unicoil": {
        "description": "Lucene impact index of the MS MARCO V1 passage corpus for uniCOIL.",
        "filename": "lucene-index.msmarco-v1-passage-unicoil.20220219.6a7080.tar.gz",
        "readme": "lucene-index.msmarco-v1-passage-unicoil.20220219.6a7080.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-passage-unicoil.20220219.6a7080.tar.gz",
        ],
        "md5": "c589978ffccaa4f116b89ad756f53b89",
        "size compressed (bytes)": 1189212017,
        "total_terms": 44495093768,
        "documents": 8841823,
        "unique_terms": 27678,
        "downloaded": False
    },
    "msmarco-v1-doc-segmented-unicoil": {
        "description": "Lucene impact index of the MS MARCO V1 segmented document corpus for uniCOIL.",
        "filename": "lucene-index.msmarco-v1-doc-segmented-unicoil.20220219.6a7080.tar.gz",
        "readme": "lucene-index.msmarco-v1-doc-segmented-unicoil.20220219.6a7080.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v1-doc-segmented-unicoil.20220219.6a7080.tar.gz",
        ],
        "md5": "393ad1227b9906c8776a4fbaddab4e9d",
        "size compressed (bytes)": 5891112039,
        "total_terms": 214505277898,
        "documents": 20545677,
        "unique_terms": 29142,
        "downloaded": False
    },
    "msmarco-v2-passage-unicoil-0shot": {
        "description": "Lucene impact index of the MS MARCO V2 passage corpus for uniCOIL.",
        "filename": "lucene-index.msmarco-v2-passage-unicoil-0shot.20220219.6a7080.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage-unicoil-0shot.20220219.6a7080.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage-unicoil-0shot.20220219.6a7080.tar.gz",
        ],
        "md5": "ea024b0dd43a574deb65942e14d32630",
        "size compressed (bytes)": 22212154603,
        "total_terms": 775253560148,
        "documents": 138364198,
        "unique_terms": 29149,
        "downloaded": False
    },
    "msmarco-v2-passage-unicoil-noexp-0shot": {
        "description": "Lucene impact index of the MS MARCO V2 passage corpus for uniCOIL (noexp).",
        "filename": "lucene-index.msmarco-v2-passage-unicoil-noexp-0shot.20220219.6a7080.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage-unicoil-noexp-0shot.20220219.6a7080.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage-unicoil-noexp-0shot.20220219.6a7080.tar.gz",
        ],
        "md5": "fb356e7614afc07e330b0559ae5cef18",
        "size compressed (bytes)": 14615689637,
        "total_terms": 411330032512,
        "documents": 138364198,
        "unique_terms": 29148,
        "downloaded": False
    },
    "msmarco-v2-doc-segmented-unicoil-0shot": {
        "description": "Lucene impact index of the MS MARCO V2 segmented document corpus for uniCOIL.",
        "filename": "lucene-index.msmarco-v2-doc-segmented-unicoil-0shot.20220219.6a7080.tar.gz",
        "readme": "lucene-index.msmarco-v2-doc-segmented-unicoil-0shot.20220219.6a7080.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-doc-segmented-unicoil-0shot.20220219.6a7080.tar.gz",
        ],
        "md5": "94fc8af0d08682f7c79ffb16d82dcfab",
        "size compressed (bytes)": 32787358081,
        "total_terms": 1185840285417,
        "documents": 124131414,
        "unique_terms": 29169,
        "downloaded": False
    },
    "msmarco-v2-doc-segmented-unicoil-noexp-0shot": {
        "description": "Lucene impact index of the MS MARCO V2 segmented document corpus for uniCOIL (noexp).",
        "filename": "lucene-index.msmarco-v2-doc-segmented-unicoil-noexp-0shot.20220219.6a7080.tar.gz",
        "readme": "lucene-index.msmarco-v2-doc-segmented-unicoil-noexp-0shot.20220219.6a7080.README.md",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-doc-segmented-unicoil-noexp-0shot.20220219.6a7080.tar.gz",
        ],
        "md5": "d7807b60087b630010e9c31b59d30b69",
        "size compressed (bytes)": 28640356748,
        "total_terms": 805830282591,
        "documents": 124131404,
        "unique_terms": 29172,
        "downloaded": False
    },

    "msmarco-passage-deepimpact": {
        "description": "Lucene impact index of the MS MARCO passage corpus encoded by DeepImpact",
        "filename": "lucene-index.msmarco-passage.deepimpact.20211012.58d286.tar.gz",
        "readme": "lucene-index.msmarco-passage.deepimpact.20211012.58d286.readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-passage.deepimpact.20211012.58d286.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/FfwF6nB9M5sjTYk/download",
        ],
        "md5": "9938f5529fee5cdb405b8587746c9e93",
        "size compressed (bytes)": 1295216704,
        "total_terms": 35455908214,
        "documents": 8841823,
        "unique_terms": 3514102,
        "downloaded": False
    },

    "msmarco-passage-unicoil-tilde": {
        "description": "Lucene impact index of the MS MARCO passage corpus encoded by uniCOIL-TILDE",
        "filename": "lucene-index.msmarco-passage.unicoil-tilde.20211012.58d286.tar.gz",
        "readme": "lucene-index.msmarco-passage.unicoil-tilde.20211012.58d286.readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-passage.unicoil-tilde.20211012.58d286.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/KdoNXqwAtTmTeNo/download"
        ],
        "md5": "cc19cfe241053f5a303f7f05a7ac40a5",
        "size compressed (bytes)": 1935108302,
        "total_terms": 73040108576,
        "documents": 8841823,
        "unique_terms": 27646,
        "downloaded": False
    },
    "msmarco-passage-distill-splade-max": {
        "description": "Lucene impact index of the MS MARCO passage corpus encoded by distill-splade-max",
        "filename": "lucene-index.msmarco-passage.distill-splade-max.20211012.58d286.tar.gz",
        "readme": "lucene-index.msmarco-passage.distill-splade-max.20211012.58d286.readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-passage.distill-splade-max.20211012.58d286.tar.gz"
        ],
        "md5": "957c0dd1b78b61aeddc8685150fd8360",
        "size compressed (bytes)": 4604547518,
        "total_terms": 95445422483,
        "documents": 8841823,
        "unique_terms": 28131,
        "downloaded": False
    },
    "msmarco-v2-passage-unicoil-tilde": {
        "description": "Lucene impact index of the MS MARCO V2 passage corpus encoded by uniCOIL-TILDE",
        "filename": "lucene-index.msmarco-v2-passage.unicoil-tilde.20211012.58d286.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage.unicoil-tilde.20211012.58d286.readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage.unicoil-tilde.20211012.58d286.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/oGQ8tWifozPaHLK/download"
        ],
        "md5": "562f9534eefe04ab8c07beb304074d41",
        "size compressed (bytes)": 31168302160,
        "total_terms": 1155211154985,
        "documents": 138364198,
        "unique_terms": 29149,
        "downloaded": False
    },

    # These MS MARCO uniCOIL models are deprecated, but keeping around for archival reasons
    "msmarco-passage-unicoil-d2q": {
        "description": "Lucene impact index of the MS MARCO passage corpus encoded by uniCOIL-d2q (deprecated; use msmarco-v1-passage-unicoil instead).",
        "filename": "lucene-index.msmarco-passage.unicoil-d2q.20211012.58d286.tar.gz",
        "readme": "lucene-index.msmarco-passage.unicoil-d2q.20211012.58d286.readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-passage.unicoil-d2q.20211012.58d286.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/LGoAAXM7ZEbyQ7y/download"
        ],
        "md5": "4a8cb3b86a0d9085a0860c7f7bb7fe99",
        "size compressed (bytes)": 1205104390,
        "total_terms": 44495093768,
        "documents": 8841823,
        "unique_terms": 27678,
        "downloaded": False
    },
    "msmarco-doc-per-passage-unicoil-d2q": {
        "description": "Lucene impact index of the MS MARCO doc corpus per passage expansion encoded by uniCOIL-d2q (deprecated; use msmarco-v1-doc-segmented-unicoil instead).",
        "filename": "lucene-index.msmarco-doc-per-passage-expansion.unicoil-d2q.20211012.58d286.tar.gz",
        "readme": "lucene-index.msmarco-doc-per-passage-expansion.unicoil-d2q.20211012.58d286.readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-doc-per-passage-expansion.unicoil-d2q.20211012.58d286.tar.gz",
        ],
        "md5": "44bfc848f9a77302b10a59c5b136eb95",
        "size compressed (bytes)": 5945466106,
        "total_terms": 214505277898,
        "documents": 20545677,
        "unique_terms": 29142,
        "downloaded": False
    },
    "msmarco-v2-passage-unicoil-noexp-0shot-deprecated": {
        "description": "Lucene impact index of the MS MARCO V2 passage corpus encoded by uniCOIL (zero-shot, no expansions) (deprecated; use msmarco-v2-passage-unicoil-noexp-0shot instead).",
        "filename": "lucene-index.msmarco-v2-passage.unicoil-noexp-0shot.20211012.58d286.tar.gz",
        "readme": "lucene-index.msmarco-v2-passage.unicoil-noexp-0shot.20211012.58d286.readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-passage.unicoil-noexp-0shot.20211012.58d286.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/eXA2BHF8WQjdY8R/download"
        ],
        "md5": "8886a8d9599838bc6d8d61464da61086",
        "size compressed (bytes)": 14801476783,
        "total_terms": 411330032512,
        "documents": 138364198,
        "unique_terms": 29148,
        "downloaded": False
    },
    "msmarco-v2-doc-per-passage-unicoil-noexp-0shot": {
        "description": "Lucene impact index of the MS MARCO V2 document corpus per passage encoded by uniCOIL (zero-shot, no expansions) (deprecated; msmarco-v2-doc-segmented-unicoil-noexp-0shot).",
        "filename": "lucene-index.msmarco-v2-doc-per-passage.unicoil-noexp-0shot.20211012.58d286.tar.gz",
        "readme": "lucene-index.msmarco-v2-doc-per-passage.unicoil-noexp-0shot.20211012.58d286.readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/lucene-index.msmarco-v2-doc-per-passage.unicoil-noexp-0shot.20211012.58d286.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/BSrJmAFJywsRYXo/download"
        ],
        "md5": "1980db886d969c3393e4da20190eaa8f",
        "size compressed (bytes)": 29229949764,
        "total_terms": 805830282591,
        "documents": 124131404,
        "unique_terms": 29172,
        "downloaded": False
    }
}

FAISS_INDEX_INFO = {
    "msmarco-passage-tct_colbert-hnsw": {
        "description": "Faiss HNSW index of the MS MARCO passage corpus encoded by TCT-ColBERT",
        "filename": "dindex-msmarco-passage-tct_colbert-hnsw-20210112-be7119.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-msmarco-passage-tct_colbert-hnsw-20210112-be7119.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/F6MjyjmCi6yHFTa/download"
        ],
        "md5": "7e12ae728ea5f2ae6d1cfb88a8775ba8",
        "size compressed (bytes)": 33359100887,
        "documents": 8841823,
        "downloaded": False,
        "texts": "msmarco-passage"
    },
    "msmarco-passage-tct_colbert-bf": {
        "description": "Faiss FlatIP index of the MS MARCO passage corpus encoded by TCT-ColBERT",
        "filename": "dindex-msmarco-passage-tct_colbert-bf-20210112-be7119.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-msmarco-passage-tct_colbert-bf-20210112-be7119.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/mHxezzSAkrWbXZC/download"
        ],
        "md5": "7312e0e7acec2a686e994902ca064fc5",
        "size compressed (bytes)": 25204514289,
        "documents": 8841823,
        "downloaded": False,
        "texts": "msmarco-passage"
    },
    "msmarco-doc-tct_colbert-bf": {
        "description": "Faiss FlatIP index of the MS MARCO document corpus encoded by TCT-ColBERT",
        "filename": "dindex-msmarco-doc-tct_colbert-bf-20210112-be7119.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-msmarco-doc-tct_colbert-bf-20210112-be7119.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/Ti5JxdCgjdw3noq/download"
        ],
        "md5": "f0b4c3bff3bb685be5c475511004c3b0",
        "size compressed (bytes)": 58514325936,
        "documents": 20544550,
        "downloaded": False,
        "texts": "msmarco-passage"
    },
    "msmarco-doc-tct_colbert-v2-hnp-bf": {
        "description": "Faiss FlatIP index of the MS MARCO document corpus encoded by TCT-ColBERT-V2-HNP",
        "filename": "faiss-flat.msmarco-doc-per-passage.tct_colbert-v2-hnp.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/faiss-flat.msmarco-doc-per-passage.tct_colbert-v2-hnp.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/XjkKAWMz2fwSeJB/download",
        ],
        "md5": "c6a7d295cfe711ef84dffe9ba6a702e5",
        "size compressed (bytes)": 58586765624,
        "documents": 20544550,
        "downloaded": False,
        "texts": "msmarco-passage"
    },
    "wikipedia-dpr-multi-bf": {
        "description": "Faiss FlatIP index of Wikipedia encoded by the DPR doc encoder trained on multiple QA datasets",
        "filename": "dindex-wikipedia-dpr_multi-bf-20200127-f403c3.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-wikipedia-dpr_multi-bf-20200127-f403c3.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/xN44ZSC9tFFtp3F/download"
        ],
        "md5": "29eb39fe0b00a03c36c0eeae4c24f775",
        "size compressed (bytes)": 59836766981,
        "documents": 21015320,
        "downloaded": False,
        "texts": "wikipedia-dpr"
    },
    "wikipedia-dpr-single-nq-bf": {
        "description": "Faiss FlatIP index of Wikipedia encoded by the DPR doc encoder trained on NQ",
        "filename": "dindex-wikipedia-dpr_single_nq-bf-20200115-cd5034.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-wikipedia-dpr_single_nq-bf-20200115-cd5034.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/W4k44aLZWcbcJXe/download"
        ],
        "md5": "d1ef9286ddb38633cd052171963c62cb",
        "size compressed (bytes)": 59836863670,
        "documents": 21015320,
        "downloaded": False,
        "texts": "wikipedia-dpr"
    },
    "wikipedia-bpr-single-nq-hash": {
        "description": "Faiss binary index of Wikipedia encoded by the BPR doc encoder trained on NQ",
        "filename": "dindex-wikipedia_bpr_single_nq-hash-20210827-8a8f75.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-wikipedia_bpr_single_nq-hash-20210827-8a8f75.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/qKFrptGP4pSp987/download"
        ],
        "md5": "e60e5ed1d7fab924bfa9149ed169d082",
        "size compressed (bytes)": 1887382350,
        "documents": 21015320,
        "downloaded": False,
        "texts": "wikipedia-dpr"
    },
    "msmarco-passage-ance-bf": {
        "description": "Faiss FlatIP index of the MS MARCO passage corpus encoded by the ANCE MS MARCO passage encoder",
        "filename": "dindex-msmarco-passage-ance-bf-20210224-060cef.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-msmarco-passage-ance-bf-20210224-060cef.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/mntwDQtXc9WbZSM/download"
        ],
        "md5": "f6332edb8f06ba796850388cf975b414",
        "size compressed (bytes)": 25102344985,
        "documents": 8841823,
        "downloaded": False,
        "texts": "msmarco-passage"
    },
    "msmarco-doc-ance-maxp-bf": {
        "description": "Faiss FlatIP index of the MS MARCO document corpus encoded by the ANCE MaxP encoder",
        "filename": "dindex-msmarco-doc-ance_maxp-bf-20210304-b2a1b0.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-msmarco-doc-ance_maxp-bf-20210304-b2a1b0.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/ifXbHmgTz27SYCC/download"
        ],
        "md5": "a9f8d77ea0cef7c6acdba881c45b7d99",
        "size compressed (bytes)": 58312805496,
        "documents": 20544550,
        "downloaded": False,
        "texts": "msmarco-doc"
    },
    "wikipedia-ance-multi-bf": {
        "description": "Faiss FlatIP index of Wikipedia encoded by the ANCE-multi encoder",
        "filename": "dindex-wikipedia-ance_multi-bf-20210224-060cef.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-wikipedia-ance_multi-bf-20210224-060cef.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/XRGYFBN6d6WZRNw/download"
        ],
        "md5": "715605b56dc393b8f939e12682dfd467",
        "size compressed (bytes)": 59890492088,
        "documents": 21015320,
        "downloaded": False,
        "texts": "wikipedia-dpr"
    },
    "msmarco-passage-sbert-bf": {
        "description": "Faiss FlatIP index of the MS MARCO passage corpus encoded by the SBERT MS MARCO passage encoder",
        "filename": "dindex-msmarco-passage-sbert-bf-20210313-a0fbb3.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-msmarco-passage-sbert-bf-20210313-a0fbb3.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/8xiZK5cx4ffExoz/download"
        ],
        "md5": "3f98b9564cd3a33e45bfeca4d4fec623",
        "size compressed (bytes)": 25214193901,
        "documents": 8841823,
        "downloaded": False,
        "texts": "msmarco-passage"
    },
    "msmarco-passage-distilbert-dot-margin_mse-T2-bf": {
        "description": "Faiss FlatIP index of the MS MARCO passage corpus encoded by the distilbert-dot-margin_mse-T2-msmarco passage encoder",
        "filename": "dindex-msmarco-passage-distilbert-dot-margin_mse-T2-20210316-d44c3a.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-msmarco-passage-distilbert-dot-margin_mse-T2-20210316-d44c3a.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/DSHYNJJRZLqckLA/download"
        ],
        "md5": "83a8081d6020910058164978b095615f",
        "size compressed (bytes)": 25162770962,
        "documents": 8841823,
        "downloaded": False,
        "texts": "msmarco-passage"
    },
    "msmarco-passage-distilbert-dot-tas_b-b256-bf": {
        "description": "Faiss FlatIP index of the MS MARCO passage corpus encoded by msmarco-passage-distilbert-dot-tas_b-b256 passage encoder",
        "filename": "dindex-msmarco-passage-distilbert-dot-tas_b-b256-bf-20210527-63276f.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-msmarco-passage-distilbert-dot-tas_b-b256-bf-20210527-63276f.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/89fr56FNeGFbyrG/download",
        ],
        "md5": "cc947bf66d9552a2a7c6fe060466e490",
        "size compressed (bytes)": 25162328596,
        "documents": 8841823,
        "downloaded": False,
        "texts": "msmarco-passage"
    },
    "msmarco-passage-tct_colbert-v2-bf": {
        "description": "Faiss FlatIP index of the MS MARCO passage corpus encoded by the tct_colbert-v2 passage encoder",
        "filename": "dindex-msmarco-passage-tct_colbert-v2-bf-20210608-5f341b.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-msmarco-passage-tct_colbert-v2-bf-20210608-5f341b.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/2EZ2feACyL8cnw5/download",
        ],
        "md5": "479591e265347ceff954ae05f6d3462b",
        "size compressed (bytes)": 25211079381,
        "documents": 8841823,
        "downloaded": False,
        "texts": "msmarco-passage"
    },
    "msmarco-passage-tct_colbert-v2-hn-bf": {
        "description": "Faiss FlatIP index of the MS MARCO passage corpus encoded by the tct_colbert-v2-hn passage encoder",
        "filename": "dindex-msmarco-passage-tct_colbert-v2-hn-bf-20210608-5f341b.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-msmarco-passage-tct_colbert-v2-hn-bf-20210608-5f341b.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/2dP6EJz7QgywM4b/download",
        ],
        "md5": "61d38e4935b3ca36c99e0cda2b27fba2",
        "size compressed (bytes)": 25205729786,
        "documents": 8841823,
        "downloaded": False,
        "texts": "msmarco-passage"
    },
    "msmarco-passage-tct_colbert-v2-hnp-bf": {
        "description": "Faiss FlatIP index of the MS MARCO passage corpus encoded by the tct_colbert-v2-hnp passage encoder",
        "filename": "dindex-msmarco-passage-tct_colbert-v2-hnp-bf-20210608-5f341b.tar.gz",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/dindex-msmarco-passage-tct_colbert-v2-hnp-bf-20210608-5f341b.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/od63ZXNadCZymwj/download",
        ],
        "md5": "c3c3fc3a288bcdf61708d4bba4bc79ff",
        "size compressed (bytes)": 25225528775,
        "documents": 8841823,
        "downloaded": False,
        "texts": "msmarco-passage"
    },
    "cast2019-tct_colbert-v2-hnsw": {
        "description": "Faiss HNSW index of the CAsT2019 passage corpus encoded by the tct_colbert-v2 passage encoder",
        "filename": "faiss-hnsw.cast2019.tct_colbert-v2.tar.gz",
        "readme": "faiss-hnsw.cast2019.tct_colbert-v2-readme.txt",
        "urls": [
            "https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/faiss-hnsw.cast2019.tct_colbert-v2.tar.gz",
            "https://vault.cs.uwaterloo.ca/s/ncrZdE67BCKxPwc/download"
        ],
        "md5": "fa7673509b34d978e1b931d5705369ee",
        "size compressed (bytes)": 112121366773,
        "documents": 38429835,
        "downloaded": False,
        "texts": "cast2019"
    },
    'mrtydi-v1.1-arabic-mdpr-nq': {
        'description': 'Faiss index for Mr.TyDi v1.1 (Arabic) '
            'corpus encoded by mDPR passage encoder '
            'pre-fine-tuned on NQ.',
        'filename': 'faiss.mrtydi-v1.1-arabic.20220207.5df364.tar.gz',
        'readme': 'faiss.mrtydi-v1.1-arabic.20220207.5df364.README.md',
        'urls': [
            'https://vault.cs.uwaterloo.ca/s/Jgj3rYjbyRrmJs8/download'
        ],
        'md5': 'de86c1ce43854bbeea4e3af5d95d6ffb',
        'size compressed (bytes)': 5997718937,
        'documents': 2106586,
        'downloaded': False,
        'texts': 'mrtydi-v1.1-arabic'
    },
    'mrtydi-v1.1-bengali-mdpr-nq': {
        'description': 'Faiss index for Mr.TyDi v1.1 '
            '(Bengali) corpus encoded by '
            'mDPR passage encoder '
            'pre-fine-tuned on NQ.',
        'filename': 'faiss.mrtydi-v1.1-bengali.20220207.5df364.tar.gz',
        'readme': 'faiss.mrtydi-v1.1-bengali.20220207.5df364.README.md',
        'urls': [
            "https://vault.cs.uwaterloo.ca/s/4PpkzXAQtXFFJHR/download"
        ],
        'md5': 'e60cb6f1f7139cf0551f0ba4e4e83bf6',
        'size compressed (bytes)': 865716848,
        'documents': 304059,
        'downloaded': False,
        "texts": "mrtydi-v1.1-bengali"
    },
    'mrtydi-v1.1-english-mdpr-nq': {
        'description': 'Faiss index for Mr.TyDi v1.1 '
            '(English) corpus encoded by '
            'mDPR passage encoder '
            'pre-fine-tuned on NQ.',
        'filename': 'faiss.mrtydi-v1.1-english.20220207.5df364.tar.gz',
        'readme': 'faiss.mrtydi-v1.1-english.20220207.5df364.README.md',
        'urls': [
            'https://vault.cs.uwaterloo.ca/s/A7pjbwYeoT4Krnj/download'
        ],
        'md5': 'a0a8cc39e8af782ec82188a18c4c97c3',
        'size compressed (bytes)': 93585951488,
        'documents': 32907100,
        'downloaded': False,
        'texts': 'mrtydi-v1.1-english'
    },
    'mrtydi-v1.1-finnish-mdpr-nq': {
        'description': 'Faiss index for Mr.TyDi v1.1 '
            '(Finnish) corpus encoded by '
            'mDPR passage encoder '
            'pre-fine-tuned on NQ.',
        'filename': 'faiss.mrtydi-v1.1-finnish.20220207.5df364.tar.gz',
        'readme': 'faiss.mrtydi-v1.1-finnish.20220207.5df364.README.md',
        'urls': ['https://vault.cs.uwaterloo.ca/s/erNYkrYzRZxpecz/download'],
        'md5': '3e4e18aacf07ca551b474315f267ead6',
        'size compressed (bytes)': 5435516778,
        'documents': 1908757,
        'downloaded': False,
        'texts': 'mrtydi-v1.1-finnish'
    },
    'mrtydi-v1.1-indonesian-mdpr-nq': {
        'description': 'Faiss index for Mr.TyDi '
            'v1.1 (Indonesian) corpus '
            'encoded by mDPR passage '
            'encoder pre-fine-tuned on '
            'NQ.',
        'filename': 'faiss.mrtydi-v1.1-indonesian.20220207.5df364.tar.gz',
        'readme': 'faiss.mrtydi-v1.1-indonesian.20220207.5df364.README.md',
        'urls': ['https://vault.cs.uwaterloo.ca/s/BpR3MzT7KJ6edx7/download'],
        'md5': '0bf693e4046d9a565ae18b9f5939d193',
        'size compressed (bytes)': 865716848,
        'documents': 4179177829,
        'downloaded': False,
        'texts': 'mrtydi-v1.1-indonesian'
    },
    'mrtydi-v1.1-japanese-mdpr-nq': {
        'description': 'Faiss index for Mr.TyDi v1.1 '
            '(Japanese) corpus encoded by '
            'mDPR passage encoder '
            'pre-fine-tuned on NQ.',
        'filename': 'faiss.mrtydi-v1.1-japanese.20220207.5df364.tar.gz',
        'readme': 'faiss.mrtydi-v1.1-japanese.20220207.5df364.README.md',
        'urls': [
            'https://vault.cs.uwaterloo.ca/s/k7bptHT8GwMJpnF/download'
        ],
        'md5': '4ba566e27bc0158108259b18a153e2fc',
        'size compressed (bytes)': 19920816424,
        'documents': 7000027,
        'downloaded': False,
        'texts': 'mrtydi-v1.1-japanese'
    },
    'mrtydi-v1.1-korean-mdpr-nq': {
        'description': 'Faiss index for Mr.TyDi v1.1 '
            '(Korean) corpus encoded by '
            'mDPR passage encoder '
            'pre-fine-tuned on NQ.',
        'filename': 'faiss.mrtydi-v1.1-korean.20220207.5df364.tar.gz',
        'readme': 'faiss.mrtydi-v1.1-korean.20220207.5df364.README.md',
        'urls': [
            'https://vault.cs.uwaterloo.ca/s/TigfYMde94YWAoE/download'
        ],
        'md5': '44212e5722632d5bcb14f0680741638c',
        'size compressed (bytes)': 4257414237,
        'documents': 1496126,
        'downloaded': False,
        'texts': 'mrtydi-v1.1-korean'
    },
    'mrtydi-v1.1-russian-mdpr-nq': {
        'description': 'Faiss index for Mr.TyDi v1.1 '
            '(Russian) corpus encoded by '
            'mDPR passage encoder '
            'pre-fine-tuned on NQ.',
        'filename': 'faiss.mrtydi-v1.1-russian.20220207.5df364.tar.gz',
        'readme': 'faiss.mrtydi-v1.1-russian.20220207.5df364.README.md',
        'urls': [
            'https://vault.cs.uwaterloo.ca/s/eN7demnmnspqxjk/download'
        ],
        'md5': 'e7634093f2a3362928e9699441ce8a3b',
        'size compressed (bytes)': 27317759143,
        'documents': 9597504,
        'downloaded': False,
        'texts': 'mrtydi-v1.1-russian'
    },
    'mrtydi-v1.1-swahili-mdpr-nq': {
        'description': 'Faiss index for Mr.TyDi v1.1 '
                '(Swahili) corpus encoded by '
                'mDPR passage encoder '
                'pre-fine-tuned on NQ.',
        'filename': 'faiss.mrtydi-v1.1-swahili.20220207.5df364.tar.gz',
        'readme': 'faiss.mrtydi-v1.1-swahili.20220207.5df364.README.md',
        'urls': [
            'https://vault.cs.uwaterloo.ca/s/JgiX8PRftnqcPwy/download'
        ],
        'md5': '5061bdd1d81bc32490bbb3682096acdd',
        'size compressed (bytes)': 389658394,
        'documents': 136689,
        'downloaded': False,
        'texts': 'mrtydi-v1.1-swahili'
    },
    'mrtydi-v1.1-telugu-mdpr-nq': {
        'description': 'Faiss index for Mr.TyDi v1.1 '
            '(Telugu) corpus encoded by '
            'mDPR passage encoder '
            'pre-fine-tuned on NQ.',
        'filename': 'faiss.mrtydi-v1.1-telugu.20220207.5df364.tar.gz',
        'readme': 'faiss.mrtydi-v1.1-telugu.20220207.5df364.README.md',
        'urls': [
            'https://vault.cs.uwaterloo.ca/s/dkm6RGdgRbnwiX2/download'
        ],
        'md5': '4952dacaeae89185d3757f9f26af4e88',
        'size compressed (bytes)': 1561173721,
        'documents': 548224,
        'downloaded': False,
        'texts': 'mrtydi-v1.1-telugu'
    },
    'mrtydi-v1.1-thai-mdpr-nq': {
        'description': 'Faiss index for Mr.TyDi v1.1 '
            '(Thai) corpus encoded by mDPR '
            'passage encoder pre-fine-tuned '
            'on NQ.',
        'filename': 'faiss.mrtydi-v1.1-thai.20220207.5df364.tar.gz',
        'readme': 'faiss.mrtydi-v1.1-thai.20220207.5df364.README.md',
        'urls': [
            'https://vault.cs.uwaterloo.ca/s/fFrRYefd3nWFR3J/download'
        ],
        'md5': '2458f704b277fa8ffe2509b6296892a0',
        'size compressed (bytes)': 1616059846,
        'documents': 568855,
        'downloaded': False,
        'texts': 'mrtydi-v1.1-thai'
    },
    'wikipedia-dpr-dkrr-nq': {
        'description': "Faiss FlatIP index of Wikipedia DPR encoded by the retriever model from: 'Distilling Knowledge from Reader to Retriever for Question Answering' trained on NQ",
        'filename': 'faiss-flat.wikipedia.dkrr-dpr-nq-retriever.20220217.25ed1f.cc91b2.tar.gz',
        'urls': [
            'https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/faiss-flat.wikipedia.dkrr-dpr-nq-retriever.20220217.25ed1f.cc91b2.tar.gz',
        ],
        'md5': 'e58886fd5485b84f2c44963ce644561b',
        'size compressed (bytes)': 37812137819,
        'documents': 21015324,
        'downloaded': False,
        'texts': 'wikipedia-dpr'
    },
    'wikipedia-dpr-dkrr-tqa': {
        'description': "Faiss FlatIP index of Wikipedia DPR encoded by the retriever model from: 'Distilling Knowledge from Reader to Retriever for Question Answering' trained on TriviaQA",
        'filename': 'faiss-flat.wikipedia.dkrr-dpr-tqa-retriever.20220217.25ed1f.cc91b2.tar.gz',
        'urls': [
            'https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/pyserini-indexes/faiss-flat.wikipedia.dkrr-dpr-tqa-retriever.20220217.25ed1f.cc91b2.tar.gz',
        ],
        'md5': 'a6b02d33c9c0376ad1bf6550212ecdcb',
        'size compressed (bytes)': 37802648060,
        'documents': 21015324,
        'downloaded': False,
        'texts': 'wikipedia-dpr'
    }
}
