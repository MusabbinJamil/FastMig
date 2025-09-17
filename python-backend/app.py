import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QFileDialog, QGridLayout, QMessageBox, QComboBox, QAction,
    QInputDialog
)
from functions import read_file, convert_column, export_data
import json

class DataMigrationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None  # DataFrame to hold the loaded data
        self.file_path = None  # File path for the selected file
        self.selected_column = None  # Track the currently selected column
        self.normal_size = (800, 600)  # Default window size
        self.is_small = False  # Track if window is in small (50x50) mode
        self.recorded_actions = []  # Add this to store recorded actions
        self.is_recording = False   # Add this to track recording state
        self.initUI()

    def initUI(self):
        self.setWindowTitle('FastMig')
        self.setGeometry(100, 100, *self.normal_size)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Initialize Menu Bar
        self.initMenuBar()

        # Grid layout for organizing two sections side by side
        grid_layout = QGridLayout()

        # --------------- Load Data Section (Left Column) ---------------
        load_data_layout = QVBoxLayout()
        file_label = QLabel('Load data')
        load_data_layout.addWidget(file_label)

        self.file_label = QLabel('No file selected')
        load_data_layout.addWidget(self.file_label)

        # Add Load Data section to grid layout (left column, first row)
        grid_layout.addLayout(load_data_layout, 0, 0)

        # --------------- Process Data Section (Right Column) ---------------
        process_data_layout = QGridLayout()

        # "Selected Column" label and display
        process_data_layout.addWidget(QLabel('Selected Column:'), 0, 0)
        self.selected_column_display = QLabel('No column selected')
        process_data_layout.addWidget(self.selected_column_display, 0, 1)

        # "Data Type" label and display
        process_data_layout.addWidget(QLabel('Data Type:'), 1, 0)
        self.type_display = QLabel('N/A')
        process_data_layout.addWidget(self.type_display, 1, 1)

        # "Format To" label and dropdown
        process_data_layout.addWidget(QLabel('Format To:'), 2, 0)
        self.format_selector = QComboBox()
        process_data_layout.addWidget(self.format_selector, 2, 1)

        # Add Process Data section to grid layout (right column, first row)
        grid_layout.addLayout(process_data_layout, 0, 1)

        # --------------- Loaded Data Section (Full width, New Row) ---------------
        loaded_data_layout = QVBoxLayout()
        # loaded_data_label = QLabel('Loaded data:')
        # loaded_data_layout.addWidget(loaded_data_label)

        self.table_widget = QTableWidget()
        self.table_widget.setSelectionBehavior(QTableWidget.SelectColumns)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.itemSelectionChanged.connect(self.on_column_selected)
        loaded_data_layout.addWidget(self.table_widget)

        # Dropdown for selecting number of rows to display
        self.row_selector = QSpinBox()
        self.row_selector.setMinimum(1)
        self.row_selector.setValue(5)
        self.row_selector.setSuffix(" rows")
        self.row_selector.valueChanged.connect(self.update_table)
        loaded_data_layout.addWidget(self.row_selector)

        # Add Loaded Data section to grid layout
        grid_layout.addLayout(loaded_data_layout, 1, 0, 1, 2)

        # Set equal column stretch factor
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        # Add the grid layout to the main layout
        main_layout.addLayout(grid_layout)

    # --------------- Initialize Menu Bar ---------------
    def initMenuBar(self):
        menubar = self.menuBar()

        # --------------- File Menu ---------------
        file_menu = menubar.addMenu('File')

        # Open Action
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Save Action
        self.save_action = QAction('Save', self)
        self.save_action.triggered.connect(self.save_file)
        self.save_action.setEnabled(False)  # Initially disabled
        file_menu.addAction(self.save_action)

        # Save As Action
        self.save_as_action = QAction('Save As', self)
        self.save_as_action.triggered.connect(self.save_file_as)
        self.save_as_action.setEnabled(False)  # Initially disabled
        file_menu.addAction(self.save_as_action)

        # --------------- Edit Menu ---------------
        edit_menu = menubar.addMenu('Edit')

        # Undo Action
        self.undo_action = QAction('Undo', self)
        self.undo_action.triggered.connect(self.undo_change)
        self.undo_action.setEnabled(False)  # Initially disabled
        edit_menu.addAction(self.undo_action)

        # Redo Action
        self.redo_action = QAction('Redo', self)
        self.redo_action.triggered.connect(self.redo_change)
        self.redo_action.setEnabled(False)  # Initially disabled
        edit_menu.addAction(self.redo_action)

        # --------------- View Menu ---------------
        view_menu = menubar.addMenu('View')

        # Full Screen Action
        full_screen_action = QAction('Toggle Full Screen', self, checkable=True)
        full_screen_action.triggered.connect(self.toggle_full_screen)
        view_menu.addAction(full_screen_action)

        # Layout Options
        layout_action = QAction('Switch Layout', self)
        layout_action.triggered.connect(self.switch_layout)
        view_menu.addAction(layout_action)

        # --------------- Process Menu ---------------
        special_menu = menubar.addMenu('Process')

        # Process Action
        process_action = QAction('Process', self)
        process_action.triggered.connect(self.process_file)
        special_menu.addAction(process_action)

        # Add new Macro menu
        macro_menu = menubar.addMenu('Macro')

        # Start Recording Action
        self.record_action = QAction('Start Recording', self)
        self.record_action.triggered.connect(self.toggle_recording)
        macro_menu.addAction(self.record_action)

        # Save Recording Action
        self.save_recording_action = QAction('Save Recording', self)
        self.save_recording_action.triggered.connect(self.save_recording)
        self.save_recording_action.setEnabled(False)
        macro_menu.addAction(self.save_recording_action)

        # Load and Run Recording Action
        self.run_recording_action = QAction('Load & Run Recording', self)
        self.run_recording_action.triggered.connect(self.load_and_run_recording)
        macro_menu.addAction(self.run_recording_action)

    # --------------- Save and Save As Methods ---------------
    def save_file(self):
        if self.file_path:
            export_data(self.df, self.file_path)
            self.file_label.setText(f'Saved file to {self.file_path}')
            self.add_to_history()  # After save, clear the redo stack

    def save_file_as(self):
        output_path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)")
        if output_path:
            export_data(self.df, output_path)
            self.file_path = output_path
            self.file_label.setText(f'Saved file to {output_path}')
            self.add_to_history()  # After save, clear the redo stack

    # --------------- Undo and Redo Methods with Stack ---------------
    def add_to_history(self):
        """Adds the current state to the undo history."""
        self.undo_stack.append(self.df.copy())  # Save a copy of the current DataFrame
        self.redo_stack.clear()  # Clear redo stack whenever a new change is made
        self.update_action_states()

    def undo_change(self):
        """Undo the last change by restoring from the undo stack."""
        if self.undo_stack:
            self.redo_stack.append(self.df.copy())  # Move current state to redo stack
            self.df = self.undo_stack.pop()  # Revert to last state in undo stack
            self.update_table()  # Update the table with the reverted data
            self.update_action_states()

    def redo_change(self):
        """Redo the last undone change by restoring from the redo stack."""
        if self.redo_stack:
            self.undo_stack.append(self.df.copy())  # Move current state to undo stack
            self.df = self.redo_stack.pop()  # Restore the next state from redo stack
            self.update_table()  # Update the table with the redone data
            self.update_action_states()

    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.recorded_actions = []  # Clear previous recordings
            self.record_action.setText('Stop Recording')
            self.save_recording_action.setEnabled(False)
        else:
            self.record_action.setText('Start Recording')
            self.save_recording_action.setEnabled(True)

    def record_action_step(self, action_type, **params):
        if self.is_recording:
            self.recorded_actions.append({
                'action_type': action_type,
                'params': params
            })

    def save_recording(self):
        if not self.recorded_actions:
            QMessageBox.warning(self, 'Warning', 'No actions recorded!')
            return

        name, ok = QInputDialog.getText(self, 'Save Recording', 'Enter name for this recording:')
        if ok and name:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Recording", f"{name}.json", "JSON Files (*.json)")
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(self.recorded_actions, f)
                QMessageBox.information(self, 'Success', 'Recording saved successfully!')

    def load_and_run_recording(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Recording", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'r') as f:
                actions = json.load(f)
            
            # Ask for the file to apply the recording to
            data_file, _ = QFileDialog.getOpenFileName(
                self, "Select File to Process", "", "All Files (*);;CSV Files (*.csv);;Excel Files (*.xls *.xlsx)")
            if data_file:
                self.replay_actions(actions, data_file)

    def replay_actions(self, actions, file_path):
        try:
            self.df = read_file(file_path)
            for action in actions:
                if action['action_type'] == 'convert_column':
                    params = action['params']
                    self.df = convert_column(
                        self.df,
                        params['column_name'],
                        params['target_type'],
                        params.get('format_spec')
                    )
            
            # Ask where to save the processed file
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Save Processed File", "", "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)")
            if output_path:
                export_data(self.df, output_path)
                QMessageBox.information(self, 'Success', 'Recording applied and file saved successfully!')
                self.update_table()
        except Exception as e:
            self.show_error_message(f"Error applying recording: {str(e)}")

    # --------------- Update Action States ---------------
    def update_action_states(self):
        """Enable or disable actions based on the application state."""
        self.save_action.setEnabled(bool(self.file_path))  # Enable save if a file is loaded
        self.save_as_action.setEnabled(bool(self.df is not None))  # Enable save as if data is loaded
        self.undo_action.setEnabled(bool(self.undo_stack))  # Enable undo if there are changes to undo
        self.redo_action.setEnabled(bool(self.redo_stack))  # Enable redo if there are changes to redo

    # --------------- Full Screen Toggle ---------------
    def toggle_full_screen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    # --------------- Layout Switch  ---------------
    def switch_layout(self):
        if not self.is_small:  # If the window is not in small mode
            self.resize(50, 50)  # Resize to small size
            self.is_small = True  # Update the flag to indicate small mode
            print("Window resized to 50x50")
        else:  # If the window is in small mode
            self.resize(*self.normal_size)  # Resize back to normal size
            self.is_small = False  # Update the flag to indicate normal mode
            print(f"Window resized to normal size {self.normal_size}")   

    # --------------- Load file function ---------------
    def open_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*);;CSV Files (*.csv);;Excel Files (*.xls *.xlsx)", options=options)
        if file_path:
            self.file_label.setText(f'Selected File: {file_path}')
            self.file_path = file_path
            self.df = read_file(file_path)
            self.update_table()

    # --------------- Update Table and Column Data Types ---------------
    def update_table(self):
        if self.df is not None:
            num_rows = self.row_selector.value()
            self.table_widget.setRowCount(num_rows)
            self.table_widget.setColumnCount(len(self.df.columns))
            self.table_widget.setHorizontalHeaderLabels(self.df.columns)

            for i in range(num_rows):
                if i < len(self.df):
                    for j, col in enumerate(self.df.columns):
                        self.table_widget.setItem(i, j, QTableWidgetItem(str(self.df.iloc[i, j])))
                else:
                    for j in range(len(self.df.columns)):
                        self.table_widget.setItem(i, j, QTableWidgetItem(''))

    # --------------- Column Selection Event Handler ---------------
    def on_column_selected(self):
        selected_ranges = self.table_widget.selectedRanges()
        if selected_ranges:
            selected_column = selected_ranges[0].leftColumn()
            column_name = self.df.columns[selected_column]
            self.selected_column = column_name
            self.selected_column_display.setText(column_name)
            self.update_type_and_format_options(selected_column)

    # --------------- Update Data Type Display and Format Dropdown ---------------
    def update_type_and_format_options(self, column_index):
        if self.df is not None:
            column_name = self.df.columns[column_index]
            column_dtype = self.df[column_name].dtype

            self.type_display.setText(str(column_dtype))
            self.format_selector.clear()
            if column_dtype in ['int64', 'float64']:
                self.format_selector.addItems(['int', 'decimal', 'string'])
            elif column_dtype == 'object':
                self.format_selector.addItems(['string', 'category', 'bool'])
            elif 'datetime' in str(column_dtype):
                self.format_selector.addItems(['datetime', 'string', 'unix'])
            elif column_dtype == 'bool':
                self.format_selector.addItems(['bool', 'int', 'string'])
            else:
                self.format_selector.addItems(['string', 'object'])

    # --------------- Process File and Column Transformation ---------------
    def process_file(self):
        try:
            if self.file_path and self.selected_column:
                df = read_file(self.file_path)
                column_name = self.selected_column
                target_type = self.format_selector.currentText()

                try:
                    self.df = convert_column(df, column_name, target_type, None)
                    # Record the action
                    self.record_action_step('convert_column', 
                        column_name=column_name,
                        target_type=target_type,
                        format_spec=None
                    )
                except Exception as e:
                    self.show_error_message(str(e))
                    return
                
                self.update_table()
                output_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)")
                if output_path:
                    export_data(self.df, output_path)
                    self.file_label.setText(f'Saved processed file to {output_path}')
            else:
                raise ValueError('No file or column selected!')

        except Exception as e:
            self.show_error_message(str(e))

    # --------------- Error Message Popup ---------------
    def show_error_message(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle('Error')
        error_dialog.setText('An error occurred:')
        error_dialog.setInformativeText(message)
        error_dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = DataMigrationApp()
    main_window.show()
    sys.exit(app.exec_())
