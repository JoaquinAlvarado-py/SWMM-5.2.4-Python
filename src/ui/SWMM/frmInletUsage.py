import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QGroupBox
from core.swmm.inlet import InletUsage, PLACEMENT_NAMES


class frmInletUsage(QMainWindow):
    def __init__(self, main_form, edit_these, new_item):
        QMainWindow.__init__(self, main_form)
        self.help_topic = "swmm/src/src/inletusageeditor.htm"
        self._main_form = main_form
        self.project = main_form.project
        self.section = self.project.inlet_usage
        self.new_item = new_item
        self.editing_item = None

        self.setWindowTitle("Inlet Usage Editor")
        self.resize(450, 420)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.setFont(font)

        self._setup_ui()
        self._connect_signals()

        if new_item:
            self.editing_item = new_item
            self.set_from(new_item)
        elif edit_these:
            if isinstance(edit_these, list):
                item = edit_these[0]
                if not isinstance(item, InletUsage):
                    item = self.section.value[item]
                self.editing_item = item
                self.set_from(item)
            else:
                if not isinstance(edit_these, InletUsage):
                    edit_these = self.section.value[edit_these]
                self.editing_item = edit_these
                self.set_from(edit_these)

        if (main_form.program_settings.value("Geometry/frmInletUsage_geometry") and
                main_form.program_settings.value("Geometry/frmInletUsage_state")):
            self.restoreGeometry(main_form.program_settings.value(
                "Geometry/frmInletUsage_geometry", self.geometry(), type=QtCore.QByteArray))
            self.restoreState(main_form.program_settings.value(
                "Geometry/frmInletUsage_state", self.windowState(), type=QtCore.QByteArray))

    def _setup_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Assignment group
        assign_group = QGroupBox("Assignment")
        assign_grid = QGridLayout(assign_group)
        row = 0

        assign_grid.addWidget(QLabel("Conduit:"), row, 0)
        self.cboConduit = QComboBox()
        self.cboConduit.setEditable(True)
        assign_grid.addWidget(self.cboConduit, row, 1)
        row += 1

        assign_grid.addWidget(QLabel("Inlet Design:"), row, 0)
        self.cboInlet = QComboBox()
        self.cboInlet.setEditable(True)
        assign_grid.addWidget(self.cboInlet, row, 1)
        row += 1

        assign_grid.addWidget(QLabel("Capture Node:"), row, 0)
        self.cboCaptureNode = QComboBox()
        self.cboCaptureNode.setEditable(True)
        assign_grid.addWidget(self.cboCaptureNode, row, 1)

        main_layout.addWidget(assign_group)

        # Parameters group
        params_group = QGroupBox("Parameters")
        params_grid = QGridLayout(params_group)
        row = 0

        params_grid.addWidget(QLabel("Number of Inlets:"), row, 0)
        self.txtNumInlets = QLineEdit()
        params_grid.addWidget(self.txtNumInlets, row, 1)
        row += 1

        params_grid.addWidget(QLabel("% Clogged:"), row, 0)
        self.txtPctClogged = QLineEdit()
        params_grid.addWidget(self.txtPctClogged, row, 1)
        row += 1

        params_grid.addWidget(QLabel("Flow Restriction (Qmax):"), row, 0)
        self.txtFlowRestrict = QLineEdit()
        params_grid.addWidget(self.txtFlowRestrict, row, 1)

        main_layout.addWidget(params_group)

        # Local depression group
        depress_group = QGroupBox("Local Gutter Depression")
        depress_grid = QGridLayout(depress_group)

        depress_grid.addWidget(QLabel("Depression Height (ft or m):"), 0, 0)
        self.txtDepressHeight = QLineEdit()
        depress_grid.addWidget(self.txtDepressHeight, 0, 1)

        depress_grid.addWidget(QLabel("Depression Width (ft or m):"), 1, 0)
        self.txtDepressWidth = QLineEdit()
        depress_grid.addWidget(self.txtDepressWidth, 1, 1)

        main_layout.addWidget(depress_group)

        # Placement
        place_layout = QHBoxLayout()
        place_layout.addWidget(QLabel("Placement:"))
        self.cboPlacement = QComboBox()
        self.cboPlacement.addItems(PLACEMENT_NAMES)
        place_layout.addWidget(self.cboPlacement)
        place_layout.addStretch()
        main_layout.addLayout(place_layout)

        # Buttons
        main_layout.addStretch()
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.cmdOK = QPushButton("OK")
        self.cmdCancel = QPushButton("Cancel")
        btn_layout.addWidget(self.cmdOK)
        btn_layout.addWidget(self.cmdCancel)
        main_layout.addLayout(btn_layout)

    def _connect_signals(self):
        self.cmdOK.clicked.connect(self.cmdOK_Clicked)
        self.cmdCancel.clicked.connect(self.cmdCancel_Clicked)

    def set_from(self, usage):
        if not isinstance(usage, InletUsage):
            usage = self.section.value[usage]
        self.editing_item = usage

        # Populate conduit combo
        self.cboConduit.clear()
        if self.project.conduits and self.project.conduits.value:
            for conduit in self.project.conduits.value:
                self.cboConduit.addItem(conduit.name)
        if usage.conduit_id:
            idx = self.cboConduit.findText(usage.conduit_id)
            if idx >= 0:
                self.cboConduit.setCurrentIndex(idx)
            else:
                self.cboConduit.setEditText(usage.conduit_id)

        # Populate inlet combo
        self.cboInlet.clear()
        if self.project.inlets and self.project.inlets.value:
            for inlet in self.project.inlets.value:
                self.cboInlet.addItem(inlet.name)
        if usage.inlet_id:
            idx = self.cboInlet.findText(usage.inlet_id)
            if idx >= 0:
                self.cboInlet.setCurrentIndex(idx)
            else:
                self.cboInlet.setEditText(usage.inlet_id)

        # Populate capture node combo
        self.cboCaptureNode.clear()
        for node in self.project.all_nodes():
            self.cboCaptureNode.addItem(node.name)
        if usage.capture_node_id:
            idx = self.cboCaptureNode.findText(usage.capture_node_id)
            if idx >= 0:
                self.cboCaptureNode.setCurrentIndex(idx)
            else:
                self.cboCaptureNode.setEditText(usage.capture_node_id)

        # Load parameters
        self.txtNumInlets.setText(usage.number_inlets)
        self.txtPctClogged.setText(usage.percent_clogged)
        self.txtFlowRestrict.setText(usage.flow_restriction)
        self.txtDepressHeight.setText(usage.depress_height)
        self.txtDepressWidth.setText(usage.depress_width)

        # Set placement
        placement_idx = 0
        for i, name in enumerate(PLACEMENT_NAMES):
            if name.upper() == usage.placement.upper():
                placement_idx = i
                break
        self.cboPlacement.setCurrentIndex(placement_idx)

    def cmdOK_Clicked(self):
        # Save originals for change detection
        orig = {attr: getattr(self.editing_item, attr) for attr in
                ('conduit_id', 'inlet_id', 'capture_node_id', 'number_inlets',
                 'percent_clogged', 'flow_restriction', 'depress_height',
                 'depress_width', 'placement')}

        # Apply new values
        self.editing_item.conduit_id = self.cboConduit.currentText()
        self.editing_item.inlet_id = self.cboInlet.currentText()
        self.editing_item.capture_node_id = self.cboCaptureNode.currentText()
        self.editing_item.number_inlets = self.txtNumInlets.text()
        self.editing_item.percent_clogged = self.txtPctClogged.text()
        self.editing_item.flow_restriction = self.txtFlowRestrict.text()
        self.editing_item.depress_height = self.txtDepressHeight.text()
        self.editing_item.depress_width = self.txtDepressWidth.text()
        self.editing_item.placement = PLACEMENT_NAMES[self.cboPlacement.currentIndex()]

        if self.new_item:
            self._main_form.add_item(self.new_item)
            self._main_form.mark_project_as_unsaved()
        else:
            changed = any(getattr(self.editing_item, attr) != orig[attr]
                          for attr in orig)
            if changed:
                self._main_form.mark_project_as_unsaved()

        self._main_form.program_settings.setValue("Geometry/frmInletUsage_geometry", self.saveGeometry())
        self._main_form.program_settings.setValue("Geometry/frmInletUsage_state", self.saveState())
        self.close()

    def cmdCancel_Clicked(self):
        self.close()
