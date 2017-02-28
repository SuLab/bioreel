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



def process_go(go_src, go_dest):
    # specifically process the go key
    

def process_simple_list_diffs(src_list, dest_list, key, diff_id):
    # return ops for list diffs
    _src = set(src_list); _dest = set(dest_list)
    _diffs = []
    for item in _src.difference(_dest):
        _diffs.append({'op': 'remove', 'path': key, 'item': item, 'diff': diff_id})
    for item in _dest.difference(_src):
        _diffs.append({'op': 'add', 'path': key, 'item': item, 'diff': diff_id})
    return _diffs

def dummy(*args, **kwargs):
    return []

def mygene_diff(src, dest, diff_id):
    if src == dest:
        return []

    osrc = copy.deepcopy(src)
    odest = copy.deepcopy(dest)

    diffs = []
    src_keys = set(src.keys()); dest_keys = set(dest.keys())

    # do the top level keys in both:
    for key in src_keys.intersection(dest_keys):
        src_val = src[key]; dest_val = dest[key]
        # These keys are always dictionaries in root level, and often represent separate entities, 
        # handle them individually
        if key == 'go':
            diff_fn = process_go_diffs
            _src = src_val
            _dest = dest_val
        elif key == 'homologene':
            for subkey in ['genes', 'id']:
                src_subval = src_val.get(subkey, [])
                dest_subval = dest_val(subkey, [])
                if not isinstance(src_subval, list):
                    src_subval = [src_subval]
                if not isinstance(dest_subval, list):
                    dest_subval = [dest_subval]
                diffs.extend(process_simple_list_diffs(src_subval, dest_subval, key=key+'.'+subkey, diff_id=diff_id))
            continue
        elif key == 'pathway':
            for subkey in ['reactome']:
                src_subval = src_val.get(subkey, [])
                dest_subval = dest_val(subkey, [])
                if not isinstance(src_subval, list):
                    src_subval = [src_subval]
                if not isinstance(dest_subval, list):
                    dest_subval = [dest_subval]
                diffs.extend(process_simple_list_diffs(src_subval, dest_subval, key=key+'.'+subkey, diff_id=diff_id))
            continue 
        elif key == 'wikipedia':
            for subkey in ['url_stub']:
                src_subval = src_val.get(subkey, [])
                dest_subval = dest_val(subkey, [])
                if not isinstance(src_subval, list):
                    src_subval = [src_subval]
                if not isinstance(dest_subval, list):
                    dest_subval = [dest_subval]
                diffs.extend(process_simple_list_diffs(src_subval, dest_subval, key=key+'.'+subkey, diff_id=diff_id))
            continue 
        elif key == 'uniprot':
            for subkey in ['TrEMBL', 'Swiss-Prot']:
                src_subval = src_val.get(subkey, [])
                dest_subval = dest_val(subkey, [])
                if not isinstance(src_subval, list):
                    src_subval = [src_subval]
                if not isinstance(dest_subval, list):
                    dest_subval = [dest_subval]
                diffs.extend(process_simple_list_diffs(src_subval, dest_subval, key=key+'.'+subkey, diff_id=diff_id))
            continue 
        elif key == 'refseq':
            for subkey in ['genomic', 'protein', 'rna', 'translation']:
                src_subval = src_val.get(subkey, [])
                dest_subval = dest_val.get(subkey, [])
                if not isinstance(src_subval, list):
                    src_subval = [src_subval]
                if not isinstance(dest_subval, list):
                    dest_subval = [dest_subval]
                diffs.extend(process_simple_list_diffs(src_subval, dest_subval, key=key+'.'+subkey, diff_id=diff_id))
            continue
                
        elif key == 'accession':
            for subkey in ['genomic', 'protein', 'rna', 'translation']:
                src_subval = src_val.get(subkey, [])
                dest_subval = dest_val.get(subkey, [])
                if not isinstance(src_subval, list):
                    src_subval = [src_subval]
                if not isinstance(dest_subval, list):
                    dest_subval = [dest_subval]
                diffs.extend(process_simple_list_diffs(src_subval, dest_subval, key=key+'.'+subkey, diff_id=diff_id))
            continue
        elif key == 'exac':
            #
        elif key == 'reporter':
            # value tests
        elif key == 'reagent':
        
        # These keys are always lists of dictionaries
        elif key == 'exons_mm9':

        elif key == 'exons_hg19':

        elif key == 'exons':

        elif key == 'generif':

        # These keys are dictionaries (for one value) and lists of dictionaries for multiple values
DICT_OR_LIST_KEYS = ['genomic_pos', 'genomic_pos_mm9', 'ensembl', 'genomic_pos_hg19', 'interpro']
        
        if ((isinstance(src_val, str) and isinstance(dest_val, str)) or 
            (isinstance(src_val, int) and isinstance(dest_val, int)) or
            (isinstance(src_val, str) and isinstance(dest_val, list) and len(dest_val) > 0 and isinstance(dest_val[0], str)) or
            (isinstance(src_val, int) and isinstance(dest_val, list) and len(dest_val) > 0 and isinstance(dest_val[0], int)) or
            (isinstance(src_val, list) and len(src_val) > 0 and isinstance(src_val[0], int) and isinstance(dest_val, int)) or
            (isinstance(src_val, list) and len(src_val) > 0 and isinstance(src_val[0], str) and isinstance(dest_val, str)) or
            (isinstance(src_val, list) and len(src_val) > 0 and isinstance(src_val[0], int) and isinstance(dest_val, list) and len(dest_val) > 0 and isinstance(dest_val[0], int))
            (isinstance(src_val, list) and len(src_val) > 0 and isinstance(src_val[0], str) and isinstance(dest_val, list) and len(dest_val) > 0 and isinstance(dest_val[0], str))):
            diff_fn = process_simple_list_diffs
            if not isinstance(src_val, list):
                _src = [src_val]
            if not isinstance(dest_val, list):
                _dest = [dest_val]
        elif ((isinstance(src_val, dict) and isinstance(dest_val, dict)) or
            (isinstance(src_val, dict) and isinstance(dest_val, list) and len(dest_val) > 0 and isinstance(dest_val[0], dict)) or
            (isinstance(src_val, list) and len(src_val) > 0 and isinstance(src_val[0], dict) and isinstance(dest_val, dict)) or
            (isinstance(src_val, list) and len(src_val) > 0 and isinstance(src_val[0], dict) and isinstance(dest_val, list) and len(dest_val) > 0 and isinstance(dest_val[0], dict)):
            else:
                if 
                diff_fn = process_entity_list_diffs
        else:
            # should never happen....log to file
            diff_fn = dummy
            _src = []
            _dest = []

        if diff_fn and _src and _dest:
            key_diffs = diff_fn(_src, _dest, key=key, diff_id=diff_id)

        diffs.extend(key_diffs)

    # do top level keys in src but not in dest (full key delete)
    for key in src_keys.difference(dest_keys):
        diffs.extend([{'op': 'delete', 'path': key, 'item': src[key], 'diff': diff_id}])

    for key in dest_keys.difference(src_keys):
        diffs.extend([{'op': 'add', 'path': key, 'item': dest[key], 'diff': diff_id}])

    return diffs
