"""Set up the sample project for the listing screenshots, through the editor's MCP server.

    python capture.py project DIR PLUGIN STARTER   build the sample project in DIR, from the packaged plugin in PLUGIN and
                                                   Epic's StarterContent in STARTER: Samples/StarterContent/Content/StarterContent
                                                   from a source engine, not the textures in Engine/Content/StarterContent
    python capture.py open DIR                     open it in UE 5.8
    python capture.py layout                       move the sample content into its folders, once, with the project open
    python capture.py docs DIR                     copy the sample documents in, after layout
    python capture.py close                        close the editor

The project enables Epic's Model Context Protocol plugin with its EditorToolset and SlateInspectorToolset, and keeps its
caches in DIR. Shots/README.md lists the shots, and what to put back afterwards: the editor keeps its layout and Content
Browser settings per user, shared with every other project.
"""

import json
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
SAMPLE = HERE / "Shots" / "sample"
URL = "http://127.0.0.1:8000/mcp"
ENGINE = pathlib.Path(r"C:\Program Files\Epic Games\UE_5.8")
SLATE = "SlateInspectorToolset.SlateInspectorToolset"
PROJECT_PLUGINS = ["KhaosDocs", "QuestSystem", "ModelContextProtocol", "EditorToolset", "SlateInspectorToolset", "PythonScriptPlugin"]
_session = None


def _post(payload, timeout=600):
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if _session:
        headers["Mcp-Session-Id"] = _session
    req = urllib.request.Request(URL, json.dumps(payload).encode(), headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        sid, body = resp.headers.get("Mcp-Session-Id"), resp.read().decode("utf-8", "replace")
    if not body.strip():
        return sid, None
    if body.lstrip().startswith("{"):
        return sid, json.loads(body)
    data = [json.loads(line[5:]) for line in body.splitlines() if line.startswith("data:")]
    return sid, data[-1] if data else None


def alive():
    """Whether an editor's MCP server answers."""
    try:
        _post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "probe", "version": "1"}}}, timeout=3)
        return True
    except OSError:
        return False


def port_open():
    """Whether something holds the MCP port. A modal dialog stalls the server, not the socket, so alive() can't tell."""
    with socket.socket() as probe:
        probe.settimeout(1)
        return probe.connect_ex(("127.0.0.1", 8000)) == 0


def call(toolset, tool, **args):
    """Call a toolset tool and return its return value."""
    global _session
    if not _session:
        _session, _ = _post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "capture", "version": "1"}}})
        _post({"jsonrpc": "2.0", "method": "notifications/initialized"})
    _, msg = _post({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
        "name": "call_tool", "arguments": {"toolset_name": toolset, "tool_name": tool, "arguments": args}}})
    text = "".join(c.get("text", "") for c in msg["result"].get("content", []))
    if msg["result"].get("isError"):
        raise RuntimeError(f"{tool}: {text[:500]}")
    try:
        return json.loads(text).get("returnValue")
    except ValueError:
        return text


WINDOW = r"""
param([string]$Title, [string]$Action)
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public class Wnd {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
}
"@
if ($Action -eq 'click') {
  $at = $Title.Split(',')
  [void][Wnd]::SetCursorPos([int]$at[0], [int]$at[1]); Start-Sleep -Milliseconds 150
  [Wnd]::mouse_event(2, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 60; [Wnd]::mouse_event(4, 0, 0, 0, [UIntPtr]::Zero)
  exit 0
}
$script:hit = [IntPtr]::Zero
$cb = [Wnd+EnumProc]{ param($h, $l)
  $sb = New-Object Text.StringBuilder 256; [void][Wnd]::GetWindowText($h, $sb, 256)
  if ($sb.ToString() -eq $Title) { $script:hit = $h; return $false }
  return $true }
[void][Wnd]::EnumWindows($cb, [IntPtr]::Zero)
if ($script:hit -eq [IntPtr]::Zero) { exit 3 }
if ($Action -eq 'close') { [void][Wnd]::PostMessage($script:hit, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) }
if ($Action -eq 'front') {
  [Wnd]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero); [Wnd]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
  [void][Wnd]::BringWindowToTop($script:hit); [void][Wnd]::SetForegroundWindow($script:hit)
}
"""


def powershell(*args):
    """What only Windows itself can do: find a window, move the mouse."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as work:
        path = pathlib.Path(work) / "s.ps1"
        path.write_text(WINDOW, encoding="utf-8")
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(path), *args], check=True, capture_output=True)


def project(folder, plugin, starter):
    folder, plugin, starter = pathlib.Path(folder), pathlib.Path(plugin), pathlib.Path(starter)
    if not (starter / "Architecture").is_dir():
        raise SystemExit(f"{starter} is not the full StarterContent folder")
    template = ENGINE / "Templates" / "TemplateResources" / "High"
    (folder / "Content" / "Characters").mkdir(parents=True, exist_ok=True)
    (folder / "Plugins").mkdir(exist_ok=True)
    shutil.copytree(plugin, folder / "Plugins" / "KhaosDocs", dirs_exist_ok=True, ignore=shutil.ignore_patterns("Intermediate", "Docs"))
    shutil.copytree(template / "Characters" / "Content" / "Mannequins", folder / "Content" / "Characters" / "Mannequins", dirs_exist_ok=True)
    shutil.copytree(template / "LevelPrototyping" / "Content", folder / "Content" / "LevelPrototyping", dirs_exist_ok=True)
    shutil.copytree(template / "Input" / "Content", folder / "Content" / "Input", dirs_exist_ok=True)
    shutil.copytree(starter, folder / "Content" / "StarterContent", dirs_exist_ok=True)
    shutil.copytree(SAMPLE / "Plugins", folder / "Plugins", dirs_exist_ok=True)
    (folder / "Config").mkdir(exist_ok=True)
    (folder / "Config" / "DefaultEditorPerProjectUserSettings.ini").write_text(
        "[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]\nbAutoStartServer=True\n", encoding="utf-8")
    (folder / "Demo.uproject").write_text(json.dumps({"FileVersion": 3, "EngineAssociation": "5.8", "Plugins": [
        {"Name": name, "Enabled": True} for name in PROJECT_PLUGINS]}, indent="\t"), encoding="utf-8")
    print(f"built {folder / 'Demo.uproject'}")


def open_project(folder):
    if port_open():
        raise SystemExit("something already holds port 8000: close that editor first")
    folder = pathlib.Path(folder).resolve()
    cache = folder / "Cache"
    subprocess.Popen([str(ENGINE / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"), str(folder / "Demo.uproject"), "-nosplash", "-NoLiveCoding",
                      "-DDC=(Local)", f"-LocalDataCachePath={cache / 'DDC'}", f"-ZenDataPath={cache / 'Zen'}",
                      "-ini:Engine:[Zen.AutoLaunch]:DesiredPort=8599"])
    for _ in range(200):
        if alive():
            print("editor is up")
            return
        time.sleep(3)
    raise TimeoutError("the editor's MCP server never answered")


def layout():
    """Run layout.py in the console."""
    powershell("Demo - Unreal Editor", "front")
    time.sleep(0.6)
    main = call(SLATE, "Snapshot", ref="", maxDepth=1).splitlines()[0].split("[ref=")[1].split("]")[0]
    call(SLATE, "Observe", ref=main, maxDepth=80)
    time.sleep(1.5)
    boxes = [line for line in call(SLATE, "Snapshot", ref=main, maxDepth=80).splitlines() if "textbox" in line and "[pos=" in line]
    console = max(boxes, key=lambda line: int(line.split("[pos=")[1].split(",")[1].split(" ")[0]))
    x, y = console.split("[pos=")[1].split(" ")[0].split(",")
    powershell(f"{int(x) + 40},{int(y) + 7}", "click")
    time.sleep(0.5)
    ref = console.split("[ref=")[1].split("]")[0]
    try:
        if not call(SLATE, "Type", ref=ref, text=f'py "{(SAMPLE / "layout.py").as_posix()}"', submit=True):
            raise SystemExit("the console box took no input: click the main window and run layout again")
    except OSError:
        print("the connection dropped during the script: check the output log for 'layout done'")
    else:
        print("layout ran: check the output log for 'layout done'")


def docs(folder):
    folder = pathlib.Path(folder)
    shutil.copytree(SAMPLE / "Content", folder / "Content", dirs_exist_ok=True)
    for name in ("README.md", "CHANGELOG.md"):
        shutil.copy(SAMPLE / name, folder / name)
    print("copied the sample documents")


def close():
    powershell("Demo - Unreal Editor", "close")
    for _ in range(60):
        if not port_open():
            return
        time.sleep(2)
    raise TimeoutError("the editor is still running: look for a save dialog")


if __name__ == "__main__":
    {"project": project, "open": open_project, "layout": layout, "docs": docs, "close": close}[sys.argv[1]](*sys.argv[2:])
