# Screenshots

`render.py` builds the listing images from these PNGs. They are real captures from a throwaway sample project in the
launcher build of UE 5.8, at 100 % editor scale, with the plugin built by BuildPlugin. Its assets are Epic's template and
Starter Content, moved into the layout in `sample/layout.json`. Its documents are in `sample/`, with a small `QuestSystem`
content plugin to show plugin docs. The plugin's own `Docs` folder is removed from the sample's copy, because a buyer's
install doesn't list it (see the listing's FAQ).

`capture.py` builds the project (see its docstring):

```
python capture.py project DIR PLUGIN STARTER
python capture.py open DIR
python capture.py layout
python capture.py docs DIR
python capture.py close
```

The shots are taken by hand or over the same MCP server, with the editor in front. Close any floating window that covers
the toolbar before clicking it. A modal dialog stalls the MCP server, so answer those with a real click.

| File | Shows | Used in |
| --- | --- | --- |
| `cb-props.png` | Content Browser in its own window, 1300×640, on `/Game/Environment/Props`, Developers, Engine and Plugin content hidden | cover, beside assets |
| `docs-props.png` | Documentation in its own window, 1500×900, on the Props README | cover |
| `docs-edit.png` | The same in Edit, with a new `## Lights` section typed and not saved | live preview |
| `docs-overview.png` | Documentation, 1240×900, two documents in Favorites, on Level Design | one window |
| `docs-plugin.png` | The same, on the Quest System README | nothing to register |
| `create-row.png` | Screen grab of the bottom of the menu from right-clicking empty space in `/Game/Environment/Sky`, Create Document highlighted. Stop above the Windows taskbar | new document |
| `create-done.png`, `docs-new.png` | Browser, 1300×760, after Create Document with the name `SkyNotes`; then double-click it. Delete `SkyNotes.md` afterwards | new document |

After retaking a shot, measure its points at the top of `render.py` again.

## Afterwards

The editor keeps some settings per user, shared with every project on the machine, in
`%LOCALAPPDATA%\UnrealEngine\Editor`. Before closing the sample project, close its floating tabs and turn Developers,
Engine and Plugin content back on in the Content Browser's settings, or your other projects open that way too.
