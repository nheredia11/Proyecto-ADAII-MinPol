import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
                           QFileDialog, QMessageBox, QGridLayout)
from PyQt6.QtCore import Qt
import subprocess
import os

class MinPolGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MinPol Solver')
        self.setGeometry(100, 100, 800, 600)
        
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Parámetros básicos
        params_layout = QGridLayout()
        
        params_layout.addWidget(QLabel('Número de personas (n):'), 0, 0)
        self.n_input = QLineEdit()
        params_layout.addWidget(self.n_input, 0, 1)
        
        params_layout.addWidget(QLabel('Número de opiniones (m):'), 1, 0)
        self.m_input = QLineEdit()
        params_layout.addWidget(self.m_input, 1, 1)
        
        params_layout.addWidget(QLabel('Costo total máximo (ct):'), 2, 0)
        self.ct_input = QLineEdit()
        params_layout.addWidget(self.ct_input, 2, 1)
        
        params_layout.addWidget(QLabel('Máximo movimientos (maxM):'), 3, 0)
        self.maxM_input = QLineEdit()
        params_layout.addWidget(self.maxM_input, 3, 1)
        
        layout.addLayout(params_layout)
        
        # Matrices y vectores
        matrices_layout = QHBoxLayout()
        
        # Distribución inicial
        dist_layout = QVBoxLayout()
        dist_layout.addWidget(QLabel('Distribución inicial (p):'))
        self.p_input = QTextEdit()
        dist_layout.addWidget(self.p_input)
        matrices_layout.addLayout(dist_layout)
        
        # Valores de opiniones
        values_layout = QVBoxLayout()
        values_layout.addWidget(QLabel('Valores de opiniones (v):'))
        self.v_input = QTextEdit()
        values_layout.addWidget(self.v_input)
        matrices_layout.addLayout(values_layout)
        
        # Costos extra
        ce_layout = QVBoxLayout()
        ce_layout.addWidget(QLabel('Costos extra (ce):'))
        self.ce_input = QTextEdit()
        ce_layout.addWidget(self.ce_input)
        matrices_layout.addLayout(ce_layout)
        
        layout.addLayout(matrices_layout)
        
        # Matriz de costos
        layout.addWidget(QLabel('Matriz de costos (c):'))
        self.c_input = QTextEdit()
        layout.addWidget(self.c_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        load_button = QPushButton('Cargar .mpl')
        load_button.clicked.connect(self.load_mpl)
        buttons_layout.addWidget(load_button)
        
        solve_button = QPushButton('Resolver')
        solve_button.clicked.connect(self.solve)
        buttons_layout.addWidget(solve_button)
        
        layout.addLayout(buttons_layout)
        
        # Resultados
        layout.addWidget(QLabel('Resultados:'))
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)
        
        main_widget.setLayout(layout)
    
    def load_mpl(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Abrir archivo .mpl', '', 'MPL Files (*.mpl)')
        if filename:
            try:
                with open(filename, 'r') as f:
                    lines = f.readlines()
                    self.n_input.setText(lines[0].strip())
                    self.m_input.setText(lines[1].strip())
                    self.p_input.setText(lines[2].strip())
                    self.v_input.setText(lines[3].strip())
                    self.ce_input.setText(lines[4].strip())
                    
                    matrix_lines = lines[5:5+int(lines[1].strip())]
                    self.c_input.setText(''.join(matrix_lines))
                    
                    self.ct_input.setText(lines[-2].strip())
                    self.maxM_input.setText(lines[-1].strip())
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al cargar archivo: {str(e)}')
    
    def create_dzn_file(self):
        with open('DatosProyecto.dzn', 'w') as f:
            f.write(f'n = {self.n_input.text()};\n')
            f.write(f'm = {self.m_input.text()};\n')
            f.write(f'p = [{self.p_input.toPlainText()}];\n')
            f.write(f'v = [{self.v_input.toPlainText()}];\n')
            f.write(f'ce = [{self.ce_input.toPlainText()}];\n')
            
            # Formatear matriz de costos
            matrix_text = self.c_input.toPlainText().strip()
            matrix_rows = matrix_text.split('\n')
            formatted_matrix = '[|' + '|'.join(matrix_rows) + '|]'
            f.write(f'c = {formatted_matrix};\n')
            
            f.write(f'ct = {self.ct_input.text()};\n')
            f.write(f'maxM = {self.maxM_input.text()};\n')
    
    def solve(self):
        try:
            self.create_dzn_file()
            result = subprocess.run(['minizinc', 'Proyecto.mzn', 'DatosProyecto.dzn'], 
                                 capture_output=True, text=True)
            self.results_text.setText(result.stdout)
            if result.stderr:
                QMessageBox.warning(self, 'Advertencia', result.stderr)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al resolver: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MinPolGUI()
    window.show()
    sys.exit(app.exec())
