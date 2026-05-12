import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractItemView
from ui.SWMM.frmProfilePlotDesigner import Ui_frmProfilePlot
from ui.help import HelpHandler
import core.swmm.hydraulics.node


class frmProfilePlot(QMainWindow, Ui_frmProfilePlot):
    MAGIC = "SWMM_PROFILE_GRAPH_SPEC:\n"

    def __init__(self, main_form):
        QMainWindow.__init__(self, main_form)
        self.helper = HelpHandler(self)
        self.help_topic = "swmm/src/src/profileplotoptionsdialog.htm"
        self._main_form = main_form
        self.setupUi(self)
        self.cmdFind.setEnabled(False)  # TODO: Enable when functionality is ready
        self.cmdSave.setText("Copy")
        self.cmdUse.setText("Paste")
        self.cmdSave.clicked.connect(self.cmdSave_Clicked)
        self.cmdUse.clicked.connect(self.cmdUse_Clicked)
        self.cmdOK.clicked.connect(self.cmdOK_Clicked)
        self.cmdCancel.clicked.connect(self.cmdCancel_Clicked)
        self.cmdFind.clicked.connect(self.cmdFind_Clicked)
        self.InDirectionOfFlow = True

    def set_from(self, project, output):
        self.project = project
        self.output = output
        self.cboStart.clear()
        self.cboEnd.clear()
        if project and self.output:
            for node_name in self.output.nodes:
                self.cboStart.addItem(node_name)
                self.cboEnd.addItem(node_name)
                self.cmdFind.setEnabled(True)
            #for link_name in self.output.links:
            #    self.lstData.addItem(link_name)

    def get_text(self):
        return self.MAGIC + '\n'.join([str(self.lstData.item(i).text()) for i in range(self.lstData.count())])

    def set_from_text(self, text):
        if text.startswith(self.MAGIC):
            self.lstData.clear()
            for line in text[len(self.MAGIC):].split('\n'):
                self.lstData.addItem(line)

    def cmdFind_Clicked(self):
        self.lstData.clear()
        start_node = str(self.cboStart.currentText())
        end_node = str(self.cboEnd.currentText())
        self.InDirectionOfFlow = True

        current_node = start_node
        counter = 0
        while current_node != end_node and counter < 1000:
            counter += 1
            for link_group in self.project.links_groups():
                if link_group and link_group.value:
                    for link in link_group.value:
                        if link.inlet_node == current_node and current_node != end_node:
                            self.lstData.addItem(link.name)
                            current_node = link.outlet_node

        if self.lstData.count() == 0:
            # try the reverse order
            self.InDirectionOfFlow = False
            # start_node = str(self.cboEnd.currentText())
            # end_node = str(self.cboStart.currentText())

            current_node = start_node
            counter = 0
            while current_node != end_node and counter < 1000:
                counter += 1
                for link_group in self.project.links_groups():
                    if link_group and link_group.value:
                        for link in link_group.value:
                            if link.outlet_node == current_node and current_node != end_node:
                                self.lstData.addItem(link.name)
                                current_node = link.inlet_node
            # if self.lstData.count() > 0:
            #     # reverse the order
            #     temp_order = []
            #     for index in range(0, self.lstData.count()):
            #         temp_order.append(self.lstData.item(index).text())
            #     temp_order.reverse()
            #     self.lstData.clear()
            #     for item in temp_order:
            #         self.lstData.addItem(item)

    def cmdSave_Clicked(self):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.get_text(), mode=cb.Clipboard)

    def cmdUse_Clicked(self):
        try:
            self.set_from_text(QApplication.clipboard().text())
        except Exception as ex:
            print(str(ex))
            self.lstData.clear()

    def cmdCancel_Clicked(self):
        self.close()

    def cmdOK_Clicked(self):
        # Profile plot based on 'Basic HGL 2-D Video Profile Plot Script by Bryant E. McDonnell'

        if self.lstData.count() == 0:
            return

        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
        import numpy as np
        from scipy.interpolate import interp1d

        # Show Plot 1 = SHOW; 2 = Save Video Plot; 3 = Export HTML
        fig_output = 1

        # Pass Ordered Links
        self.lstData.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lstData.selectAll()
        LKsToPlot = []
        for selected_item in self.lstData.selectedItems():
            LKsToPlot.append(str(selected_item.text()))

        # #pass Appendix (If desired, else set to [])
        LKsToPlotAppendix = []

        appendpltdir = -1 # Appendix direction: can be -1 for left and 1 for right

        # Manhole radius removed - manholes drawn as vertical lines (official SWMM style)

        # Input file Hydraulic Data
        # Conduit ID,  US Node, DS,    Len, Diameter, US offset, DS offset
        start_node = ''
        end_node = ''
        LKsToPlotData = {}
        MaxDepthData = {}
        for link_name in LKsToPlot:
            try:
                link = self.project.find_link(link_name)
                if self.InDirectionOfFlow:
                    nodes = (link.inlet_node, link.outlet_node)
                else:
                    nodes = (link.outlet_node, link.inlet_node)
                diameter = 0
                for cross_section in self.project.xsections.value:
                    if cross_section.link == link_name:
                        diameter = cross_section.geometry1
                        MaxDepthData[link.inlet_node] = cross_section.geometry1
                        MaxDepthData[link.outlet_node] = cross_section.geometry1
                length = 10
                if isinstance(link,core.swmm.hydraulics.link.Conduit):
                    length = float(link.length)
                inlet_offset = 10
                if isinstance(link,core.swmm.hydraulics.link.Conduit):
                    inlet_offset = link.inlet_offset
                outlet_offset = 10
                if isinstance(link,core.swmm.hydraulics.link.Conduit):
                    outlet_offset = link.outlet_offset
                LKsToPlotData[link_name] = [nodes, length, diameter, inlet_offset, outlet_offset]
                # this is also a convenient place to record the start and end nodes for use in the title
                if self.InDirectionOfFlow:
                    if len(start_node) == 0:
                        start_node = link.inlet_node
                    end_node = link.outlet_node
                else:
                    if len(start_node) == 0:
                        start_node = link.outlet_node
                    end_node = link.inlet_node
            except:
                pass  # probably did not find link in this group, move on to the next group

        NodeInverts = {}
        NodeDepths = {}
        for node_group in self.project.nodes_groups():
            if node_group and node_group.value:
                for node in node_group.value:
                    elevation = 0
                    depth = 0
                    if node.elevation:
                        elevation = node.elevation
                    if isinstance(node, core.swmm.hydraulics.node.Outfall):
                        # try to get from conduit max depth
                        if node.name in MaxDepthData:
                            depth = MaxDepthData[node.name]
                    elif isinstance(node,core.swmm.hydraulics.node.Junction):
                        depth = node.max_depth

                    NodeInverts[node.name] = elevation
                    NodeDepths[node.name] = depth

        # Build ordered node list
        MHList = []
        for ind, ID in enumerate(LKsToPlot):
            if ind == 0:
                MHList.append(LKsToPlotData[ID][0][0])
            MHList.append(LKsToPlotData[ID][0][1])

        # Compute cumulative x-distances (center of each node)
        node_x_center = np.zeros(len(MHList))
        for ind, ID in enumerate(LKsToPlot):
            node_x_center[ind + 1] = node_x_center[ind] + float(LKsToPlotData[ID][1])

        # Junction box half-width (proportional to total distance)
        total_dist = node_x_center[-1] - node_x_center[0]
        mh_hw = max(total_dist * 0.008, 0.3)  # half-width
        node_x_left = node_x_center - mh_hw
        node_x_right = node_x_center + mh_hw

        # Node elevations
        node_invert = np.array([float(NodeInverts[n]) for n in MHList])
        node_ground = np.array([float(NodeInverts[n]) + float(NodeDepths[n]) for n in MHList])

        # Check if offsets are depths (added to node invert) or elevations (absolute)
        from core.swmm.options.general import LinkOffsets
        offsets_are_depth = (self.project.options.link_offsets == LinkOffsets.DEPTH)

        # Build pipe geometry for each link
        # Pipes connect from right wall of upstream node to left wall of downstream node
        pipe_x = []
        pipe_inv = []
        pipe_crown = []
        for ind, ID in enumerate(LKsToPlot):
            x_up = node_x_right[ind]
            x_down = node_x_left[ind + 1]
            offset_up = float(LKsToPlotData[ID][3])
            offset_down = float(LKsToPlotData[ID][4])
            if offsets_are_depth:
                inv_up = float(NodeInverts[LKsToPlotData[ID][0][0]]) + offset_up
                inv_down = float(NodeInverts[LKsToPlotData[ID][0][1]]) + offset_down
            else:
                inv_up = offset_up
                inv_down = offset_down
            diameter = float(LKsToPlotData[ID][2])
            pipe_x.append([x_up, x_down])
            pipe_inv.append([inv_up, inv_down])
            pipe_crown.append([inv_up + diameter, inv_down + diameter])

        # Read Model output Data
        OutputObject = self.output
        NPeriods = OutputObject.num_periods
        RESULTMATRIX = np.zeros((len(MHList), NPeriods))
        for ind, ID in enumerate(MHList):
            node = OutputObject.nodes[ID]
            RESULTMATRIX[ind, :] = node.get_series(OutputObject, node.attribute_head)

        # --- Create figure (official SWMM style) ---
        length_unit = "m" if OutputObject.unit_system == 1 else "ft"
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_title('Water Elevation Profile: Node ' + start_node + ' - ' + end_node)
        ax.set_xlabel("Distance (" + length_unit + ")")
        ax.set_ylabel("Elevation (" + length_unit + ")")
        ax.grid(True, alpha=0.3)
        fig.canvas.setWindowTitle('Profile: Node ' + start_node + ' - ' + end_node)

        # Draw pipe invert and crown lines (between junction walls)
        for i in range(len(LKsToPlot)):
            ax.plot(pipe_x[i], pipe_inv[i], '-k', linewidth=1)
            ax.plot(pipe_x[i], pipe_crown[i], '-k', linewidth=1)

        # Draw junction boxes and pipe-to-junction connections
        for i, name in enumerate(MHList):
            xl = node_x_left[i]
            xr = node_x_right[i]
            inv = node_invert[i]
            grnd = node_ground[i]

            # Junction box: left wall, right wall, top, bottom
            ax.plot([xl, xl], [inv, grnd], '-k', linewidth=1)
            ax.plot([xr, xr], [inv, grnd], '-k', linewidth=1)
            ax.plot([xl, xr], [grnd, grnd], '-k', linewidth=1)
            ax.plot([xl, xr], [inv, inv], '-k', linewidth=1)

            # Vertical connections inside junction: pipe crown/invert to junction walls
            # Left side: connect incoming pipe (if not first node)
            if i > 0:
                p_inv_down = pipe_inv[i - 1][1]
                p_crown_down = pipe_crown[i - 1][1]
                ax.plot([xl, xl], [inv, p_inv_down], '-k', linewidth=1)
                ax.plot([xl, xl], [p_crown_down, grnd], '-k', linewidth=1)
            # Right side: connect outgoing pipe (if not last node)
            if i < len(MHList) - 1:
                p_inv_up = pipe_inv[i][0]
                p_crown_up = pipe_crown[i][0]
                ax.plot([xr, xr], [inv, p_inv_up], '-k', linewidth=1)
                ax.plot([xr, xr], [p_crown_up, grnd], '-k', linewidth=1)

            # Node label at top
            ax.text(node_x_center[i], grnd, '  ' + name,
                    ha='left', va='bottom', fontsize=9, rotation=90)

        # Ground level (interpolated green line)
        if len(node_x_center) > 1:
            # Use left/right edges for ground interpolation
            gx = []
            gy = []
            for i in range(len(MHList)):
                gx.extend([node_x_left[i], node_x_right[i]])
                gy.extend([node_ground[i], node_ground[i]])
            gx = np.array(gx)
            gy = np.array(gy)
            func = interp1d(gx, gy, kind='linear')
            xinterp = np.linspace(gx[0], gx[-1], 300)
            ax.plot(xinterp, func(xinterp), 'g-', linewidth=1)

        # Compute axis limits - zoom to infrastructure elevation range
        all_elevs = list(node_invert) + list(node_ground)
        for pair in pipe_inv:
            all_elevs.extend(pair)
        for pair in pipe_crown:
            all_elevs.extend(pair)
        y_min = min(all_elevs)
        y_max = max(all_elevs)
        y_margin = max((y_max - y_min) * 0.15, 0.5)
        x_range = node_x_center[-1] - node_x_center[0]
        ax.set_xlim(node_x_center[0] - x_range * 0.02 - mh_hw,
                     node_x_center[-1] + x_range * 0.02 + mh_hw)
        ax.set_ylim(y_min - y_margin, y_max + y_margin)

        # HGL animated line
        line, = ax.plot([], [], lw=2, c='b', label='HGL f(t)')
        tex = ax.text(node_x_center[-1], y_min, '', color='r', fontsize=10, ha='right')
        ax.legend(loc=4)

        def build_hgl(hgl_values):
            """Build HGL x,y arrays that follow junction walls and respect pipe inverts."""
            hx, hy = [], []
            n = len(MHList)
            for i in range(n):
                h = hgl_values[i]
                # Left wall of junction
                if i > 0:
                    hx.append(node_x_left[i])
                    hy.append(max(h, pipe_inv[i - 1][1]))
                else:
                    hx.append(node_x_left[i])
                    hy.append(h)
                # Right wall of junction
                if i < n - 1:
                    hx.append(node_x_right[i])
                    hy.append(max(h, pipe_inv[i][0]))
                else:
                    hx.append(node_x_right[i])
                    hy.append(h)
            return hx, hy

        # Make room for controls at bottom
        plt.subplots_adjust(bottom=0.20)

        # --- Playback state ---
        state = {'frame': 0, 'playing': False, 'ani': None}

        def update_frame(frame_idx):
            frame_idx = max(0, min(frame_idx, NPeriods - 1))
            state['frame'] = frame_idx
            hx, hy = build_hgl(RESULTMATRIX[:, frame_idx])
            line.set_data(hx, hy)
            tex.set_text("Interval " + str(frame_idx))
            slider.set_val(frame_idx)
            fig.canvas.draw_idle()

        # --- Slider ---
        from matplotlib.widgets import Slider, Button
        ax_slider = plt.axes([0.15, 0.06, 0.55, 0.03])
        slider = Slider(ax_slider, 'Time', 0, NPeriods - 1, valinit=0, valstep=1, valfmt='%d')

        def on_slider(val):
            idx = int(val)
            if idx != state['frame']:
                state['frame'] = idx
                hx, hy = build_hgl(RESULTMATRIX[:, idx])
                line.set_data(hx, hy)
                tex.set_text("Interval " + str(idx))
                fig.canvas.draw_idle()
        slider.on_changed(on_slider)

        # --- Buttons ---
        ax_prev = plt.axes([0.75, 0.06, 0.05, 0.03])
        ax_play = plt.axes([0.81, 0.06, 0.07, 0.03])
        ax_next = plt.axes([0.89, 0.06, 0.05, 0.03])
        btn_prev = Button(ax_prev, '<<')
        btn_play = Button(ax_play, 'Play')
        btn_next = Button(ax_next, '>>')

        def on_prev(event):
            if state['playing']:
                toggle_play(None)
            update_frame(state['frame'] - 1)

        def on_next(event):
            if state['playing']:
                toggle_play(None)
            update_frame(state['frame'] + 1)

        def anim_step(frame_idx):
            state['frame'] = frame_idx
            hx, hy = build_hgl(RESULTMATRIX[:, frame_idx])
            line.set_data(hx, hy)
            tex.set_text("Interval " + str(frame_idx))
            slider.set_val(frame_idx)
            return line, tex

        def anim_frames():
            while state['playing']:
                state['frame'] += 1
                if state['frame'] >= NPeriods:
                    state['frame'] = 0
                yield state['frame']

        def toggle_play(event):
            if state['playing']:
                state['playing'] = False
                if state['ani'] is not None:
                    state['ani'].event_source.stop()
                    state['ani'] = None
                btn_play.label.set_text('Play')
            else:
                state['playing'] = True
                btn_play.label.set_text('Pause')
                state['ani'] = animation.FuncAnimation(
                    fig, anim_step, anim_frames, interval=100,
                    save_count=NPeriods, blit=False, repeat=False)
                fig.canvas.draw_idle()

        btn_prev.on_clicked(on_prev)
        btn_play.on_clicked(toggle_play)
        btn_next.on_clicked(on_next)

        # Show initial frame
        update_frame(0)

        fig.show()
        fig.canvas.draw()

        self.close()

