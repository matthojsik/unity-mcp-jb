# Standard Operating Procedure: Updating the Unity MCP Package from GitHub

This guide explains how to pull the latest version of Unity MCP when it is installed via
Unity's "Add package from git URL" workflow. Follow these steps whenever you push
changes to the GitHub repository and want them available in your Unity project.

## 1. Push Changes to GitHub

1. Commit and push your updates to the repository.
2. (Recommended) Increment the `version` field in `UnityMcpBridge/package.json` and
   push the change so Unity detects a new version.
3. Optionally create a Git tag for the release if you prefer to reference tags.

## 2. Refresh the Package in Unity

1. Open your Unity project.
2. Go to **Window > Package Manager**.
3. Locate **Unity MCP Bridge** (`com.justinpbarnett.unity-mcp`).
4. If Unity displays an **Update** button, click it to fetch the latest commit.
   Otherwise, click the `+` button and choose **Add package from git URL...** again,
   using the same URL:
   ```
   https://github.com/justinpbarnett/unity-mcp.git?path=/UnityMcpBridge
   ```
5. Unity will download the newest revision and recompile scripts.

## 3. Verify the Python Server Path

The package automatically installs the Python server the first time you add it.
If you moved or renamed the server folder, update your MCP client's configuration
so it points to the new location. For typical updates where files remain in the
same directories, no additional steps are required.

## 4. Test the Updated Package

1. Restart the Unity Editor to ensure all assemblies reload.
2. Launch your MCP client and verify the server starts successfully.
3. Run a simple tool (e.g., `read_console`) to confirm connectivity.

Following this procedure ensures your Unity project uses the most recent code
from GitHub whenever you make changes.
