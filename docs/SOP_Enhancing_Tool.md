# Standard Operating Procedure: Enhancing Unity MCP Tools

This SOP describes the steps required to safely modify or extend an existing tool such as `manage_gameobject`.
Follow these steps whenever you add new features or adjust behaviour so every layer stays in sync.

## 1. Update the Unity Bridge (C#)

1. Edit the appropriate handler in `UnityMcpBridge/Editor/Tools` (e.g. `ManageGameObject.cs`).
2. Implement new logic or parameters inside the `HandleCommand` switch and associated helper methods.
3. If new command names are introduced, ensure they are registered in `CommandRegistry.cs`.
4. Recompile the Unity project and verify no compile errors appear in the Console.

## 2. Update the Python Server Wrapper

1. Modify the matching Python tool in `UnityMcpServer/src/tools` (e.g. `manage_gameobject.py`).
2. Document any new arguments in the `@mcp.tool()` function signature and pass them through to Unity via `send_command`.
3. Remove parameters with `None` values before sending them to keep the payload clean.
4. If you create a brand new tool module, import and register it in `UnityMcpServer/src/tools/__init__.py` and call the registration function inside `register_all_tools`.

## 3. Check Server Entry Point

If the server's main file (`server.py`) directly references the tool or exposes it in the `asset_creation_strategy` prompt, make sure any new behaviour is reflected there.

## 4. Update Documentation

1. Describe the new functionality in `docs/HOW_IT_WORKS.md` or another appropriate document.
2. Keep argument names and behaviour descriptions consistent between the docs and the Python/C# implementations.

## 5. Validate End-to-End

1. Restart the Unity Editor so the bridge reloads your C# changes.
2. Run the Python server (`uv run server.py`) and ensure it reports all tools registering successfully.
3. Call the updated tool from your MCP client to verify it behaves as intended.
4. Check the Unity Console for errors and fix any issues found.

Following this procedure ensures both sides of the bridge remain synchronized when enhancing tools such as `manage_gameobject`.
