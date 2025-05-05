import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QRadioButton, QVBoxLayout,
    QHBoxLayout, QComboBox, QLineEdit, QPushButton, QGridLayout, QGroupBox,
    QMessageBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PIDInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projeto Prático C213 - Sistemas Embarcados")
        self.setStyleSheet("font-family: Arial; font-size: 12px;")
        self.setMinimumWidth(1000)
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        graph_layout = QVBoxLayout()
        control_layout = QVBoxLayout()

        title = QLabel("<h2>Projeto Prático C213 – Sistemas Embarcados</h2>")
        graph_layout.addWidget(title)

        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas)

        # Painel lateral de controle
        group = QGroupBox("Seleção de Sintonia:")
        self.radio_metodo = QRadioButton("Método")
        self.radio_manual = QRadioButton("Manual")
        self.radio_metodo.setChecked(True)
        self.radio_metodo.toggled.connect(self.toggle_inputs)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_metodo)
        radio_layout.addWidget(self.radio_manual)

        self.combo = QComboBox()
        self.combo.addItems(["Cohen & Coon", "Ziegler-Nichols"])

        self.kp_input = QLineEdit("0.0")
        self.ti_input = QLineEdit("0.0")
        self.td_input = QLineEdit("0.0")
        self.sp_input = QLineEdit("20")

        for input_field in [self.kp_input, self.ti_input, self.td_input, self.sp_input]:
            input_field.setFixedWidth(80)

        self.btn_sintonizar = QPushButton("Sintonizar")
        self.btn_exportar = QPushButton("Exportar")
        self.btn_sintonizar.setFixedWidth(100)
        self.btn_exportar.setFixedWidth(100)

        self.btn_sintonizar.setStyleSheet("""
            QPushButton {
                background-color: #007bff; 
                color: white;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        self.btn_exportar.setStyleSheet("""
            QPushButton {
                background-color: #1da1f2; 
                color: white;
                border-radius: 10px;
                padding: 5px;
            }
        """)

        self.btn_sintonizar.clicked.connect(self.sintonizar_pid)
        self.btn_exportar.clicked.connect(self.exportar_config)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_sintonizar)
        btn_layout.addWidget(self.btn_exportar)

        control_grid = QGridLayout()
        control_grid.setVerticalSpacing(5)
        control_grid.addLayout(radio_layout, 0, 0, 1, 2)
        control_grid.addWidget(QLabel("Método de Sintonia:"), 1, 0, 1, 2)
        control_grid.addWidget(self.combo, 2, 0, 1, 2)
        control_grid.addWidget(QLabel("Kp:"), 3, 0)
        control_grid.addWidget(self.kp_input, 3, 1)
        control_grid.addWidget(QLabel("Ti:"), 4, 0)
        control_grid.addWidget(self.ti_input, 4, 1)
        control_grid.addWidget(QLabel("Td:"), 5, 0)
        control_grid.addWidget(self.td_input, 5, 1)
        control_grid.addWidget(QLabel("SP:"), 6, 0)
        control_grid.addWidget(self.sp_input, 6, 1)
        control_grid.addLayout(btn_layout, 7, 0, 1, 2)

        self.input_ts = QLineEdit("-")
        self.input_tr = QLineEdit("-")
        self.input_mp = QLineEdit("-")

        for field in [self.input_ts, self.input_tr, self.input_mp]:
            field.setReadOnly(True)
            field.setFixedWidth(80)

        control_grid.addWidget(QLabel("ts:"), 8, 0)
        control_grid.addWidget(self.input_ts, 8, 1)
        control_grid.addWidget(QLabel("tr:"), 9, 0)
        control_grid.addWidget(self.input_tr, 9, 1)
        control_grid.addWidget(QLabel("mp:"), 10, 0)
        control_grid.addWidget(self.input_mp, 10, 1)

        group.setLayout(control_grid)
        control_layout.addWidget(group)

        main_layout.addLayout(graph_layout)
        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)

        self.toggle_inputs()
        self.plot_pid_response(2.0, 3.0, 1.0, 20)  # Resposta inicial

    def toggle_inputs(self):
        metodo_checked = self.radio_metodo.isChecked()
        self.kp_input.setEnabled(not metodo_checked)
        self.ti_input.setEnabled(not metodo_checked)
        self.td_input.setEnabled(not metodo_checked)
        self.sp_input.setEnabled(True)

    def sintonizar_pid(self):
        try:
            sp = float(self.sp_input.text())

            if self.radio_manual.isChecked():
                kp = float(self.kp_input.text())
                ti = float(self.ti_input.text())
                td = float(self.td_input.text())
            else:
                metodo = self.combo.currentText()
                if metodo == "Ziegler-Nichols":
                    kp, ti, td = 2.0, 3.0, 1.0
                elif metodo == "Cohen & Coon":
                    kp, ti, td = 1.5, 4.0, 0.8

                self.kp_input.setText(f"{kp:.2f}")
                self.ti_input.setText(f"{ti:.2f}")
                self.td_input.setText(f"{td:.2f}")

            self.plot_pid_response(kp, ti, td, sp)

            self.input_ts.setText("130.2")
            self.input_tr.setText("45.0")
            self.input_mp.setText("4.7%")
        except ValueError:
            QMessageBox.warning(self, "Erro", "Verifique os valores inseridos.")

    def plot_pid_response(self, kp, ti, td, sp):
        self.figure.clear()  # Clear the previous figure
        ax = self.figure.add_subplot(111)

        t = [i for i in range(0, 321)]
        y = [sp * (1 - 2.718 ** (-0.02 * i)) for i in t]

        ax.plot(t, y, 'k')
        ax.axhline(sp, linestyle='--', color='blue')
        ax.plot(15, y[15], 'ro')
        ax.text(180, 0.9 * sp, f"ts ≈ 130s\nSP = {sp}", fontsize=10,
                bbox=dict(facecolor='yellow', alpha=0.7))
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Temperatura")
        ax.set_title("Resposta do Sistema PID")
        self.canvas.draw()

    def exportar_config(self):
        try:
            with open("configuracao_pid.txt", "w") as f:
                f.write("Parâmetros PID e SP\n")
                f.write(f"Kp: {self.kp_input.text()}\n")
                f.write(f"Ti: {self.ti_input.text()}\n")
                f.write(f"Td: {self.td_input.text()}\n")
                f.write(f"SP: {self.sp_input.text()}\n")
                f.write(f"ts: {self.input_ts.text()}\n")
                f.write(f"tr: {self.input_tr.text()}\n")
                f.write(f"mp: {self.input_mp.text()}\n")
            QMessageBox.information(self, "Sucesso", "Configuração exportada com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PIDInterface()
    window.show()
    sys.exit(app.exec_())
