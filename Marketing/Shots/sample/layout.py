"""Runs inside the editor (py <path>): moves Epic's sample content into a realistic project layout and adds a small
blueprint to the folders that would otherwise be empty. capture.py layout starts it."""

import json
import pathlib

import unreal

LAYOUT = json.loads((pathlib.Path(__file__).resolve().parent / "layout.json").read_text(encoding="utf-8"))
LIBRARY = unreal.EditorAssetLibrary

for source, target in LAYOUT["moves"].items():
    if LIBRARY.does_directory_exist(source):
        LIBRARY.make_directory(target.rsplit("/", 1)[0])
        LIBRARY.rename_directory(source, target)

tools = unreal.AssetToolsHelpers.get_asset_tools()
for folder, names in LAYOUT["add"].items():
    LIBRARY.make_directory(folder)
    for name in names:
        if not LIBRARY.does_asset_exist(f"{folder}/{name}"):
            factory = unreal.BlueprintFactory()
            factory.set_editor_property("parent_class", unreal.Actor)
            tools.create_asset(name, folder, unreal.Blueprint, factory)

LIBRARY.save_directory("/Game", only_if_is_dirty=True, recursive=True)
if LIBRARY.does_directory_exist("/Game/StarterContent"):
    LIBRARY.delete_directory("/Game/StarterContent")
print("layout done")
