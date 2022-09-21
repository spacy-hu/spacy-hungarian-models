import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Dict, List, Optional, Union, Any

from packaging import version
from packaging.version import Version

from huspacy.utils import run_command

__URL = "https://huggingface.co/huspacy/{model_name}/resolve/{version}/{model_name}-any-py3-none-any.whl"
__DEFAULT_VERSION = "main"
__DEFAULT_MODEL = "hu_core_news_lg"

__AVAILABLE_MODELS: Dict[str, List[str]] = {
    "hu_core_news_lg": ["3.2.1", "3.2.2", "3.3.0", "3.3.1", "3.4.0", "3.4.1", "3.4.2"],
    "hu_core_news_trf": ["3.2.0", "3.2.1", "3.2.2", "3.2.3", "3.2.4"]
}


def get_valid_models(spacy_version: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Returns valid model names and versions for the given spacy version

    Returns:
        Dict[str, List[str]]: Valid model names and associated versions
    """
    if spacy_version is not None:
        spacy_version: Version = version.parse(spacy_version)
        available_models = defaultdict(list)
        for model_name, versions in __AVAILABLE_MODELS.items():
            for ver in versions:
                model_ver = version.parse(ver)
                if model_ver.major == spacy_version.major and model_ver.minor == spacy_version.minor:
                    available_models[model_name].append(model_ver)

        return dict(available_models)
    else:
        return __AVAILABLE_MODELS


def download(model_name: str = __DEFAULT_MODEL, version: str = __DEFAULT_VERSION) -> None:
    """Downloads a HuSpaCy model.

    Args:
        model_name (str): model name, if not provided it defaults to `hu_core_news_lg`
        version (str): model version, if not provided it defaults to the latest version

    Returns: None

    """
    assert model_name in __AVAILABLE_MODELS, \
        f"{model_name} is not a valid model name"
    assert version == "main" or version in __AVAILABLE_MODELS[model_name], \
        f"{version} is not a valid version for {model_name}"

    download_url = __URL.format(version=version, model_name=model_name)
    cmd = [sys.executable, "-m", "pip", "install"] + [download_url]
    run_command(cmd)


# noinspection PyDefaultArgument,PyUnresolvedReferences
def load(
        name: Union[str, Path] = __DEFAULT_MODEL,
        vocab: Union["Vocab", bool] = True,
        disable: Optional[Iterable[str]] = None,
        exclude: Optional[Iterable[str]] = None,
        config: Union[Dict[str, Any], "Config", None] = None,
) -> "Language":
    """Loads a HuSpaCy model.

    Args:
        name (str): model name, if not provided it defaults to `hu_core_news_lg`
        vocab (Vocab): A Vocab object. If True, a vocab is created.
        disable (Iterable[str]): Names of pipeline components to disable. Disabled pipes will be loaded but they
            won't be run unless you explicitly enable them by calling nlp.enable_pipe.
        exclude (Iterable[str]): Names of pipeline components to exclude. Excluded components won't be loaded.
        config (Dict[str, Any] / Config): Config overrides as nested dict or dict
        keyed by section values in dot notation.

    Returns:
        Language: The loaded nlp object

    """
    from spacy.util import load_model, SimpleFrozenDict, SimpleFrozenList

    disable = disable or SimpleFrozenList()
    exclude = exclude or SimpleFrozenList()
    config = config or SimpleFrozenDict()

    return load_model(
        name, vocab=vocab, disable=disable, exclude=exclude, config=config
    )
