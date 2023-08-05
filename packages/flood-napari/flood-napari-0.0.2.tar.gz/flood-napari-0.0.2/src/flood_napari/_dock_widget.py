"""
Example module of a barebones QWidget plugin for napari.

It implements the ``napari_experimental_provide_dock_widget`` hook
specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs.

The code below was edited to create flood-napari plugin
"""
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QComboBox
from qtpy.QtCore import Signal
from magicgui import magic_factory

'''
Plugin1
'''
# This imports UI file generated from Designer
from qtpy.QtWidgets import QMainWindow
from napari.layers import Image
from qtpy import uic
from pathlib import Path


def flood1(image, delta):
    """
    Create a blue label image by manual threshold of input image.

    Keyword Arguments:
    -----------------
    image -- the image
    delta -- the threshold value (min 0, max 255)

    """
    new_level = delta
    label_image = image <= new_level
    label_image = label_image.astype(int)*13  # label 13 is blue in napari
    return(label_image, new_level)


class ComboBox_with_click_event(QComboBox):
    """Sub-class from QComboBox that emits a signal before popup event."""

    popup_signal = Signal()

    def showPopup(self):
        """Modify showPopup function from QComboBox."""
        self.popup_signal.emit()
        super(ComboBox_with_click_event, self).showPopup()


# Define the main window class
class QtDesignerFlood(QMainWindow):
    """Main window class."""

    def __init__(self, napari_viewer):  # include napari_viewer as argument
        super().__init__()
        self.viewer = napari_viewer
        self.UI_FILE = str(Path(__file__).parent / "flood_tool.ui")  # path to .ui file
        uic.loadUi(self.UI_FILE, self)           # load QtDesigner .ui file
        # Replaces default combobox by combobox with click event
        self.gridLayout.removeWidget(self.comboBox)
        self.comboBox.close()
        self.comboBox = ComboBox_with_click_event(self.centralwidget)
        self.gridLayout.addWidget(self.comboBox, 1, 1, 1, 3)
        self.comboBox.popup_signal.connect(self.update_layer_list)

        self.last_selected = None              # last selected image layer text
        self.update_layer_list()
        self.label_layer = None                # label layer variable

        self.spinBox.valueChanged.connect(self.on_spinbox)
        self.horizontalSlider.valueChanged.connect(self.on_slider)
        self.comboBox.activated.connect(self.on_combobox)

    def on_combobox(self):
        """Callback function from comboBox."""
        # Stores selection text
        self.last_selected = self.comboBox.currentText()
        self.apply_delta()

    def update_layer_list(self):
        """Update layer list with available 2D 8-bit images."""
        self.layer_list_names = []
        self.comboBox.clear()
        for layer in self.viewer.layers:
            if type(layer) == Image:  # Checks if 2D 8-bit image
                if len(layer.data.shape) != 2:
                    continue
                elif layer.data.dtype != 'uint8':
                    continue
                else:
                    self.layer_list_names.append(layer.name)
        if not self.layer_list_names:
            self.comboBox.addItems(['No 2D 8-bit image layer found'])
        else:
            self.comboBox.addItems(self.layer_list_names)
            # Sets the last selection (if it still exists)
            for i in range(self.comboBox.count()):
                if self.last_selected == self.comboBox.itemText(i):
                    self.comboBox.setCurrentIndex(i)

    def apply_delta(self):
        """Create label image."""
        image_layer_name = self.comboBox.currentText()
        label_layer_name = 'flooded_' + image_layer_name
        if image_layer_name != 'No 2D 8-bit image layer found':
            image = self.viewer.layers[image_layer_name].data
            delta = self.spinBox.value()
            label, level = flood1(image, delta)
            if self.label_layer is None:
                self.label_layer = self.viewer.add_labels(
                    label, name=label_layer_name)
            else:
                self.label_layer.data = label
                self.label_layer.name = label_layer_name
                label_layer_idx = self.viewer.layers.index(label_layer_name)
                image_layer_idx = self.viewer.layers.index(image_layer_name)
                if label_layer_idx < image_layer_idx:
                    self.viewer.layers.move(image_layer_idx, label_layer_idx)

    def on_spinbox(self):
        """Callback function from spinBox."""
        self.update_layer_list()
        self.horizontalSlider.setValue(self.spinBox.value())
        self.apply_delta()

    def on_slider(self):
        """Callback function from slider."""
        self.update_layer_list()
        self.spinBox.setValue(self.horizontalSlider.value())
        self.apply_delta()


'''
Plugin2
'''
from napari.types import ImageData, LabelsData


@magic_factory(auto_call=True, delta={'label': 'Gray value (0-255):',
                                      'min': 0,
                                      'max': 255,
                                      'step': 1},
               level={'label': 'Water Level:',
                      'widget_type': 'Slider',
                      'min': 0,
                      'max': 255,
                      'enabled': False})
def magic_factory_flood(image: ImageData, delta: int = 0,
                        level: int = 0) -> LabelsData:
    """
    Create a blue label image by manual threshold of input image.

    Keyword Arguments:
    -----------------
    image -- the image
    delta -- the threshold value (min 0, max 255)
    level -- used to display slider

    """
    new_level = delta
    label_image = image <= new_level
    label_image = label_image.astype(int)*13  # label 13 is blue in napari
    return(label_image)


'''
Plugin3
'''
from magicgui.widgets import FunctionGui
from napari.types import ImageData, LabelsData, LayerDataTuple


def flood3(image: ImageData, delta: int = 0, level: int = 0) -> LayerDataTuple:
    """
    Create a blue label image by manual threshold of input image.

    Keyword Arguments:
    -----------------
    image -- the image
    delta -- the threshold value (min 0, max 255)
    level -- used to display slider

    """
    new_level = delta
    label_image = image <= new_level
    label_image = label_image.astype(int)*13  # label 13 is blue in napari
    return((label_image,
            {'name': 'flood result', 'metadata': {'new_level': new_level}}))


class FunctionGuiFlood(FunctionGui):
    """Sub-class from FunctionGui."""

    def __init__(self):
        super().__init__(
          flood3,
          call_button=False,
          auto_call=True,
          layout='vertical',
          param_options={'delta':
                         {'label': 'Gray value (0-255):',
                          'min': 0,
                          'max': 255,
                          'step': 1},
                         'level':
                             {'label': 'Water Level:',
                              'widget_type': 'Slider',
                              'min': 0,
                              'max': 255}}
        )

    def __call__(self):
        """Modify default __call__ function from FunctionGui."""
        try:
            label_image = super().__call__()
            new_level = round(label_image[1]['metadata']['new_level'])
            self.level.value = new_level
        except TypeError:
            pass


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return [QtDesignerFlood, magic_factory_flood, FunctionGuiFlood]
