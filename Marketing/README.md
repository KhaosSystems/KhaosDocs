# Marketing

The Fab listing for Khaos Docs. Nothing here ships in the plugin.

- [Listing.md](Listing.md): the listing text to paste into Fab.
- [Images/](Images/): the seven 1920×1080 listing images to upload.
- [Shots/](Shots/): the editor screenshots the images are built from, the sample documents, and how to retake them.
- [render.py](render.py): builds `Images/` from `Shots/` (needs Chrome or Edge). [capture.py](capture.py) builds the sample
  project through the editor's MCP server.
- [Brand/](Brand/): the Khaos Systems logo and the plugin icon.

When the plugin changes visibly, retake the shots and run `python render.py`. A missing shot renders as a stand-in and
that image is written as `.draft.png`, which git ignores; upload only images without `.draft`.
