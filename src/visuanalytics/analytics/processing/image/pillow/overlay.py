"""
Modul welches die Pillow Image Funktionen zum erstellen und bearbeiten von Bildern beinhaltet.
"""

from PIL import Image

from visuanalytics.analytics.control.procedures.step_data import StepData
from visuanalytics.analytics.processing.image.pillow.draw import DRAW_TYPES
from visuanalytics.analytics.processing.image.wordcloud.wordcloud import WORDCLOUD_TYPES
from visuanalytics.analytics.util import resources
from visuanalytics.analytics.util.step_errors import ImageError
from visuanalytics.analytics.util.step_utils import execute_type_option, execute_type_compare
from visuanalytics.analytics.util.type_utils import register_type_func, get_type_func

OVERLAY_TYPES = {}
"""Ein Dictionary bestehende aus allen Overlay Typ Methoden  """


def register_overlay(func):
    """
    Fügt eine Typ-Funktion dem Dictionary OVERLAY_TYPES hinzu.

    :param func: Eine Funktion
    :return: Die übergebene Funktion
    """
    return register_type_func(OVERLAY_TYPES, ImageError, func)


@register_overlay
def text(overlay: dict, source_img, draw, presets: dict, step_data: StepData):
    """
    Methode um Text auf ein gegebenes Bild zu schreiben mit dem Bauplan der in overlay vorgegeben ist.

    :param overlay: Bauplan des zu schreibenden Overlays
    :param source_img: Bild auf welches geschrieben werden soll
    :param draw: Draw Objekt
    :param presets: Preset Part aus der JSON
    :param step_data: Daten aus der API
    """
    content = step_data.format(overlay["pattern"])
    draw_func = get_type_func(overlay, DRAW_TYPES, "anchor_point")
    draw_func(draw,
              (step_data.format(overlay["pos_x"]), step_data.format(overlay["pos_y"])),
              content,
              step_data.format(presets[overlay["preset"]]["font_size"]),
              step_data.format(presets[overlay["preset"]]["color"]),
              step_data.format(presets[overlay["preset"]]["font"]))


@register_overlay
def text_array(overlay: dict, source_img, draw, presets: dict, step_data: StepData):
    """
    Methode um ein Text-Array auf ein gegebenes Bild zu schreiben mit dem Bauplan der in overlay vorgegeben ist.
    Im Bauplan sind mehrere Texte vorgegeben die auf das Bild geschrieben werden sollen, diese werden ausgepackt
    und umformatiert sodass alle einzelnen overlays nacheinander an die Funktion text übergeben werden.

    :param overlay: Bauplan des zu schreibenden Overlays
    :param source_img: Bild auf welches geschrieben werden soll
    :param draw: Draw Objekt
    :param presets: Preset Part aus der JSON
    :param step_data: Daten aus der API
    """
    for idx, i in enumerate(overlay["pos_x"]):
        if isinstance(overlay["preset"], list):
            preset = overlay["preset"][idx]
        else:
            preset = overlay["preset"]
        if isinstance(overlay["pattern"], list):
            pattern = overlay["pattern"][idx]
        else:
            pattern = overlay["pattern"]
        new_overlay = {
            "anchor_point": overlay["anchor_point"],
            "pos_x": overlay["pos_x"][idx],
            "pos_y": overlay["pos_y"][idx],
            "pattern": pattern,
            "preset": preset}
        text(new_overlay, source_img, draw, presets, step_data)


@register_overlay
def option(values: dict, source_img, draw, presets: dict, step_data: StepData):
    """
    Methode welche 2 verschiedene Baupläne bekommt was auf ein Bild geschrieben werden soll, dazu
    wird ein boolean Wert in der Step_data ausgewertet und je nachdem ob dieser Wert
    true oder false ist wird entweder Bauplan A oder Bauplan B ausgeführt.

    :param values: Baupläne des zu schreibenden Overlays
    :param source_img: Bild auf welches geschrieben werden soll
    :param draw: Draw Objekt
    :param presets: Preset Part aus der JSON
    :param step_data: Daten aus der API
    """
    chosen_text = execute_type_option(values, step_data)

    for overlay in chosen_text:
        over_func = get_type_func(overlay, OVERLAY_TYPES)
        over_func(overlay, source_img, draw, presets, step_data)


@register_overlay
def compare(values: dict, source_img, draw, presets: dict, step_data: StepData):
    """
    Methode welche 2 verschiedene Baupläne bekommt was auf ein Bild geschrieben werden soll, dazu
    wird ein boolean Wert in der Step_data ausgewertet und je nachdem ob dieser Wert
    true oder false ist wird entweder Bauplan A oder Bauplan B ausgeführt.

    :param values: Baupläne des zu schreibenden Overlays
    :param source_img: Bild auf welches geschrieben werden soll
    :param draw: Draw Objekt
    :param presets: Preset Part aus der JSON
    :param step_data: Daten aus der API
    """
    chosen_text = execute_type_compare(values, step_data)

    for overlay in chosen_text:
        over_func = get_type_func(overlay, OVERLAY_TYPES)
        over_func(overlay, source_img, draw, presets, step_data)


@register_overlay
def image(overlay: dict, source_img, draw, presets: dict, step_data: StepData):
    """
    Methode um ein Bild in das source_img einzufügen mit dem Bauplan der in overlay vorgegeben ist.

    :param overlay: Bauplan des zu schreibenden Overlays
    :param source_img: Bild auf welches das Bild eingefügt werden soll
    :param draw: Draw Objekt
    :param presets: Preset Part aus der JSON
    :param step_data: Daten aus der API
    """
    path = step_data.format(overlay["path"])
    icon = Image.open(
        resources.get_image_path(path)).convert("RGBA")
    if step_data.format(overlay.get("color", "RGBA")) != "RGBA":
        icon = icon.convert(step_data.format(overlay["color"]))
    if overlay.get("size_x", None) is not None and overlay.get("size_y", None) is not None:
        icon = icon.resize([step_data.format(overlay["size_x"]),
                            step_data.format(overlay["size_y"])], Image.LANCZOS)
    if overlay.get("transparency", False):
        source_img.alpha_composite(icon, (step_data.format(overlay["pos_x"]),
                                          step_data.format(overlay["pos_y"])))
    else:
        source_img.paste(icon, (step_data.format(overlay["pos_x"]),
                                step_data.format(overlay["pos_y"])), icon)


@register_overlay
def image_array(overlay: dict, source_img, draw, presets: dict, step_data: StepData):
    """
    Methode um ein Bild-Array in das source_img einzufügen mit dem Bauplan der in overlay vorgegeben ist.
    Im Bauplan sind mehrere Bilder vorgegeben die auf das Bild gesetzt werden sollen, diese werden ausgepackt
    und umformatiert sodass alle einzelnen Bilder nacheinander an die Funktion image übergeben werden


    :param overlay: Bauplan des zu schreibenden Overlays
    :param source_img: Bild auf welches das Bild eingefügt werden soll
    :param draw: Draw Objekt
    :param presets: Preset Part aus der JSON
    :param step_data: Daten aus der API
    """
    for idx, i in enumerate(overlay["pos_x"]):
        if isinstance(overlay["color"], list):
            color = overlay["color"][idx]
        else:
            color = overlay["color"]
        if isinstance(overlay["path"], list):
            path = overlay["path"][idx]
        else:
            path = overlay["path"]
        new_overlay = {
            "size_x": overlay.get("size_x", None),
            "size_y": overlay.get("size_y", None),
            "pos_x": overlay["pos_x"][idx],
            "pos_y": overlay["pos_y"][idx],
            "transparency": overlay.get("transparency", False),
            "path": path,
            "color": color}
        image(new_overlay, source_img, draw, presets, step_data)


@register_overlay
def wordcloud(overlay: dict, source_img, draw, presets: dict, step_data: StepData):
    """
    Erstellt ein Wordcloud Bild.

    :param values: Image Bauplan des zu erstellenden Bildes
    :param prev_paths: Alle Image Baupläne und somit auch alle Pfade zu den bisher erstellen Bildern
    :param presets: Preset Part aus der JSON
    :param step_data: Daten aus der API
    :return: Den Pfad zum erstellten Bild
    :rtype: str
    """

    word_func = get_type_func(overlay, WORDCLOUD_TYPES)
    file = word_func(overlay, source_img, draw, presets, step_data)

    return file
