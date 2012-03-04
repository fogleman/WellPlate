wxPython Well Plate Dialog
--------------------------

This module provides a simple dialog that allows the user to configure a
well plate by specifying a "type" for each well. The default types are:

- Empty
- Blank
- Calibrant
- Sample

The user selection can be returned in a variety of ways, including well names
or row- or column-major indexes for each type.

The dialog is reasonably configurable:

- Number of rows and columns (96 or 384 well plate, or any other size)
- Selectable types: labels and colors
- Font sizes for row and column header labels
- Whether or not to show labels and well labels

Sample code:

    model = plate.PlateModel(8, 12)
    dialog = plate.PlateDialog(model)
    if dialog.ShowModal() == wx.ID_OK:
        for row in range(model.rows):
            for col in range(model.cols):
                key = model.grid[row][col]
                if key == plate.SAMPLE:
                    # do something
    dialog.Destroy()

Screenshot:

![](https://raw.github.com/fogleman/WellPlate/master/screenshot.png)
