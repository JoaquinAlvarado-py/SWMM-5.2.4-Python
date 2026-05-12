import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTabWidget, QGroupBox
from core.swmm.inlet import Inlet, InletType, GRATE_TYPE_NAMES, THROAT_TYPE_NAMES


class frmInlet(QMainWindow):
    def __init__(self, main_form, edit_these, new_item):
        QMainWindow.__init__(self, main_form)
        self.help_topic = "swmm/src/src/inleteditor.htm"
        self._main_form = main_form
        self.project = main_form.project
        self.section = self.project.inlets
        self.new_item = new_item
        self.editing_item = None

        self.setWindowTitle("Inlet Design Editor")
        self.resize(500, 420)
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
                if not isinstance(item, Inlet):
                    item = self.section.value[item]
                self.editing_item = item
                self.set_from(item)
            else:
                if not isinstance(edit_these, Inlet):
                    edit_these = self.section.value[edit_these]
                self.editing_item = edit_these
                self.set_from(edit_these)

        if (main_form.program_settings.value("Geometry/frmInlet_geometry") and
                main_form.program_settings.value("Geometry/frmInlet_state")):
            self.restoreGeometry(main_form.program_settings.value(
                "Geometry/frmInlet_geometry", self.geometry(), type=QtCore.QByteArray))
            self.restoreState(main_form.program_settings.value(
                "Geometry/frmInlet_state", self.windowState(), type=QtCore.QByteArray))

    def _setup_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Name and Type row
        top_grid = QGridLayout()
        top_grid.addWidget(QLabel("Name:"), 0, 0)
        self.txtName = QLineEdit()
        top_grid.addWidget(self.txtName, 0, 1)

        top_grid.addWidget(QLabel("Inlet Type:"), 1, 0)
        self.cboInletType = QComboBox()
        self.cboInletType.addItems([
            "Grate", "Curb Opening", "Combination (Grate + Curb)",
            "Slotted Drain", "Drop Grate", "Drop Curb Opening", "Custom"
        ])
        top_grid.addWidget(self.cboInletType, 1, 1)
        main_layout.addLayout(top_grid)

        # Tabbed panels for properties
        self.tabInlet = QTabWidget()

        # -- Tab 0: Grate --
        grate_tab = QWidget()
        grate_layout = QGridLayout(grate_tab)
        row = 0

        grate_layout.addWidget(QLabel("Grate Type:"), row, 0)
        self.cboGrateType = QComboBox()
        self.cboGrateType.addItems(GRATE_TYPE_NAMES)
        grate_layout.addWidget(self.cboGrateType, row, 1)
        row += 1

        grate_layout.addWidget(QLabel("Length (ft or m):"), row, 0)
        self.txtGrateLength = QLineEdit()
        grate_layout.addWidget(self.txtGrateLength, row, 1)
        row += 1

        grate_layout.addWidget(QLabel("Width (ft or m):"), row, 0)
        self.txtGrateWidth = QLineEdit()
        grate_layout.addWidget(self.txtGrateWidth, row, 1)
        row += 1

        self.lblOpenFrac = QLabel("Open Area Fraction:")
        grate_layout.addWidget(self.lblOpenFrac, row, 0)
        self.txtOpenFraction = QLineEdit()
        grate_layout.addWidget(self.txtOpenFraction, row, 1)
        row += 1

        self.lblSplashVel = QLabel("Splash-Over Velocity (ft/s or m/s):")
        grate_layout.addWidget(self.lblSplashVel, row, 0)
        self.txtSplashVelocity = QLineEdit()
        grate_layout.addWidget(self.txtSplashVelocity, row, 1)

        grate_layout.setRowStretch(row + 1, 1)
        self.tabInlet.addTab(grate_tab, "Grate")

        # -- Tab 1: Curb Opening --
        curb_tab = QWidget()
        curb_layout = QGridLayout(curb_tab)
        row = 0

        curb_layout.addWidget(QLabel("Length (ft or m):"), row, 0)
        self.txtCurbLength = QLineEdit()
        curb_layout.addWidget(self.txtCurbLength, row, 1)
        row += 1

        curb_layout.addWidget(QLabel("Height (ft or m):"), row, 0)
        self.txtCurbHeight = QLineEdit()
        curb_layout.addWidget(self.txtCurbHeight, row, 1)
        row += 1

        curb_layout.addWidget(QLabel("Throat Angle:"), row, 0)
        self.cboThroat = QComboBox()
        self.cboThroat.addItems(THROAT_TYPE_NAMES)
        curb_layout.addWidget(self.cboThroat, row, 1)

        curb_layout.setRowStretch(row + 1, 1)
        self.tabInlet.addTab(curb_tab, "Curb Opening")

        # -- Tab 2: Slotted Drain --
        slotted_tab = QWidget()
        slotted_layout = QGridLayout(slotted_tab)
        row = 0

        slotted_layout.addWidget(QLabel("Length (ft or m):"), row, 0)
        self.txtSlottedLength = QLineEdit()
        slotted_layout.addWidget(self.txtSlottedLength, row, 1)
        row += 1

        slotted_layout.addWidget(QLabel("Width (ft or m):"), row, 0)
        self.txtSlottedWidth = QLineEdit()
        slotted_layout.addWidget(self.txtSlottedWidth, row, 1)

        slotted_layout.setRowStretch(row + 1, 1)
        self.tabInlet.addTab(slotted_tab, "Slotted Drain")

        # -- Tab 3: Custom --
        custom_tab = QWidget()
        custom_layout = QGridLayout(custom_tab)

        custom_layout.addWidget(QLabel("Diversion/Rating Curve:"), 0, 0)
        self.cboCustomCurve = QComboBox()
        self.cboCustomCurve.setEditable(True)
        custom_layout.addWidget(self.cboCustomCurve, 0, 1)

        custom_layout.setRowStretch(1, 1)
        self.tabInlet.addTab(custom_tab, "Custom")

        main_layout.addWidget(self.tabInlet)

        # Buttons
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
        self.cboInletType.currentIndexChanged.connect(self._inlet_type_changed)
        self.cboGrateType.currentIndexChanged.connect(self._grate_type_changed)

    def set_from(self, inlet):
        if not isinstance(inlet, Inlet):
            inlet = self.section.value[inlet]
        self.editing_item = inlet
        self.txtName.setText(inlet.name)

        # Set inlet type combo
        type_map = {
            InletType.GRATE: 0, InletType.CURB: 1, InletType.COMBO: 2,
            InletType.SLOTTED: 3, InletType.DROP_GRATE: 4,
            InletType.DROP_CURB: 5, InletType.CUSTOM: 6
        }
        self.cboInletType.setCurrentIndex(type_map.get(inlet.inlet_type, 0))

        # Load grate properties
        grate_idx = 0
        for i, name in enumerate(GRATE_TYPE_NAMES):
            if name.upper() == inlet.grate_type.upper():
                grate_idx = i
                break
        self.cboGrateType.setCurrentIndex(grate_idx)
        self.txtGrateLength.setText(inlet.grate_length)
        self.txtGrateWidth.setText(inlet.grate_width)
        self.txtOpenFraction.setText(inlet.grate_open_fraction)
        self.txtSplashVelocity.setText(inlet.grate_splash_velocity)

        # Load curb properties
        throat_idx = 0
        for i, name in enumerate(THROAT_TYPE_NAMES):
            if name.upper() == inlet.curb_throat.upper():
                throat_idx = i
                break
        self.cboThroat.setCurrentIndex(throat_idx)
        self.txtCurbLength.setText(inlet.curb_length)
        self.txtCurbHeight.setText(inlet.curb_height)

        # Load slotted properties
        self.txtSlottedLength.setText(inlet.slotted_length)
        self.txtSlottedWidth.setText(inlet.slotted_width)

        # Load custom curve
        self._populate_curves()
        if inlet.custom_curve:
            idx = self.cboCustomCurve.findText(inlet.custom_curve)
            if idx >= 0:
                self.cboCustomCurve.setCurrentIndex(idx)
            else:
                self.cboCustomCurve.setEditText(inlet.custom_curve)

        self._inlet_type_changed(self.cboInletType.currentIndex())
        self._grate_type_changed(self.cboGrateType.currentIndex())

    def _populate_curves(self):
        self.cboCustomCurve.clear()
        self.cboCustomCurve.addItem("")
        if self.project.curves and self.project.curves.value:
            for curve in self.project.curves.value:
                self.cboCustomCurve.addItem(curve.name)

    def _inlet_type_changed(self, index):
        # Enable/disable tabs based on inlet type
        # 0=Grate, 1=Curb, 2=Combo, 3=Slotted, 4=DropGrate, 5=DropCurb, 6=Custom
        grate_on = index in (0, 2, 4)     # Grate, Combo, DropGrate
        curb_on = index in (1, 2, 5)      # Curb, Combo, DropCurb
        slotted_on = index == 3           # Slotted
        custom_on = index == 6            # Custom

        self.tabInlet.setTabEnabled(0, grate_on)
        self.tabInlet.setTabEnabled(1, curb_on)
        self.tabInlet.setTabEnabled(2, slotted_on)
        self.tabInlet.setTabEnabled(3, custom_on)

        # Show throat angle only for CURB and COMBO (not DROP_CURB)
        self.cboThroat.setVisible(index != 5)

        # Auto-select first enabled tab
        for i in range(4):
            if self.tabInlet.isTabEnabled(i):
                self.tabInlet.setCurrentIndex(i)
                break

    def _grate_type_changed(self, index):
        # Show open fraction and splash velocity only for GENERIC grate type
        is_generic = (index == len(GRATE_TYPE_NAMES) - 1)  # GENERIC is last
        self.lblOpenFrac.setVisible(is_generic)
        self.txtOpenFraction.setVisible(is_generic)
        self.lblSplashVel.setVisible(is_generic)
        self.txtSplashVelocity.setVisible(is_generic)

    def cmdOK_Clicked(self):
        oldname = self.editing_item.name

        # Save originals for change detection
        orig = {attr: getattr(self.editing_item, attr) for attr in
                ('name', 'inlet_type', 'grate_type', 'grate_length', 'grate_width',
                 'grate_open_fraction', 'grate_splash_velocity',
                 'curb_length', 'curb_height', 'curb_throat',
                 'slotted_length', 'slotted_width', 'custom_curve')}

        # Apply new values
        self.editing_item.name = self.txtName.text()

        type_map = [InletType.GRATE, InletType.CURB, InletType.COMBO,
                    InletType.SLOTTED, InletType.DROP_GRATE,
                    InletType.DROP_CURB, InletType.CUSTOM]
        self.editing_item.inlet_type = type_map[self.cboInletType.currentIndex()]

        self.editing_item.grate_type = GRATE_TYPE_NAMES[self.cboGrateType.currentIndex()]
        self.editing_item.grate_length = self.txtGrateLength.text()
        self.editing_item.grate_width = self.txtGrateWidth.text()
        self.editing_item.grate_open_fraction = self.txtOpenFraction.text()
        self.editing_item.grate_splash_velocity = self.txtSplashVelocity.text()

        self.editing_item.curb_length = self.txtCurbLength.text()
        self.editing_item.curb_height = self.txtCurbHeight.text()
        self.editing_item.curb_throat = THROAT_TYPE_NAMES[self.cboThroat.currentIndex()]

        self.editing_item.slotted_length = self.txtSlottedLength.text()
        self.editing_item.slotted_width = self.txtSlottedWidth.text()

        self.editing_item.custom_curve = self.cboCustomCurve.currentText()

        if self.new_item:
            self._main_form.add_item(self.new_item)
            self._main_form.mark_project_as_unsaved()
        else:
            if oldname != self.editing_item.name:
                self._main_form.edited_name([(oldname, self.editing_item)])
            changed = any(getattr(self.editing_item, attr) != orig[attr]
                          for attr in orig)
            if changed:
                self._main_form.mark_project_as_unsaved()

        self._main_form.program_settings.setValue("Geometry/frmInlet_geometry", self.saveGeometry())
        self._main_form.program_settings.setValue("Geometry/frmInlet_state", self.saveState())
        self.close()

    def cmdCancel_Clicked(self):
        self.close()
