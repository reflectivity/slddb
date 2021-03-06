"""
Functions to create database compatible entries from other file formats.
"""
import pathlib
import os
from .material import Formula
from .dbconfig import db_lookup

class Importer(dict):
    """
    Base class for importing database entries. Includes checkes for correctness used by all importers.
    """
    formula=None

    def __init__(self, filename):
        self.filename=filename
        self.name=os.path.basename(filename).rsplit('.', 1)[0]
        data=self.build_data()
        self.validate(name=self.name, formula=self.formula, **data)
        dict.__init__(self, data)

    @staticmethod
    def validate(**full_entry):
        # check for all values of the data dictionary if the format is valid
        for key, value in full_entry.items():
            if not db_lookup[key][1].validate(value):
                raise ValueError(f"Can not import dataset, failed to validate value '{value}' for key '{key}'")

    def build_data(self):
        raise NotImplementedError("Importer has to be subclassed with _build_data implemented.")

    def __repr__(self):
        return f'MaterialData(name="{self.name}", formula={repr(self.formula)} , data={dict.__repr__(self)})'


class CifImporter(Importer):
    suffix='cif'

    @staticmethod
    def float_werr(value):
        # Convert CIF entry that might have an uncertainty to float
        return float(value.split('(')[0])

    def build_data(self):
        try:
            import CifFile
        except ImportError:
            raise RuntimeError("You have to install PyCifRW python package to be able to import cif files")

        output={'data_origin': 'diffraction', 'comments': 'imported from CIF file',
                'physical_state': 'solid'}

        cf=CifFile.ReadCif(pathlib.Path(self.filename).as_uri())
        block=cf.first_block()

        formula=Formula(block['_chemical_formula_sum'])

        if '_exptl_crystal_density_diffrn' in block:
            output['density']=self.float_werr(block['_exptl_crystal_density_diffrn'])
        elif '_cell_volume' in block and '_cell_formula_units_Z' in block:
            output['FU_volume']=self.float_werr(block['_cell_volume'])/self.float_werr(block['_cell_formula_units_Z']) # Å³
        else:
            raise ValueError("No data to deduce material density")

        if '_chemical_name_mineral' in block:
            self.name=block['_chemical_name_mineral']

        if all([ii in block for ii in ['_journal_name_full', '_journal_volume', '_journal_year',
                                       '_publ_author_name', ]]):
            authors=', '.join(block['_publ_author_name'])
            journal=block["_journal_name_full"]
            volume=block["_journal_volume"]
            year=block["_journal_year"]
            if '_journal_page_first' in block:
                page=block['_journal_page_first']
            else:
                page='-'
            output['reference']=f'{authors}; {journal}, {volume}, p. {page} ({year})'.replace('\n', ' ')

        if '_journal_paper_doi' in block:
            output['doi']='https://doi.org/'+block['_journal_paper_doi']

        self.formula=formula
        return output

importers=[CifImporter]