from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from PySide6 import QtCore, QtGui, QtWidgets

from conversion import ConversionMode, ConversionRequest
from service import GlossaryJobInput, OcrJobInput, PptExtractJobInput, ServiceLayer


class FileListWidget(QtWidgets.QListWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.exists():
                self.addItem(str(path))
        event.acceptProposedAction()

    def paths(self) -> List[Path]:
        return [Path(self.item(index).text()) for index in range(self.count())]

    def remove_selected(self) -> None:
        for item in self.selectedItems():
            row = self.row(item)
            self.takeItem(row)


@dataclass
class UiState:
    output: Optional[Path]


class ConversionWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SH File Helper")
        self.resize(1000, 700)

        self._service = ServiceLayer()
        self._state = UiState(output=None)

        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        layout = QtWidgets.QVBoxLayout(root)

        self.tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.tabs)

        self._conversion_tab = self._build_conversion_tab()
        self._ocr_tab = self._build_ocr_tab()
        self._ppt_tab = self._build_ppt_tab()
        self._glossary_tab = self._build_glossary_tab()

        self.tabs.addTab(self._conversion_tab, "Conversion")
        self.tabs.addTab(self._ocr_tab, "OCR")
        self.tabs.addTab(self._ppt_tab, "PPT Extract")
        self.tabs.addTab(self._glossary_tab, "Glossary")

        self.task_table = QtWidgets.QTableWidget(0, 4)
        self.task_table.setHorizontalHeaderLabels(["Task ID", "Description", "Status", "Result"])
        self.task_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(QtWidgets.QLabel("Task Queue"))
        layout.addWidget(self.task_table)

        self.status_label = QtWidgets.QLabel("Idle")
        layout.addWidget(self.status_label)

        self._update_conversion_output_placeholder(self.mode_combo.currentText())

    def _build_conversion_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(tab)

        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems([mode.value for mode in ConversionMode])
        self.mode_combo.currentTextChanged.connect(self._update_conversion_output_placeholder)
        layout.addRow("Conversion Mode", self.mode_combo)

        self.conversion_inputs = FileListWidget()
        conversion_buttons = self._build_file_buttons(self.conversion_inputs, multi=True)
        layout.addRow("Input Files", self._wrap_list_with_buttons(self.conversion_inputs, conversion_buttons))

        self.conversion_output = QtWidgets.QLineEdit()
        browse_output = QtWidgets.QPushButton("Browse")
        browse_output.clicked.connect(self._select_conversion_output)
        layout.addRow("Output File", self._wrap_path_field(self.conversion_output, browse_output))

        run_button = QtWidgets.QPushButton("Run Conversion")
        run_button.clicked.connect(self._run_conversion)
        layout.addRow(run_button)

        return tab

    def _build_ocr_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(tab)

        self.ocr_mode = QtWidgets.QComboBox()
        self.ocr_mode.addItems(["ocr_image", "ocr_pdf"])
        layout.addRow("OCR Mode", self.ocr_mode)

        self.ocr_input = FileListWidget()
        ocr_buttons = self._build_file_buttons(self.ocr_input, multi=False)
        layout.addRow("Input File", self._wrap_list_with_buttons(self.ocr_input, ocr_buttons))

        self.ocr_output = QtWidgets.QLineEdit()
        ocr_browse = QtWidgets.QPushButton("Browse")
        ocr_browse.clicked.connect(lambda: self._select_output_file(self.ocr_output, ".txt"))
        layout.addRow("Output Text", self._wrap_path_field(self.ocr_output, ocr_browse))

        self.ocr_lang = QtWidgets.QComboBox()
        self.ocr_lang.addItem("English", "eng")
        self.ocr_lang.addItem("Chinese Simplified", "chi_sim")
        self.ocr_lang.addItem("Chinese Simplified + English", "chi_sim+eng")
        self.ocr_lang.addItem("Japanese", "jpn")
        self.ocr_lang.addItem("Korean", "kor")
        self.ocr_lang.setCurrentText("English")
        layout.addRow("Language", self.ocr_lang)

        self.ocr_dpi = QtWidgets.QSpinBox()
        self.ocr_dpi.setRange(72, 600)
        self.ocr_dpi.setValue(300)
        layout.addRow("DPI", self.ocr_dpi)

        run_button = QtWidgets.QPushButton("Run OCR")
        run_button.clicked.connect(self._run_ocr)
        layout.addRow(run_button)

        return tab

    def _build_ppt_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(tab)

        self.ppt_input = FileListWidget()
        ppt_buttons = self._build_file_buttons(self.ppt_input, multi=False)
        layout.addRow("PPTX File", self._wrap_list_with_buttons(self.ppt_input, ppt_buttons))

        self.ppt_output = QtWidgets.QLineEdit()
        ppt_browse = QtWidgets.QPushButton("Browse")
        ppt_browse.clicked.connect(lambda: self._select_output_file(self.ppt_output, ".txt"))
        layout.addRow("Output Text", self._wrap_path_field(self.ppt_output, ppt_browse))

        self.ppt_lang = QtWidgets.QComboBox()
        self.ppt_lang.addItem("English", "eng")
        self.ppt_lang.addItem("Chinese Simplified", "chi_sim")
        self.ppt_lang.addItem("Chinese Simplified + English", "chi_sim+eng")
        self.ppt_lang.addItem("Japanese", "jpn")
        self.ppt_lang.addItem("Korean", "kor")
        self.ppt_lang.setCurrentText("English")
        layout.addRow("OCR Language", self.ppt_lang)

        run_button = QtWidgets.QPushButton("Extract PPT Text")
        run_button.clicked.connect(self._run_ppt_extract)
        layout.addRow(run_button)

        return tab

    def _build_glossary_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(tab)

        self.glossary_inputs = FileListWidget()
        glossary_buttons = self._build_file_buttons(self.glossary_inputs, multi=True)
        layout.addRow("Input Files", self._wrap_list_with_buttons(self.glossary_inputs, glossary_buttons))

        self.glossary_output = QtWidgets.QLineEdit()
        glossary_browse = QtWidgets.QPushButton("Browse")
        glossary_browse.clicked.connect(lambda: self._select_output_file(self.glossary_output, ".txt"))
        layout.addRow("Output File", self._wrap_path_field(self.glossary_output, glossary_browse))

        self.glossary_top_k = QtWidgets.QSpinBox()
        self.glossary_top_k.setRange(1, 500)
        self.glossary_top_k.setValue(30)
        layout.addRow("Top K", self.glossary_top_k)

        self.glossary_window = QtWidgets.QSpinBox()
        self.glossary_window.setRange(2, 10)
        self.glossary_window.setValue(4)
        layout.addRow("Window Size", self.glossary_window)

        self.glossary_min_length = QtWidgets.QSpinBox()
        self.glossary_min_length.setRange(1, 50)
        self.glossary_min_length.setValue(2)
        layout.addRow("Min Term Length", self.glossary_min_length)

        self.glossary_format = QtWidgets.QComboBox()
        self.glossary_format.addItems(["txt", "json"])
        layout.addRow("Output Format", self.glossary_format)

        self.glossary_lang = QtWidgets.QComboBox()
        self.glossary_lang.addItem("English", "eng")
        self.glossary_lang.addItem("Chinese Simplified", "chi_sim")
        self.glossary_lang.addItem("Chinese Simplified + English", "chi_sim+eng")
        self.glossary_lang.addItem("Japanese", "jpn")
        self.glossary_lang.addItem("Korean", "kor")
        self.glossary_lang.setCurrentText("English")
        layout.addRow("OCR Language", self.glossary_lang)

        self.glossary_dpi = QtWidgets.QSpinBox()
        self.glossary_dpi.setRange(72, 600)
        self.glossary_dpi.setValue(300)
        layout.addRow("OCR DPI", self.glossary_dpi)

        run_button = QtWidgets.QPushButton("Generate Glossary")
        run_button.clicked.connect(self._run_glossary)
        layout.addRow(run_button)

        return tab

    def _build_file_buttons(self, widget: FileListWidget, multi: bool) -> QtWidgets.QVBoxLayout:
        buttons = QtWidgets.QVBoxLayout()
        add_button = QtWidgets.QPushButton("Add Files")
        add_button.clicked.connect(lambda: self._add_inputs(widget, multi))
        remove_button = QtWidgets.QPushButton("Remove Selected")
        remove_button.clicked.connect(widget.remove_selected)
        buttons.addWidget(add_button)
        buttons.addWidget(remove_button)
        buttons.addStretch()
        return buttons

    def _wrap_list_with_buttons(
        self, list_widget: FileListWidget, buttons: QtWidgets.QVBoxLayout
    ) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.addWidget(list_widget, stretch=1)
        layout.addLayout(buttons)
        return container

    def _wrap_path_field(self, field: QtWidgets.QLineEdit, button: QtWidgets.QWidget) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.addWidget(field, stretch=1)
        layout.addWidget(button)
        return container

    def _add_inputs(self, widget: FileListWidget, multi: bool) -> None:
        if multi:
            files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Input Files")
        else:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Input File")
            files = [file_path] if file_path else []
        for file_path in files:
            if not file_path:
                continue
            widget.addItem(file_path)

    def _select_output_file(self, field: QtWidgets.QLineEdit, suffix: str) -> None:
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            filter=f"Output (*{suffix})",
        )
        if filename:
            field.setText(filename)

    def _select_conversion_output(self) -> None:
        mode = ConversionMode(self.mode_combo.currentText())
        suffix = _output_suffix(mode)
        self._select_output_file(self.conversion_output, suffix)

    def _run_conversion(self) -> None:
        inputs = self.conversion_inputs.paths()
        output = self.conversion_output.text().strip()
        if not inputs:
            self._set_status("Error: Please select at least one input file.")
            return
        if not output:
            self._set_status("Error: Please choose an output path.")
            return

        request = ConversionRequest(
            mode=ConversionMode(self.mode_combo.currentText()),
            input_paths=inputs,
            output_path=Path(output),
        )
        task = self._service.submit_conversion(request)
        self._service.queue.run_all()
        self._refresh_tasks()
        self._report_task(task)

    def _run_ocr(self) -> None:
        inputs = self.ocr_input.paths()
        output = self.ocr_output.text().strip()
        if len(inputs) != 1:
            self._set_status("Error: Please select exactly one OCR input file.")
            return
        if not output:
            self._set_status("Error: Please choose an output path.")
            return

        request = OcrJobInput(
            input_path=inputs[0],
            output_path=Path(output),
            language=self.ocr_lang.currentData(),
            dpi=self.ocr_dpi.value(),
        )
        if self.ocr_mode.currentText() == "ocr_image":
            task = self._service.submit_ocr_image(request)
        else:
            task = self._service.submit_ocr_pdf(request)
        self._service.queue.run_all()
        self._refresh_tasks()
        self._report_task(task)

    def _run_ppt_extract(self) -> None:
        inputs = self.ppt_input.paths()
        output = self.ppt_output.text().strip()
        if len(inputs) != 1:
            self._set_status("Error: Please select exactly one PPTX file.")
            return
        if not output:
            self._set_status("Error: Please choose an output path.")
            return

        request = PptExtractJobInput(
            input_path=inputs[0],
            output_path=Path(output),
            language=self.ppt_lang.currentData(),
        )
        task = self._service.submit_ppt_extract(request)
        self._service.queue.run_all()
        self._refresh_tasks()
        self._report_task(task)

    def _run_glossary(self) -> None:
        inputs = self.glossary_inputs.paths()
        output = self.glossary_output.text().strip()
        if not inputs:
            self._set_status("Error: Please select glossary input files.")
            return
        if not output:
            self._set_status("Error: Please choose an output path.")
            return

        request = GlossaryJobInput(
            input_paths=inputs,
            output_path=Path(output),
            top_k=self.glossary_top_k.value(),
            window_size=self.glossary_window.value(),
            min_term_length=self.glossary_min_length.value(),
            language=self.glossary_lang.currentData(),
            dpi=self.glossary_dpi.value(),
            output_format=self.glossary_format.currentText(),
        )
        task = self._service.submit_glossary(request)
        self._service.queue.run_all()
        self._refresh_tasks()
        self._report_task(task)

    def _report_task(self, task) -> None:
        if task.status.value == "completed":
            self._set_status(f"Completed: {task.result}")
        else:
            self._set_status(f"Failed: {task.error}")

    def _refresh_tasks(self) -> None:
        tasks = self._service.queue.list_tasks()
        self.task_table.setRowCount(len(tasks))
        for row, task in enumerate(tasks):
            self.task_table.setItem(row, 0, QtWidgets.QTableWidgetItem(task.task_id))
            self.task_table.setItem(row, 1, QtWidgets.QTableWidgetItem(task.description))
            self.task_table.setItem(row, 2, QtWidgets.QTableWidgetItem(task.status.value))
            result_text = str(task.result) if task.result is not None else ""
            self.task_table.setItem(row, 3, QtWidgets.QTableWidgetItem(result_text))

    def _update_conversion_output_placeholder(self, mode_text: str) -> None:
        mode = ConversionMode(mode_text)
        suffix = _output_suffix(mode)
        self.conversion_output.setPlaceholderText(f"Select output path ({suffix})")

    def _set_status(self, message: str) -> None:
        self.status_label.setText(message)


def _output_suffix(mode: ConversionMode) -> str:
    mapping = {
        ConversionMode.PPTX_TO_PDF: ".pdf",
        ConversionMode.PDF_TO_PPTX: ".pptx",
        ConversionMode.DOCX_TO_PDF: ".pdf",
        ConversionMode.PDF_TO_DOCX: ".docx",
        ConversionMode.IMAGE_TO_PDF: ".pdf",
        ConversionMode.IMAGES_TO_PDF: ".pdf",
    }
    return mapping[mode]


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = ConversionWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()