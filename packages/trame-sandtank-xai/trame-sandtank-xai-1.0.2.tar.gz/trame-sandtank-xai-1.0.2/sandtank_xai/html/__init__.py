from trame.html import AbstractElement
from . import module

from trame.internal.app import get_app_instance

# Activate your Vue library
_app = get_app_instance()
_app.enable_module(module)


class XaiImageOverlay(AbstractElement):
    def __init__(self, **kwargs):
        super().__init__(
            "xai-image-overlay",
            **kwargs,
        )
        self._attr_names += [
            "id",
            "scale",
            "data",
            ("color_map", "dataToColor"),
            "overlay",
            "weights",
            ("pointer_location", "pointerLocation"),
            ("show_ij", "showIJ"),
            "crop",
        ]
        self._event_names += [
            "hover",
            "exit",
            "enter",
        ]


class XaiFullPipeline(AbstractElement):
    def __init__(self, **kwargs):
        super().__init__(
            "xai-full-pipeline",
            **kwargs,
        )
        self._attr_names += [
            "pipeline",
            "labels",
        ]
        self._event_names += ["click"]


class XaiImage(AbstractElement):
    def __init__(self, **kwargs):
        super().__init__(
            "xai-image",
            **kwargs,
        )
        self._attr_names += [
            "config",
            "scale",
            "size",
            "values",
            "convert",
            "rgb",
            "alpha",
        ]
        self._event_names += [
            "exit",
        ]
