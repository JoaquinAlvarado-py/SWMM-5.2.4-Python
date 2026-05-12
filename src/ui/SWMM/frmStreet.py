import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QFrame, QGroupBox
from core.swmm.street import Street


class frmStreet(QMainWindow):
    def __init__(self, main_form, edit_these, new_item):
        QMainWindow.__init__(self, main_form)
        self.help_topic = "swmm/src/src/streeteditor.htm"
        self._main_form = main_form
        self.project = main_form.project
        self.section = self.project.streets
        self.new_item = new_item
        self.editing_item = None

        self.setWindowTitle("Street Cross-Section Editor")
        self.resize(450, 480)
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
                if not isinstance(item, Street):
                    item = self.section.value[item]
                self.editing_item = item
                self.set_from(item)
            else:
                if not isinstance(edit_these, Street):
                    edit_these = self.section.value[edit_these]
                self.editing_item = edit_these
                self.set_from(edit_these)

        if (main_form.program_settings.value("Geometry/frmStreet_geometry") and
                main_form.program_settings.value("Geometry/frmStreet_state")):
            self.restoreGeometry(main_form.program_settings.value(
                "Geometry/frmStreet_geometry", self.geometry(), type=QtCore.QByteArray))
            self.restoreState(main_form.program_settings.value(
                "Geometry/frmStreet_state", self.windowState(), type=QtCore.QByteArray))

    def _setup_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Name row
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.txtName = QLineEdit()
        name_layout.addWidget(self.txtName)
        main_layout.addLayout(name_layout)

        # Road geometry group
        road_group = QGroupBox("Road Geometry")
        road_grid = QGridLayout(road_group)
        row = 0

        self.txtTcrown = QLineEdit()
        road_grid.addWidget(QLabel("Crown Width (ft or m):"), row, 0)
        road_grid.addWidget(self.txtTcrown, row, 1)
        row += 1

        self.txtHcurb = QLineEdit()
        road_grid.addWidget(QLabel("Curb Height (ft or m):"), row, 0)
        road_grid.addWidget(self.txtHcurb, row, 1)
        row += 1

        self.txtSx = QLineEdit()
        road_grid.addWidget(QLabel("Cross Slope (%):"), row, 0)
        road_grid.addWidget(self.txtSx, row, 1)
        row += 1

        self.txtNroad = QLineEdit()
        road_grid.addWidget(QLabel("Manning's n:"), row, 0)
        road_grid.addWidget(self.txtNroad, row, 1)
        row += 1

        self.cboSides = QComboBox()
        self.cboSides.addItems(["1", "2"])
        road_grid.addWidget(QLabel("Number of Sides:"), row, 0)
        road_grid.addWidget(self.cboSides, row, 1)

        main_layout.addWidget(road_group)

        # Gutter group
        gutter_group = QGroupBox("Gutter")
        gutter_grid = QGridLayout(gutter_group)
        row = 0

        self.txtDepression = QLineEdit()
        gutter_grid.addWidget(QLabel("Depression Height (ft or m):"), row, 0)
        gutter_grid.addWidget(self.txtDepression, row, 1)
        row += 1

        self.txtWgutter = QLineEdit()
        gutter_grid.addWidget(QLabel("Gutter Width (ft or m):"), row, 0)
        gutter_grid.addWidget(self.txtWgutter, row, 1)

        main_layout.addWidget(gutter_group)

        # Backing group
        backing_group = QGroupBox("Backing / Sidewalk")
        backing_grid = QGridLayout(backing_group)
        row = 0

        self.txtTback = QLineEdit()
        backing_grid.addWidget(QLabel("Width (ft or m):"), row, 0)
        backing_grid.addWidget(self.txtTback, row, 1)
        row += 1

        self.txtSback = QLineEdit()
        backing_grid.addWidget(QLabel("Slope (%):"), row, 0)
        backing_grid.addWidget(self.txtSback, row, 1)
        row += 1

        self.txtNback = QLineEdit()
        backing_grid.addWidget(QLabel("Manning's n:"), row, 0)
        backing_grid.addWidget(self.txtNback, row, 1)

        main_layout.addWidget(backing_group)

        # Max depth display
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Computed Max. Depth:"))
        self.lblMaxDepth = QLabel("0.0")
        self.lblMaxDepth.setStyleSheet("font-weight: bold;")
        depth_layout.addWidget(self.lblMaxDepth)
        depth_layout.addStretch()
        main_layout.addLayout(depth_layout)

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
        # Update max depth when any geometry field changes
        for txt in (self.txtTcrown, self.txtHcurb, self.txtSx,
                    self.txtDepression, self.txtTback, self.txtSback):
            txt.textChanged.connect(self._update_max_depth)

    def set_from(self, street):
        if not isinstance(street, Street):
            street = self.section.value[street]
        self.editing_item = street
        self.txtName.setText(street.name)
        self.txtTcrown.setText(street.tcrown)
        self.txtHcurb.setText(street.hcurb)
        self.txtSx.setText(street.sx)
        self.txtNroad.setText(street.nroad)
        self.txtDepression.setText(street.a_depression)
        self.txtWgutter.setText(street.w_gutter)
        self.cboSides.setCurrentIndex(0 if street.sides == "1" else 1)
        self.txtTback.setText(street.tback)
        self.txtSback.setText(street.sback)
        self.txtNback.setText(street.nback)
        self._update_max_depth()

    def _update_max_depth(self):
        try:
            ydep = float(self.txtDepression.text() or "0")
            ycurb = float(self.txtHcurb.text() or "0")
            wcrown = float(self.txtTcrown.text() or "0")
            scross = float(self.txtSx.text() or "0")
            wback = float(self.txtTback.text() or "0")
            sback_val = float(self.txtSback.text() or "0")
            d1 = ydep + ycurb + wback * sback_val / 100.0
            d2 = ydep + wcrown * scross / 100.0
            self.lblMaxDepth.setText("{:.4f}".format(max(d1, d2)))
        except ValueError:
            self.lblMaxDepth.setText("---")

    def cmdOK_Clicked(self):
        oldname = self.editing_item.name

        # Save original values for change detection
        orig = {attr: getattr(self.editing_item, attr) for attr in
                ('name', 'tcrown', 'hcurb', 'sx', 'nroad', 'a_depression',
                 'w_gutter', 'sides', 'tback', 'sback', 'nback')}

        # Apply new values
        self.editing_item.name = self.txtName.text()
        self.editing_item.tcrown = self.txtTcrown.text()
        self.editing_item.hcurb = self.txtHcurb.text()
        self.editing_item.sx = self.txtSx.text()
        self.editing_item.nroad = self.txtNroad.text()
        self.editing_item.a_depression = self.txtDepression.text()
        self.editing_item.w_gutter = self.txtWgutter.text()
        self.editing_item.sides = self.cboSides.currentText()
        self.editing_item.tback = self.txtTback.text()
        self.editing_item.sback = self.txtSback.text()
        self.editing_item.nback = self.txtNback.text()

        if self.new_item:
            self._main_form.add_item(self.new_item)
            self._main_form.mark_project_as_unsaved()
        else:
            if oldname != self.editing_item.name:
                self._main_form.edited_name([(oldname, self.editing_item)])
            # Check for any changes
            changed = any(getattr(self.editing_item, attr) != orig[attr]
                          for attr in orig)
            if changed:
                self._main_form.mark_project_as_unsaved()

        self._main_form.program_settings.setValue("Geometry/frmStreet_geometry", self.saveGeometry())
        self._main_form.program_settings.setValue("Geometry/frmStreet_state", self.saveState())
        self.close()

    def cmdCancel_Clicked(self):
        self.close()
