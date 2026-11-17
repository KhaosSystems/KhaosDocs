# Khaos Docs: Fab listing

## Title

Khaos Docs: Markdown in the Content Browser

## Short description

Project docs in the Content Browser, as plain .md files.

## Description

The best place for a note about a folder is that folder. Khaos Docs puts your markdown in the Content Browser, right beside the assets it describes, and opens it in one Documentation window where you read and edit with a live preview.

Nothing is imported. A document is a real `.md` file, so it lives in your repo and opens in any editor. Docs in your project and its plugins all land in one table of contents, with nothing to register.

Editor-only. No plugin code or cooked content in your packaged game.

## FAQ

**Do I have to convert anything?**
No. Any `.md` or `.txt` under `Content` shows up where it sits, with no import and no `.uasset`.

**How do I open it?**
Press the document icon on the level editor toolbar, choose Tools > Documentation, or double-click a document in the Content Browser.

**How do I make a new document?**
Right-click empty space in a folder and choose Create Document. The name you give it becomes the first heading.

**Which markdown does it render?**
Headings, bold, italic, inline code, code blocks, lists, quotes, rules and links. Tables, images, task lists and syntax highlighting aren't supported, and show up as plain text.

**Where does it look for documents?**
In your project and its plugins, as long as the plugin can hold content: everywhere under `Content`, a `Docs` folder, and files like `README.md` beside the project or `.uplugin`. Only `Content` files appear in the Content Browser; the rest are in the Documentation window. Plugins installed in the engine folder aren't scanned.

**Do links work?**
Relative links open the other document in place, and web links open your browser. Links to assets and to a heading on a page don't.

**Can I search my docs?**
You can filter the table of contents by title or file name. It doesn't search inside documents.

**Does it work with source control?**
Documents are plain text, so they go in your repo like any other file. On Perforce, check a file out before you save it: the editor won't do it for you.

**Does it add anything to my game?**
No code or cooked content: the module only builds for Editor targets.

## Technical details

- **Code modules:** `KhaosDocsEditor` (Editor)
- **Number of Blueprints:** 0
- **Number of C++ classes:** 1 UObject class
- **Network replicated:** No
- **Supported development platforms:** Windows
- **Supported target build platforms:** Windows, Mac, Linux
- **Supported engine versions:** 5.8
- **Documentation:** https://docs.khaos.systems/unreal/khaos-docs/
- **Important notes:** Put a `.md` file under `Content`, or right-click a folder in the Content Browser and choose Create Document. Open the Documentation window from the toolbar or Tools > Documentation.

## Version notes (1.0.0)

First release.

## Tags

documentation, markdown, docs, notes, wiki, content browser, editor tool, team, workflow, utility
