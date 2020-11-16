import io

import logging
import os
import time
from typing import List

from collections import OrderedDict
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.template import _ENVIRONMENT
from homeassistant.util.yaml import loader as hass_loader
from homeassistant.components.lovelace import dashboard

from .const import (
    DATA_DEFAULT_LANGUAGE,
    DOMAIN,
    TRANSLATIONS_PATH,
    JINJA_VARIABLE_TRANSLATE,
    JINJA_VARIABLE_USER_ID,
)

_LOGGER = logging.getLogger(__name__)


async def setup_yaml_parser(hass):
    def load_translations(language=None):
        # Always load the default language
        translations = parse_yaml(
            os.path.join(
                os.path.dirname(__file__),
                TRANSLATIONS_PATH + DATA_DEFAULT_LANGUAGE + ".yaml",
            ),
            skip_translations=True,
        )

        # Update with the selected language which allows for incomplete translations.
        if language is not None and language != DATA_DEFAULT_LANGUAGE:
            try:
                translations.update(
                    parse_yaml(
                        os.path.join(
                            os.path.dirname(__file__),
                            TRANSLATIONS_PATH + language + ".yaml",
                        ),
                        skip_translations=True,
                    )
                )
            except:
                _LOGGER.warning(f"Translation doesn't exist for language '{language}'")

        return translations

    def load_yaml(fname, args={}, user_id=None, language=None, translations=None):
        return parse_yaml(fname, args, user_id, language, translations)

    def parse_yaml(
        fname,
        args={},
        user_id=None,
        language=None,
        translations=None,
        skip_translations=False,
    ):
        try:
            jinja = hass.data.get(_ENVIRONMENT)

            if not skip_translations and translations is None:
                translations = load_translations(language)
            template = jinja.get_template(fname).render(
                {
                    **args,
                    JINJA_VARIABLE_TRANSLATE: translations,
                    JINJA_VARIABLE_USER_ID: user_id,
                }
            )

            stream = io.StringIO(template)
            stream.name = fname

            return load(stream, None, user_id, translations) or OrderedDict()
        except hass_loader.yaml.YAMLError as exc:
            _LOGGER.error(f"{str(exc)}: {template}")
            raise HomeAssistantError(exc) from exc

    def process_node(loader, node):
        args = {}

        if isinstance(node.value, str):
            value = node.value
        else:
            value, args, *_ = loader.construct_sequence(node)

        fname = os.path.abspath(os.path.join(os.path.dirname(loader.name), value))
        return [fname, args]

    def _include_yaml(loader, node):
        node_values = process_node(loader, node)

        try:
            return hass_loader._add_reference(
                load_yaml(*node_values, loader._user_id, None, loader._translations),
                loader,
                node,
            )
        except FileNotFoundError as exc:
            _LOGGER.error("Unable to include file %s: %s", node_values[0], exc)
            raise HomeAssistantError(exc)

    def _include_dir_list_yaml(loader, node):
        node_values = process_node(loader, node)
        loc = os.path.join(os.path.dirname(loader.name), node_values[0])
        return [
            load_yaml(f, node_values[1], loader._user_id, None, loader._translations)
            for f in hass_loader._find_files(loc, "*.yaml")
            if os.path.basename(f) != hass_loader.SECRET_YAML
        ]

    def _include_dir_merge_list_yaml(loader, node):
        node_values = process_node(loader, node)
        loc: str = os.path.join(os.path.dirname(loader.name), node_values[0])
        merged_list: List[hass_loader.JSON_TYPE] = []
        for fname in hass_loader._find_files(loc, "*.yaml"):
            if os.path.basename(fname) == hass_loader.SECRET_YAML:
                continue
            loaded_yaml = load_yaml(
                fname, node_values[1], loader._user_id, None, loader._translations
            )
            if isinstance(loaded_yaml, list):
                merged_list.extend(loaded_yaml)
        return hass_loader._add_reference(merged_list, loader, node)

    def _include_dir_named_yaml(loader, node):
        node_values = process_node(loader, node)
        mapping: OrderedDict = OrderedDict()
        loc = os.path.join(os.path.dirname(loader.name), node_values[0])
        for fname in hass_loader._find_files(loc, "*.yaml"):
            filename = os.path.splitext(os.path.basename(fname))[0]
            if os.path.basename(fname) == hass_loader.SECRET_YAML:
                continue
            mapping[filename] = load_yaml(
                fname, node_values[1], loader._user_id, None, loader._translations
            )
        return hass_loader._add_reference(mapping, loader, node)

    def _uncache_file(_loader, node):
        path = node.value
        timestamp = str(time.time())
        if "?" in path:
            return f"{path}&{timestamp}"
        return f"{path}?{timestamp}"

    def load(stream, Loader, user_id=None, translations=None):
        # if Loader is None:
        #     hass_loader.yaml.load_warning("load")
        Loader = CustomLoader

        loader = None
        if isinstance(Loader, CustomLoader):
            loader = Loader(stream, user_id, translations)
        else:
            loader = Loader(stream)

        try:
            return loader.get_single_data()
        finally:
            loader.dispose()

    class CustomLoader(hass_loader.SafeLineLoader):
        def __init__(self, stream, user_id=None, translations=None):
            super().__init__(stream)
            self._user_id = user_id
            self._translations = translations

    hass_loader.load_yaml = load_yaml
    dashboard.load_yaml = load_yaml
    CustomLoader.add_constructor("!include", _include_yaml)
    CustomLoader.add_constructor("!include_dir_list", _include_dir_list_yaml)
    CustomLoader.add_constructor(
        "!include_dir_merge_list", _include_dir_merge_list_yaml
    )
    CustomLoader.add_constructor("!include_dir_named", _include_dir_named_yaml)
    CustomLoader.add_constructor("!file", _uncache_file)
