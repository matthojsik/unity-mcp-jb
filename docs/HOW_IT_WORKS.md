# Unity MCP Detailed Overview

This document explains the architecture and workflow of the Unity MCP project and describes the tools exposed to Model Context Protocol clients like Cursor.

## High Level Architecture

Unity MCP has two main components:

1. **UnityMcpBridge** – a Unity package running inside the Editor. It listens on TCP port `6400`, receives JSON commands, performs the requested operations in the editor and sends the results back.
2. **UnityMcpServer** – a Python server that exposes MCP tools. It communicates with the UnityMcpBridge via sockets and allows MCP clients (like Cursor) to call Unity operations as functions.

The usual data flow is:

```
[MCP client (Cursor, Claude, etc.)]
        ↕  (MCP protocol)
[UnityMcpServer (Python)]
        ↕  (TCP JSON commands)
[UnityMcpBridge (Unity Editor)]
```

## UnityMcpServer

The server is implemented in `UnityMcpServer/src/server.py`. It loads configuration from `config.py`, registers tool functions and exposes them to MCP clients.

Key lines from `server.py` show how all tools are registered and how the list of available tools is advertised:

```python
register_all_tools(mcp)
```

```python
@mcp.prompt()
def asset_creation_strategy() -> str:
    return (
        "Available Unity MCP Server Tools:\n\n"
        "- `manage_editor`: Controls editor state and queries info.\n"
        "- `execute_menu_item`: Executes Unity Editor menu items by path.\n"
        "- `read_console`: Reads or clears Unity console messages, with filtering options.\n"
        "- `manage_scene`: Manages scenes.\n"
        "- `manage_gameobject`: Manages GameObjects in the scene.\n"
        "- `manage_script`: Manages C# script files.\n"
        "- `manage_asset`: Manages prefabs and assets.\n\n"
    )
```
【F:UnityMcpServer/src/server.py†L48-L67】

The `register_all_tools` function inside `UnityMcpServer/src/tools/__init__.py` registers each tool with the server:

```python
from .manage_script import register_manage_script_tools
from .manage_scene   import register_manage_scene_tools
from .manage_editor  import register_manage_editor_tools
from .manage_gameobject import register_manage_gameobject_tools
from .manage_asset   import register_manage_asset_tools
from .read_console   import register_read_console_tools
from .execute_menu_item import register_execute_menu_item_tools
```
【F:UnityMcpServer/src/tools/__init__.py†L1-L18】

When the server starts it attempts to connect to the Unity editor via `UnityConnection` and keeps the connection alive for tool calls.

## UnityMcpBridge

The bridge lives in `UnityMcpBridge/Editor`. It launches a TCP listener when the editor starts. Incoming commands are parsed and dispatched to handlers. The code around setting up the listener can be seen in `UnityMcpBridge.cs`:

```csharp
listener = new TcpListener(IPAddress.Loopback, unityPort);
listener.Start();
Task.Run(ListenerLoop);
EditorApplication.update += ProcessCommands;
```
【F:UnityMcpBridge/Editor/UnityMcpBridge.cs†L132-L142】

Each command is routed based on the tool name. For example the `ExecuteCommand` method maps command types to the tool handlers:

```csharp
object result = command.type switch
{
    "manage_script" => ManageScript.HandleCommand(paramsObject),
    "manage_scene"  => ManageScene.HandleCommand(paramsObject),
    "manage_editor" => ManageEditor.HandleCommand(paramsObject),
    "manage_gameobject" => ManageGameObject.HandleCommand(paramsObject),
    "manage_asset" => ManageAsset.HandleCommand(paramsObject),
    "read_console" => ReadConsole.HandleCommand(paramsObject),
    "execute_menu_item" => ExecuteMenuItem.HandleCommand(paramsObject),
    _ => throw new ArgumentException($"Unknown or unsupported command type: {command.type}"),
};
```
【F:UnityMcpBridge/Editor/UnityMcpBridge.cs†L335-L349】

## Available Tools

Below is an overview of the primary tools that Cursor (or any MCP client) can call through the server. Each tool corresponds to a C# handler in `UnityMcpBridge/Editor/Tools` and a Python wrapper in `UnityMcpServer/src/tools`.

### manage_script
Handles creation, reading, updating and deletion of C# scripts within the project.
The handler begins as follows:
```csharp
/// Handles CRUD operations for C# scripts within the Unity project.
public static class ManageScript
```
【F:UnityMcpBridge/Editor/Tools/ManageScript.cs†L12-L16】

### manage_scene
Loads, saves, creates and queries scenes.
```csharp
/// Handles scene management operations like loading, saving, creating, and querying hierarchy.
public static class ManageScene
```
【F:UnityMcpBridge/Editor/Tools/ManageScene.cs†L14-L18】

### manage_gameobject
Allows creation, modification, searching and deletion of GameObjects in the current scene, along with component inspection.
```csharp
/// Handles GameObject manipulation within the current scene (CRUD, find, components).
public static class ManageGameObject
```
【F:UnityMcpBridge/Editor/Tools/ManageGameObject.cs†L15-L18】
Optional parameters `include_components` and `include_component_properties` control how much component data is returned when searching for objects or retrieving a scene hierarchy.

### manage_asset
Supports importing, creating, modifying and retrieving info about assets and prefabs.
```csharp
/// Handles asset management operations within the Unity project.
public static class ManageAsset
```
【F:UnityMcpBridge/Editor/Tools/ManageAsset.cs†L13-L16】

### manage_editor
Exposes editor-level operations such as tag and layer management or querying the active tool.
```csharp
/// Handles operations related to controlling and querying the Unity Editor state,
/// including managing Tags and Layers.
public static class ManageEditor
```
【F:UnityMcpBridge/Editor/Tools/ManageEditor.cs†L12-L16】

### read_console
Reads or clears messages from the Unity console using reflection to access internal log entries.
```csharp
/// Handles reading and clearing Unity Editor console log entries.
/// Uses reflection to access internal LogEntry methods/properties.
public static class ReadConsole
```
【F:UnityMcpBridge/Editor/Tools/ReadConsole.cs†L13-L18】

### execute_menu_item
Allows scripted execution of menu commands in the Unity Editor while maintaining a small blacklist for safety.
```csharp
/// Handles executing Unity Editor menu items by path.
public static class ExecuteMenuItem
```
【F:UnityMcpBridge/Editor/Tools/ExecuteMenuItem.cs†L10-L14】

## Using Cursor with Unity MCP

Once the Unity package is installed and the Python server is configured in Cursor's `mcp.json`, the tools above become callable as functions from within Cursor. For example:

- `manage_gameobject(action="create", name="Player")` – creates a new GameObject named *Player*.
- `manage_scene(action="get_hierarchy", path="Assets/Scenes/Main.unity")` – returns a structured description of a scene.
- `execute_menu_item(menu_path="File/Save Project")` – triggers the Save Project command in the editor.
- `manage_gameobject(action="find", target="Player", include_components=True, include_component_properties=True)` – find an object and include its components and their properties.

Because the server is implemented using the FastMCP framework, these calls appear to Cursor as standard function-like tools with documentation, arguments and return values. This allows automation of complex Unity workflows from within the editor.

## Summary

Unity MCP bridges a running Unity Editor with an MCP-compatible client. The Python server registers multiple tools related to scenes, assets, scripts, editor settings and more. The Unity side listens for JSON commands and performs the requested operations. When hooked up to Cursor, these tools allow rich programmatic control of Unity directly from your code editor or chat interface, unlocking automated workflows and streamlined project management.
