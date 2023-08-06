import json
from pathlib import Path
from typing import Optional

import fire
import mojimoji
import yaml


class Converter:
    @classmethod
    def yaml2json(cls, yaml_path: Path, json_path: Optional[Path] = None) -> None:
        with open(yaml_path) as f:
            contents = yaml.safe_load(f)

        output_path = str(yaml_path).replace(yaml_path.suffix, ".json") if json_path is None else str(json_path)
        with open(output_path, "w") as f:
            json.dump(contents, f, indent=4, ensure_ascii=False)

    @classmethod
    def json2yaml(cls, json_path: Path, yaml_path: Optional[Path] = None) -> None:
        with open(json_path) as f:
            contents = json.load(f)

        output_path = str(json_path).replace(json_path.suffix, ".yml") if yaml_path is None else str(yaml_path)
        with open(output_path, "w") as f:
            yaml.safe_dump(contents, f)

    @classmethod
    def han2zen(cls, text: str) -> str:
        return mojimoji.han_to_zen(text)

    @classmethod
    def zen2han(cls, text: str) -> str:
        return mojimoji.zen_to_han(text)


def yaml2json():
    fire.Fire(Converter.yaml2json)


def json2yaml():
    fire.Fire(Converter.json2yaml)


def han2zen():
    fire.Fire(Converter.han2zen)


def zen2han():
    fire.Fire(Converter.zen2han)
