#!/usr/bin/env python3
"""
Qt GUI to access the SLDDB.
"""

import sys
from datetime import datetime
from PyQt5 import QtCore, QtWidgets, uic
from slddb import SLDDB
from slddb.dbconfig import DB_FILE, DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA

class SLDDBWindow(QtWidgets.QMainWindow):
    selected_material=None

    def __init__(self):
        super(SLDDBWindow, self).__init__() # Call the inherited classes __init__ method
        self.ui=uic.loadUi('qt_interface/slddb_window.ui', self) # Load the .ui file
        self.setColumns()
        self.show() # Show the GUI
        self.db=SLDDB(DB_FILE)

    def setColumns(self):
        tbl=self.ui.resultTable
        tbl.setColumnCount(len(DB_MATERIALS_FIELDS)-len(DB_MATERIALS_HIDDEN_DATA))
        self.headers=[]
        for field in DB_MATERIALS_FIELDS:
            if field in DB_MATERIALS_HIDDEN_DATA:
                continue
            self.headers.append(field)
        tbl.setHorizontalHeaderLabels(self.headers)
        for i in range(len(self.headers)):
            tbl.setColumnHidden(i, True)

        tbl=self.ui.entryTable
        tbl.setRowCount(len(self.headers))
        tbl.setVerticalHeaderLabels(self.headers)

    def searchDatabase(self):
        name=self.ui.nameEdit.text()
        description=self.ui.descriptionEdit.text()
        formula=self.ui.formulaEdit.text()
        search={'name': name, 'description': description, 'formula': formula}
        for key, value in list(search.items()):
            if value.strip()=='':
                del(search[key])

        results=self.db.search_material(**search)
        hidden_columns=[True for field in self.headers]
        for row in results:
            for i, field in enumerate(self.headers):
                if row[field] is not None:
                    hidden_columns[i]=False
        tbl=self.ui.resultTable
        tbl.sortByColumn(-1, QtCore.Qt.AscendingOrder)
        tbl.setRowCount(len(results))
        for i, hidden in enumerate(hidden_columns):
            tbl.setColumnHidden(i, hidden)
        for i,result in enumerate(results):
            for j, field in enumerate(self.headers):
                item=result[field]
                if type(item) is datetime:
                    item=str(item)
                titem=QtWidgets.QTableWidgetItem()
                titem.setData(QtCore.Qt.DisplayRole, item)
                tbl.setItem(i, j, titem)
        tbl.resizeColumnsToContents()
        self.results=results

        if len(results)==1:
            tbl.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(0, -1, 1, -1), True)
            self.selectItem(0, 0)

    def selectItem(self, row, col):
        tbl=self.ui.resultTable
        ID=tbl.indexFromItem(tbl.item(row, 0)).data()
        orig_row=[res['ID'] for res in self.results].index(ID)
        result=self.results[orig_row]
        try:
            material=self.db.select_material(result)
        except Exception as e:
            return
        self.selected_material=material
        self.ui.resultName.setText(result['name'])
        self.updateResult()

    def updateResult(self):
        material=self.selected_material
        if material is None:
            return

        if self.ui.densityVolumeSelect.currentIndex()==0:
            self.ui.densityVolume.setText('%.4f'%material.dens)
        else:
            self.ui.densityVolume.setText('%.4g'%(1000./material.fu_dens))
        self.ui.neutronSLD.setText("%.6f"%(1e6*material.rho_n.real))
        self.ui.neutronSLDimag.setText("%.6f"%(1e6*material.rho_n.imag))

        try:
            rhox=material.delta_of_E(float(self.ui.xrayEnergyEdit.currentText()))
        except ValueError:
            self.ui.xraySLD.setText("")
            self.ui.xraySLDimag.setText("")
        else:
            self.ui.xraySLD.setText("%.6f"%(1e6*rhox.real))
            self.ui.xraySLDimag.setText("%.6f"%(1e6*rhox.imag))


if __name__=='__main__':
    app=QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
    window=SLDDBWindow()  # Create an instance of our class
    app.exec_()  # Start the application
