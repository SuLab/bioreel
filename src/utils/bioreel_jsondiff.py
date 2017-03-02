"""

    Some code to do a type of diff on mygene object.

    Below is the result of a key analysis on all mygene documents circa late 2016-early 2017.

    STRING_ONLY_KEYS = ['APHIDBASE', 'map_location', 'summary', 'MIM', 'type_of_gene', 'miRBase', 'SGD', 'Araport',
        'VGNC', 'EcoGene', 'RGD', 'dictyBase', 'VectorBase', 'Xenbase', 'Pathema', 'symbol', 'NASONIABASE',
        'locus_tag', 'MGI', 'ZFIN', 'TAIR', 'CGNC', 'PseudoCap', 'BGD', 'BEETLEBASE', 'ApiDB_CryptoDB', 'HGNC',
        'Vega', 'BEEBASE', 'FLYBASE', 'name', 'WormBase', 'AnimalQTLdb']

    DICT_ONLY_KEYS = ['homologene', 'pathway', 'wikipedia', 'uniprot', 'refseq', 'go', 'accession', 'exac', 
        'reporter', 'reagent']

    LIST_ONLY_KEYS = ['exons_mm9', 'generif', 'exons_hg19', 'exons']

    INT_ONLY_KEYS = ['entrezgene', 'taxid']

    STRING_OR_LIST_KEYS = ['pfam', 'pir', 'ipi', 'prosite', 'ec', 'unigene', 'pharmgkb', 'alias', 'pdb', 'other_names']

    INT_OR_LIST_KEYS = ['retired']

    DICT_OR_LIST_KEYS = ['genomic_pos', 'genomic_pos_mm9', 'ensembl', 'genomic_pos_hg19', 'interpro']

    MYGENE_ROOT_KEYS = ['APHIDBASE', 'AnimalQTLdb', 'ApiDB_CryptoDB', 'Araport', 'BEEBASE', 'BEETLEBASE',
     'BGD', 'CGNC', 'EcoGene', 'FLYBASE', 'HGNC', 'MGI', 'MIM', 'NASONIABASE', 'Pathema', 'PseudoCap',
     'RGD', 'SGD', 'TAIR', 'VGNC', 'VectorBase', 'Vega', 'WormBase', 'Xenbase', 'ZFIN', 'accession',
     'alias', 'dictyBase', 'ec', 'ensembl', 'entrezgene', 'exac', 'exons', 'exons_hg19', 'exons_mm9',
     'generif', 'genomic_pos', 'genomic_pos_hg19', 'genomic_pos_mm9', 'go', 'homologene', 'interpro',
     'ipi', 'locus_tag', 'map_location', 'miRBase', 'name', 'other_names', 'pathway', 'pdb', 'pfam',
     'pharmgkb', 'pir', 'prosite', 'reagent', 'refseq', 'reporter', 'retired', 'summary', 'symbol',
     'taxid', 'type_of_gene', 'unigene', 'uniprot', 'wikipedia']

"""
import json
import copy

# These are root keys where the value is an entity or list of entities that can be directly diffed
SIMPLE_ENTITIES = ['APHIDBASE', 'AnimalQTLdb', 'ApiDB_CryptoDB', 'Araport', 
                'BEEBASE', 'BEETLEBASE', 'BGD', 'CGNC', 'EcoGene', 'FLYBASE', 'HGNC', 'MGI', 'MIM', 
                'NASONIABASE', 'Pathema', 'PseudoCap', 'RGD', 'SGD', 'TAIR', 'VGNC', 'VectorBase', 'Vega', 
                'WormBase', 'Xenbase', 'ZFIN', 'alias', 'dictyBase', 'ec', 'entrezgene', 'generif', 'interpro',
                'locus_tag', 'map_location', 'miRBase', 'name', 'other_names', 'pfam', 'pharmgkb', 'prosite',
                'retired', 'summary', 'symbol', 'taxid', 'type_of_gene', 'unigene', 'genomic_pos', 
                'genomic_pos_hg19', 'genomic_pos_mm9', 'pir', 'pdb', 'ipi', 'exons', 'exons_hg19', 'exons_mm9']

# These are root keys where the diffed entity is nested inside a dict.  The value list is the subkey that contains
# a diff-able entity or entity list
NESTED_ENTITIES = {'go': ['BP', 'MF', 'CC'], 'accession': ['genomic', 'protein', 'rna', 'translation'], 
                'ensembl': ['gene', 'protein', 'transcript', 'translation'], 
                'homologene': ['genes', 'id'], 'refseq': ['genomic', 'protein', 'rna', 'translation'],
                'uniprot': ['TrEMBL', 'Swiss-Prot'], 'pathway': ['biocarta', 'humancyc', 'kegg', 
                'mousecyc', 'netpath', 'pharmgkb', 'pid', 'reactome', 'smpdb', 'wikipathways', 'yeastcyc'],
                'wikipedia': ['url_stub']}

# These are root keys where the keys contain values, and need special processing
DICT_ITEM_ENTITIES = ['reporter', 'reagent']

# These are root keys with no lists and potentially many nested levels...
ALL_ITEM_ENTITIES = ['exac']

def process_simple_list_diffs(src, dest, key, diff_id):
    # return ops for list diffs
    if not isinstance(src, list):
        src = [src]
    if not isinstance(dest, list):
        dest = [dest]
    _diffs = []
    if len(src) and isinstance(src[0], dict):
        src = [json.dumps(d, sort_keys=True) for d in src]
        dest = [json.dumps(d, sort_keys=True) for d in dest]
        _src = set(src); _dest = set(dest)
        for item in _src.difference(_dest):
            _diffs.append({'op': 'remove', 'path': key, 'item': json.loads(item), 'diff': diff_id})
        for item in _dest.difference(_src):
            _diffs.append({'op': 'add', 'path': key, 'item': json.loads(item), 'diff': diff_id})
    elif len(src) and isinstance(src[0], list):
        src = [tuple(d) for d in src]
        dest = [tuple(d) for d in dest]
        _src = set(src); _dest = set(dest)
        for item in _src.difference(_dest):
            _diffs.append({'op': 'remove', 'path': key, 'item': list(item), 'diff': diff_id})
        for item in _dest.difference(_src):
            _diffs.append({'op': 'add', 'path': key, 'item': list(item), 'diff': diff_id})
    else:
        _src = set(src); _dest = set(dest)
        _diffs = []
        for item in _src.difference(_dest):
            _diffs.append({'op': 'remove', 'path': key, 'item': item, 'diff': diff_id})
        for item in _dest.difference(_src):
            _diffs.append({'op': 'add', 'path': key, 'item': item, 'diff': diff_id})
    return _diffs

def process_all_item_entity_diffs(src, dest, key, diff_id):
    # 
    _diffs = []
    if src == dest:
        return _diffs
    
    def _get_dest(dot):
        fields = dot.split('.')[1:]
        _ret = copy.deepcopy(dest)
        for field in fields:
            _ret = []
            if field != 'pRec' or field != 'p_rec':
                _ret = _ret[field]
        return _ret

    def _traverse(d, _path):
        if isinstance(d, dict):
            for (k,v) in d.items():
                _traverse(v, _path + '.' + k)
        else:
            _diffs.extend(process_simple_list_diffs(d, _get_dest(_path), _path, diff_id))

    _traverse(src, key)
    return _diffs

def mygene_diff(src, dest, diff_id):
    if src == dest:
        return []

    diffs = []
    src_keys = set(src.keys()); dest_keys = set(dest.keys())

    # do the top level keys in both:
    for key in src_keys.intersection(dest_keys):
        print("***************\nStarting root key: {}".format(key))
        src_val = src[key]; dest_val = dest[key]
        # Do simple entities
        if key in SIMPLE_ENTITIES:
            diffs.extend(process_simple_list_diffs(src_val, dest_val, key, diff_id))
        elif key in NESTED_ENTITIES:
            for subkey in NESTED_ENTITIES[key]:
                sk_src_val = src_val.get(subkey, []); sk_dest_val = dest_val.get(subkey, [])
                diffs.extend(process_simple_list_diffs(sk_src_val, sk_dest_val, key + '.' + subkey, diff_id))
        elif key in DICT_ITEM_ENTITIES:
            src_subkeys = set(list(src_val.keys())); dest_subkeys = set(list(dest_val.keys()))
            for subkey in src_subkeys.intersection(dest_subkeys):
                sk_src_val = src_val.get(subkey); sk_dest_val = dest_val.get(subkey)
                diffs.extend(process_simple_list_diffs(sk_src_val, sk_dest_val, key + '.' + subkey, diff_id))

            # in src but not in dest (delete)
            for subkey in src_subkeys.difference(dest_subkeys):
                diffs.append({'op': 'delete', 'path': key + '.' + subkey, 'item': src_val[subkey], 'diff': diff_id})

            # in dest but not in src (add)
            for subkey in dest_subkeys.difference(src_subkeys):
                diffs.append({'op': 'add', 'path': key + '.' + subkey, 'item': dest_val[subkey], 'diff': diff_id})
        #elif key in ALL_ITEM_ENTITIES:
        #    diffs.extend(process_all_item_entity_diffs(src_val, dest_val, key, diff_id))

    # do top level keys in src but not in dest (full key delete)
    for key in src_keys.difference(dest_keys):
        diffs.extend([{'op': 'delete', 'path': key, 'item': src[key], 'diff': diff_id}])

    for key in dest_keys.difference(src_keys):
        diffs.extend([{'op': 'add', 'path': key, 'item': dest[key], 'diff': diff_id}])

    return diffs
