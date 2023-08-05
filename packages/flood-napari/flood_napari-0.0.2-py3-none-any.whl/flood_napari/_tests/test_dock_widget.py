import flood_napari
import pytest
import numpy as np

# this is your plugin name declared in your napari.plugins entry point
MY_PLUGIN_NAME = "flood-napari"
# the name of your widget(s)
MY_WIDGET_NAMES = ["Qt Designer Flood", "magic_factory_flood", "Function Gui Flood"]


@pytest.mark.parametrize("widget_name", MY_WIDGET_NAMES)
def test_something_with_viewer(widget_name, make_napari_viewer, napari_plugin_manager):
    napari_plugin_manager.register(flood_napari, name=MY_PLUGIN_NAME)
    viewer = make_napari_viewer()
    num_dw = len(viewer.window._dock_widgets)
    viewer.window.add_plugin_dock_widget(
        plugin_name=MY_PLUGIN_NAME, widget_name=widget_name
    )
    assert len(viewer.window._dock_widgets) == num_dw + 1


image2D_8bit = np.arange(9).reshape(3,3).astype('uint8')
value = [4, 4, 4]
expected_output = np.array([[13, 13, 13],
                            [13, 13, 0],
                            [0, 0, 0]])

@pytest.mark.parametrize("widget_name, value", zip(MY_WIDGET_NAMES, value))
def test_flood_image(widget_name, make_napari_viewer, value, napari_plugin_manager):
    napari_plugin_manager.register(flood_napari, name=MY_PLUGIN_NAME)
    viewer = make_napari_viewer()
    dw, wdg = viewer.window.add_plugin_dock_widget(
        plugin_name=MY_PLUGIN_NAME, widget_name=widget_name
    )
    viewer.add_image(image2D_8bit)
    if widget_name=="Qt Designer Flood":
        wdg.spinBox.setValue(value)
    else:
        wdg.delta.value = value
    label_img = viewer.layers[1].data
    assert np.array_equal(label_img, expected_output)



