import os
import tempfile
from flask import redirect, url_for
from werkzeug.utils import secure_filename

from slddb.importers import CifImporter, PolymerSequence
from slddb.blender import collect_blend

CALC_DEFAULT_FIELDS = dict(densinput='volume', mu=0.0, magninput='muB')


def calculate_blend(mtype, name, idstr):
    result = collect_blend(mtype, idstr)
    return redirect(url_for('calculate_sld', _anchor='results_header',
                            formula=str(result.formula), density=result.fu_volume,
                            name=name or mtype, description=result.extra_data.get('description', None),
                            **CALC_DEFAULT_FIELDS))


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
        try:
            data=CifImporter(full_path, validate=False, sequence=sequence)
        except IndexError:
            return None, None
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
