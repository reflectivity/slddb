import os
import tempfile
from flask import redirect, url_for
from werkzeug.utils import secure_filename

from slddb import DB_FILE, SLDDB
from slddb.material import Material
from slddb.element_table import get_element
from slddb.importers import CifImporter, PolymerSequence
from slddb.comparators import ExactString

CALC_DEFAULT_FIELDS = dict(densinput='volume',mu=0.0,magninput='muB')

AMINO_ABRV={
    "A": "Alanine",
    "R": "Arginine",
    "N": "Asparagine",
    "D": "Aspartate",
    "B": "Aspartate",
    "C": "Cysteine",
    "E": "Glutamate",
    "Q": "Glutamine",
    "Z": "Glutamate",
    "G": "Glycine",
    "H": "Histidine",
    "I": "Isoleucine",
    "L": "Leucine",
    "K": "Lysine",
    "M": "Methionine",
    "F": "Phenylalanine",
    "P": "Proline",
    "S": "Serine",
    "T": "Threonine",
    "W": "Tryptophan",
    "Y": "Tyrosine",
    "V": "Valine",
    }

RNA_ABRV={
    "A": "RNA-Adenine",
    "G": "RNA-Guanine",
    "C": "RNA-Cytosine",
    "U": "RNA-Uracil",
    }
DNA_ABRV={
    "A": "DNA-Adenine",
    "G": "DNA-Guanine",
    "C": "DNA-Cytosine",
    "T": "DNA-Thymine",
    }

class SequenceParseError(ValueError):
    pass

def collect_combination(ids, name_dict):
    db = SLDDB(DB_FILE)
    elements=[]
    loaded_ids={}
    for id in ids:
        if not id in loaded_ids:
            try:
                entry=db.search_material(name=ExactString(name_dict[id]))[0]
            except KeyError:
                possible_ids=name_dict.keys()
                raise SequenceParseError(f"Not a valid identifier {id}, options are {''.join(possible_ids)}")
            except IndexError:
                raise SequenceParseError(f"Molecule {name_dict[id]} not found in database")
            m=db.select_material(entry)
            loaded_ids[id]=m
        elements.append(loaded_ids[id])
    result=elements[0]
    for element in elements[1:]:
        # combine molecule matierials
        result+=element
    return result

def clean_str(string):
    return string.replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '').strip()

def calculate_blend(mtype, name, idstr):
    result=collect_blend(mtype, idstr)
    return redirect(url_for('calculate_sld', formula=str(result.formula), density=result.fu_volume,
                            name=name or mtype, description=result.extra_data.get('description', None),
                            **CALC_DEFAULT_FIELDS))

def collect_blend(mtype, idstr):
    if mtype=='protein':
        return collect_protein(idstr)
    elif mtype=='dna':
        return collect_dna(idstr)
    elif mtype=='rna':
        return collect_rna(idstr)
    elif mtype=='db':
        return collect_blendIDs(idstr)

hx2o=Material([(get_element(element), amount) for element, amount in [('Hx', 2.0), ('O', 1.0)]], dens=1.0)
def collect_protein(acids):
    acids=clean_str(acids).upper()
    result=collect_combination(acids, AMINO_ABRV)+hx2o
    result.extra_data['description']=f'protein, {len(acids)} resiudes'
    return result

def collect_dna(bases):
    bases=clean_str(bases).upper()
    result=collect_combination(bases, DNA_ABRV)+hx2o
    result.extra_data['description']=f'DNA, {len(bases)} resiudes'
    return result

def collect_rna(bases):
    bases=clean_str(bases).upper()
    result=collect_combination(bases, RNA_ABRV)+hx2o
    result.extra_data['description']=f'RNA, {len(bases)} resiudes'
    return result

def collect_blendIDs(formula):
    db = SLDDB(DB_FILE)
    elements=[]
    loaded_ids={}
    items=[]
    while '(' in clean_str(formula):
        pre, formula=formula.split(')',1)
        number=float(pre.split('*',1)[0].strip('(').strip())
        ID=int(pre.split('*',1)[1].strip())
        items.append((number, ID))
    for number, ID in items:
        if not ID in loaded_ids:
            entry=db.search_material(ID=ID)[0]
            m=db.select_material(entry)
            loaded_ids[ID]=m
        elements.append(number*loaded_ids[ID])
    result=elements[0]
    for element in elements[1:]:
        # combine molecule matierials
        result+=element
    return result

def formula_from_pdb(file_obj, sequence=1):
    filename=secure_filename(file_obj.filename)
    full_path=os.path.join(tempfile.gettempdir(), filename)
    file_obj.save(full_path)
    if filename.endswith('.gz'):
        import gzip
        txt=gzip.open(full_path, 'rb').read()
        os.remove(full_path)
        full_path=os.path.join(tempfile.gettempdir(), filename[:-3])
        open(full_path, 'wb').write(txt)
    if full_path.endswith('.cif'):
        data=CifImporter(full_path, validate=False, sequence=sequence)
        os.remove(full_path)
        if type(data.formula) is PolymerSequence:
            return data.name, data.formula
        else:
            return None, None
    else:
        txt=open(full_path, 'r').read()
        blocks=[]
        block_start=txt.find('>')
        while block_start!=-1:
            block_end=txt.find('>', block_start+1)
            blocks.append((block_start, block_end))
            block_start=block_end
        if sequence>len(blocks):
            return None,None
        block=txt[blocks[sequence-1][0]:blocks[sequence-1][1]].splitlines()
        head='';data=''
        for line in block:
            if line.startswith('>'):
                head+=line[1:]
            else:
                data+=line+'\n'
            head_items=head.split('|')
        return head_items[0], data.strip()
