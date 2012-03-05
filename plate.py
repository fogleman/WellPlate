import wx

EMPTY = 0
BLANK = 1
CALIBRANT = 2
SAMPLE = 3

class PlateModel(object):
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.padding = 10
        self.show_labels = True
        self.show_well_labels = True
        self.show_legend = False
        self.labels = {
            EMPTY: 'Empty',
            BLANK: 'Blank',
            CALIBRANT: 'Calibrant',
            SAMPLE: 'Sample',
        }
        self.colors = {
            EMPTY: (255, 255, 255),
            BLANK: (102, 102, 255),
            CALIBRANT: (51, 204, 51),
            SAMPLE: (204, 51, 51),
        }
        self.active_key = SAMPLE
        self.grid = [[EMPTY] * self.cols for _ in range(self.rows)]
    def select(self, row, col):
        self.grid[row][col] = self.active_key
    def toggle(self, row, col):
        if self.grid[row][col] == self.active_key:
            self.grid[row][col] = EMPTY
        else:
            self.grid[row][col] = self.active_key
    def select_all(self):
        self.grid = [[self.active_key] * self.cols for _ in range(self.rows)]
    def select_none(self):
        self.grid = [[EMPTY] * self.cols for _ in range(self.rows)]
    def check_cell(self, row, col, key):
        if key is None:
            return self.grid[row][col]
        else:
            return self.grid[row][col] == key
    def get_col_major_indexes(self, key=None):
        result = []
        index = 1
        for col in range(self.cols):
            for row in range(self.rows):
                if self.check_cell(row, col, key):
                    result.append(index)
                index += 1
        return result
    def get_row_major_indexes(self, key=None):
        result = []
        index = 1
        for row in range(self.rows):
            for col in range(self.cols):
                if self.check_cell(row, col, key):
                    result.append(index)
                index += 1
        return result
    def get_names(self, key=None):
        result = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.check_cell(row, col, key):
                    name = '%s%02d' % (chr(ord('A') + row), col + 1)
                    result.append(name)
        return result

class PlatePanel(wx.Panel):
    def __init__(self, model, *args, **kwargs):
        super(PlatePanel, self).__init__(*args, **kwargs)
        self.model = model
        self.coords = {}
        self.size = 0
        self.box = None
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_left_dclick)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.on_mouse_capture_lost)
        self.SetMinSize((model.cols * 24, model.rows * 24))
    def on_size(self, event):
        event.Skip()
        self.Refresh()
    def hit_test(self, mx, my):
        size = self.size / 2
        for (row, col), (x, y) in self.coords.iteritems():
            d = ((x - mx) ** 2 + (y - my) ** 2) ** 0.5
            if d < size:
                return (row, col)
        return None
    def box_test(self, x1, y1, x2, y2):
        result = []
        size = self.size / 2 - 1
        x1, x2 = min(x1, x2) + size, max(x1, x2) - size
        y1, y2 = min(y1, y2) + size, max(y1, y2) - size
        for (row, col), (x, y) in self.coords.iteritems():
            if x > x1 and x < x2 and y > y1 and y < y2:
                result.append((row, col))
        return result
    def on_mouse_capture_lost(self, event):
        self.box = None
        self.Refresh()
    def on_left_dclick(self, event):
        self.on_left_down(event)
    def on_left_down(self, event):
        self.CaptureMouse()
        x, y = event.GetPosition()
        self.box = (x, y, x, y)
        self.Refresh()
    def on_left_up(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        if self.box:
            a, b, _, _ = self.box
            c, d = event.GetPosition()
            e = 3
            if abs(a - c) < e and abs(b - d) < e:
                coord = self.hit_test(a, b)
                if coord is not None:
                    row, col = coord
                    self.model.toggle(row, col)
            else:
                for row, col in self.box_test(a, b, c, d):
                    self.model.select(row, col)
            self.box = None
            self.Refresh()
    def on_motion(self, event):
        if self.box:
            a, b, _, _ = self.box
            c, d = event.GetPosition()
            self.box = (a, b, c, d)
            self.Refresh()
    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.Clear()
        dc = wx.GCDC(dc)
        self.draw(dc)
    def draw(self, dc):
        self.draw_plate(dc)
        self.draw_box(dc)
    def draw_box(self, dc):
        if not self.box:
            return
        x1, y1, x2, y2 = self.box
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 32)))
        dc.SetPen(wx.BLACK_PEN)
        dc.DrawRectangle(x1, y1, x2 - x1, y2 - y1)
    def draw_plate(self, dc):
        model = self.model
        w, h = self.GetClientSize()
        padding = min(w, h) / 36
        margin = min(w, h) / 8
        pw, ph = w - margin * 2 - padding * 2, h - margin * 2 - padding * 2
        self.size = size = min(pw / model.cols, ph / model.rows)
        dw, dh = size * model.cols, size * model.rows
        dx, dy = (w - dw) / 2, (h - dh) / 2
        dc.SetPen(wx.Pen(wx.BLACK, 4))
        dc.SetBrush(wx.Brush(wx.Colour(235, 235, 235)))
        dc.DrawRectangle(dx - padding, dy - padding, 
            dw + padding * 2, dh + padding * 2)
        font = dc.GetFont()
        font.SetPointSize(size / 4)
        dc.SetFont(font)
        box = set(self.box_test(*self.box)) if self.box else set()
        dc.SetPen(wx.Pen(wx.BLACK, 2))
        for row in range(model.rows):
            for col in range(model.cols):
                x = dx + col * size + size / 2
                y = dy + row * size + size / 2
                self.coords[(row, col)] = (x, y)
                if (row, col) in box:
                    key = model.active_key
                else:
                    key = model.grid[row][col]
                if key:
                    dc.SetTextForeground(wx.Colour(0, 0, 0))
                else:
                    dc.SetTextForeground(wx.Colour(64, 64, 64))
                dc.SetBrush(wx.Brush(wx.Colour(*model.colors[key])))
                dc.DrawCircle(x, y, size / 2 - size / 12)
                if model.show_well_labels:
                    if key == EMPTY:
                        label = '%s%d' % (chr(ord('A') + row), col + 1)
                    else:
                        label = model.labels[key][0]
                    tw, th = dc.GetTextExtent(label)
                    dc.DrawText(label, x - tw / 2, y - th / 2)
        if model.show_labels:
            font = dc.GetFont()
            font.SetPointSize(size / 2)
            dc.SetFont(font)
            dc.SetTextForeground(wx.BLACK)
            for row in range(model.rows):
                y = dy + row * size + size / 2
                x = dx - padding * 2 - size / 4
                label = chr(ord('A') + row)
                tw, th = dc.GetTextExtent(label)
                dc.DrawText(label, x - tw / 2, y - th / 2)
            for col in range(model.cols):
                x = dx + col * size + size / 2
                y = dy - padding * 2 - size / 4
                label = str(col + 1)
                tw, th = dc.GetTextExtent(label)
                dc.DrawText(label, x - tw / 2, y - th / 2)
        if model.show_legend:
            x = dx - padding
            y = dy + dh + padding * 2
            w = dw + padding * 2
            h = margin - padding * 2
            w = w / len(model.labels)
            dc.SetPen(wx.Pen(wx.BLACK, 2))
            font = dc.GetFont()
            font.SetPointSize(h * 3 / 7)
            dc.SetFont(font)
            for key in sorted(model.labels):
                label = model.labels[key]
                dc.SetBrush(wx.Brush(wx.Colour(*model.colors[key])))
                dc.DrawRoundedRectangle(x + padding / 2, y, 
                    w - padding, h, padding / 2)
                tw, th = dc.GetTextExtent(label)
                dc.DrawText(label, x + w / 2 - tw / 2, y + h / 2 - th / 2)
                x += w + 1

class PlateDialog(wx.Dialog):
    def __init__(self, model, parent=None):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX
        super(PlateDialog, self).__init__(parent, style=style)
        self.model = model
        self.SetTitle('Select Wells')
        sizer = self.create_controls(self)
        self.SetSizerAndFit(sizer)
    def create_controls(self, parent):
        padding = 12
        panel = PlatePanel(self.model, parent, style=wx.BORDER_SUNKEN)
        labels = self.create_labels(parent)
        line = wx.StaticLine(parent)
        buttons = self.create_buttons(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND | wx.ALL, padding)
        sizer.Add(labels, 0, wx.ALL & ~wx.TOP, padding)
        sizer.Add(line, 0, wx.EXPAND)
        sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, padding)
        return sizer
    def create_labels(self, parent):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for key in self.model.labels:
            label = self.model.labels[key]
            button = wx.RadioButton(parent, -1, label)
            button.key = key
            button.Bind(wx.EVT_RADIOBUTTON, self.on_radio_button)
            if key == self.model.active_key:
                button.SetValue(True)
            sizer.Add(button)
            sizer.AddSpacer(8)
        return sizer
    def create_buttons(self, parent):
        select_all = wx.Button(parent, -1, 'Select All')
        select_all.Bind(wx.EVT_BUTTON, self.on_select_all)
        select_none = wx.Button(parent, -1, 'Select None')
        select_none.Bind(wx.EVT_BUTTON, self.on_select_none)
        ok = wx.Button(parent, wx.ID_OK, 'OK')
        ok.SetDefault()
        cancel = wx.Button(parent, wx.ID_CANCEL, 'Cancel')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(select_all)
        sizer.AddSpacer(8)
        sizer.Add(select_none)
        sizer.AddSpacer(8)
        sizer.AddStretchSpacer(1)
        sizer.Add(ok)
        sizer.AddSpacer(8)
        sizer.Add(cancel)
        return sizer
    def on_radio_button(self, event):
        self.model.active_key = event.GetEventObject().key
    def on_select_all(self, event):
        self.model.select_all()
        self.Refresh()
    def on_select_none(self, event):
        self.model.select_none()
        self.Refresh()

def main():
    app = wx.PySimpleApp()
    model = PlateModel(8, 12) # 96
    #model = PlateModel(16, 24) # 384
    #model.show_well_labels = False
    dialog = PlateDialog(model)
    dialog.SetSize((800, 700))
    dialog.Center()
    if dialog.ShowModal() == wx.ID_OK:
        for key, label in model.labels.iteritems():
            print '%s (Column Major):' % label, model.get_col_major_indexes(key)
            print '%s (Row Major):' % label, model.get_row_major_indexes(key)
            print '%s (Names):' % label, model.get_names(key)
        for row in range(model.rows):
            for col in range(model.cols):
                key = model.grid[row][col]
                print model.labels[key][0],
            print
    dialog.Destroy()
    app.MainLoop()

if __name__ == '__main__':
    main()
