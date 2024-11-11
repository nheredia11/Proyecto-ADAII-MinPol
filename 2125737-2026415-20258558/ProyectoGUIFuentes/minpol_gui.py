import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
                             QFileDialog, QMessageBox, QHBoxLayout, QGroupBox)
from PyQt6.QtCore import Qt
import subprocess
import os

# Clase principal que hereda de QMainWindow para crear la ventana de la aplicación.
class MinPolGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuración inicial de la ventana.
        self.setWindowTitle('MinPol Solver')  # Título de la ventana.
        self.setGeometry(100, 100, 800, 600)  # Tamaño de la ventana.
        
        # Inicializar la ruta del archivo MZN como None (aún no seleccionado).
        self.mzn_path = None
        
        # Widget principal que contiene todos los demás widgets.
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout principal que organiza los widgets de manera vertical.
        layout = QVBoxLayout()
        
        # Título principal de la interfaz de usuario.
        title_label = QLabel('<h1 style="color: #4CAF50;">MinPol Solver - Resolución de Problemas de Programación Entera</h1>')
        layout.addWidget(title_label)
        
        # Sección para seleccionar el archivo .mzn
        mzn_layout = QHBoxLayout()
        self.mzn_path_label = QLabel('Archivo Proyecto.mzn no seleccionado')  # Etiqueta para mostrar el archivo seleccionado.
        mzn_layout.addWidget(self.mzn_path_label)
        
        # Botón para seleccionar el archivo .mzn.
        select_mzn_button = QPushButton('Seleccionar Proyecto.mzn')
        select_mzn_button.clicked.connect(self.select_mzn_file)  # Conectar el botón con la función de selección de archivo.
        mzn_layout.addWidget(select_mzn_button)
        
        # Añadir la sección de selección de archivo al layout.
        layout.addLayout(mzn_layout)
        
        # Layout para los parámetros básicos del problema (n, m, ct, maxM).
        params_layout = QFormLayout()
        
        # Campos para ingresar los parámetros del problema.
        self.n_input = QLineEdit()
        params_layout.addRow('Número de personas (n):', self.n_input)
        
        self.m_input = QLineEdit()
        params_layout.addRow('Número de opiniones (m):', self.m_input)
        
        self.ct_input = QLineEdit()
        params_layout.addRow('Costo total máximo (ct):', self.ct_input)
        
        self.maxM_input = QLineEdit()
        params_layout.addRow('Máximo movimientos (maxM):', self.maxM_input)
        
        # Crear un contenedor para los parámetros del problema.
        params_group = QGroupBox("Parámetros del problema")
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Layout para las matrices y vectores.
        matrices_layout = QVBoxLayout()
        
        # Sección para la distribución inicial.
        dist_layout = QVBoxLayout()
        dist_layout.addWidget(QLabel('Distribución inicial (p):'))
        self.p_input = QTextEdit()  # Campo de texto para la distribución inicial.
        dist_layout.addWidget(self.p_input)
        matrices_layout.addLayout(dist_layout)
        
        # Sección para los valores de opiniones.
        values_layout = QVBoxLayout()
        values_layout.addWidget(QLabel('Valores de opiniones (v):'))
        self.v_input = QTextEdit()  # Campo de texto para los valores de opiniones.
        values_layout.addWidget(self.v_input)
        matrices_layout.addLayout(values_layout)
        
        # Sección para los costos extra.
        ce_layout = QVBoxLayout()
        ce_layout.addWidget(QLabel('Costos extra (ce):'))
        self.ce_input = QTextEdit()  # Campo de texto para los costos extra.
        ce_layout.addWidget(self.ce_input)
        matrices_layout.addLayout(ce_layout)
        
        # Añadir el layout de matrices y vectores al layout principal.
        layout.addLayout(matrices_layout)
        
        # Campo de texto para la matriz de costos.
        layout.addWidget(QLabel('Matriz de costos (c):'))
        self.c_input = QTextEdit()  # Campo de texto para la matriz de costos.
        layout.addWidget(self.c_input)
        
        # Botones para cargar el archivo MPL y resolver el problema.
        buttons_layout = QHBoxLayout()
        
        # Botón para cargar un archivo .mpl.
        load_button = QPushButton('Cargar .mpl')
        load_button.clicked.connect(self.load_mpl)  # Conectar el botón con la función de carga de archivo MPL.
        buttons_layout.addWidget(load_button)
        
        # Botón para resolver el problema.
        solve_button = QPushButton('Resolver')
        solve_button.clicked.connect(self.solve)  # Conectar el botón con la función de resolver.
        buttons_layout.addWidget(solve_button)
        
        # Añadir los botones al layout principal.
        layout.addLayout(buttons_layout)
        
        # Sección para mostrar los resultados.
        layout.addWidget(QLabel('<h2 style="color: #4CAF50;">Resultados:</h2>'))
        self.results_text = QTextEdit()  # Campo de texto para mostrar los resultados.
        self.results_text.setReadOnly(True)  # Establecer el campo como solo lectura.
        self.results_text.setStyleSheet("""  # Estilo del área de resultados.
            background-color: #222222;
            color: #FFFFFF;
            padding: 10px;
            font-family: Courier, monospace;
            font-size: 18px;
        """)
        self.results_text.setFixedHeight(300)  # Establecer altura fija del área de resultados.
        layout.addWidget(self.results_text)
        
        # Estilo del fondo de la ventana.
        main_widget.setStyleSheet("""
            background-color: #2E2E2E;
            color: #FFFFFF;
        """)
        
        # Establecer el layout principal del widget.
        main_widget.setLayout(layout)
    
    # Función para seleccionar el archivo .mzn
    def select_mzn_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'Seleccionar archivo Proyecto.mzn',
            '',
            'MiniZinc Files (*.mzn);;All Files (*)'
        )
        if filename:
            self.mzn_path = filename
            self.mzn_path_label.setText(f'Archivo seleccionado: {os.path.basename(filename)}')
    
    # Función para cargar un archivo .mpl y prellenar los campos del formulario.
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
                    
                    # Cargar la matriz de costos.
                    matrix_lines = lines[5:5+int(lines[1].strip())]
                    self.c_input.setText(''.join(matrix_lines))
                    
                    self.ct_input.setText(lines[-2].strip())
                    self.maxM_input.setText(lines[-1].strip())
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al cargar archivo: {str(e)}')
    
    # Función para crear el archivo .dzn a partir de los datos ingresados por el usuario.
    def create_dzn_file(self):
        with open('DatosProyecto.dzn', 'w') as f:
            f.write(f'n = {self.n_input.text()};\n')
            f.write(f'm = {self.m_input.text()};\n')
            f.write(f'p = [{self.p_input.toPlainText()}];\n')
            f.write(f'v = [{self.v_input.toPlainText()}];\n')
            f.write(f'ce = [{self.ce_input.toPlainText()}];\n')
            
            # Formatear la matriz de costos.
            matrix_text = self.c_input.toPlainText().strip()
            matrix_rows = matrix_text.split('\n')
            formatted_matrix = '[|' + '|'.join(matrix_rows) + '|]'
            f.write(f'c = {formatted_matrix};\n')
            
            f.write(f'ct = {self.ct_input.text()};\n')
            f.write(f'maxM = {self.maxM_input.text()};\n')
    
    # Función para ejecutar MiniZinc y obtener los resultados.
    def solve(self):
        try:
            # Verificar si se ha seleccionado el archivo MZN.
            if not self.mzn_path:
                QMessageBox.critical(self, 'Error', 
                                   'Por favor, selecciona primero el archivo Proyecto.mzn')
                return
            
            # Verificar si el archivo MZN existe en el sistema.
            if not os.path.exists(self.mzn_path):
                QMessageBox.critical(self, 'Error', 
                                   f'No se puede encontrar el archivo:\n{self.mzn_path}')
                return
                
            self.create_dzn_file()  # Crear el archivo .dzn.
            
            # Ejecutar el comando de MiniZinc para resolver el problema.
            result = subprocess.run(['minizinc', self.mzn_path, 'DatosProyecto.dzn'], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.results_text.setText(result.stdout)  # Mostrar los resultados en el área de texto.
            else:
                self.results_text.setText(f"Error al ejecutar MiniZinc:\n{result.stderr}")  # Mostrar errores si los hay.
        
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Ocurrió un error: {str(e)}')


# Bloque principal para ejecutar la aplicación.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MinPolGUI()  # Crear la ventana principal.
    window.show()  # Mostrar la ventana.
    sys.exit(app.exec())  # Ejecutar la aplicación.
