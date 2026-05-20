(function () {
  function buildPendingTree(items) {
    const root = { name: "/", path: "/", directories: new Map(), files: [] };
    for (const item of items) {
      const path = String(item?.path || "");
      const parts = path.split("/").filter(Boolean);
      let cursor = root;
      let current = "";
      for (let index = 0; index < parts.length - 1; index += 1) {
        const part = parts[index];
        current += `/${part}`;
        if (!cursor.directories.has(part)) {
          cursor.directories.set(part, { name: part, path: current, directories: new Map(), files: [] });
        }
        cursor = cursor.directories.get(part);
      }
      cursor.files.push(item);
    }
    return root;
  }

  function collectNodeFilePaths(node) {
    let result = [];
    for (const file of node.files || []) {
      if (file?.path) result.push(file.path);
    }
    for (const child of node.directories?.values() || []) {
      result = result.concat(collectNodeFilePaths(child));
    }
    return result;
  }

  function refreshPendingDirectoryMap(root) {
    const directoryFiles = new Map();
    function walk(node) {
      directoryFiles.set(node.path, collectNodeFilePaths(node));
      for (const child of node.directories?.values() || []) walk(child);
    }
    walk(root);
    return directoryFiles;
  }

  function renderPendingNode(ctx, node, state) {
    const childDirs = [...(node.directories?.values() || [])].sort((a, b) => a.path.localeCompare(b.path, "zh-CN"));
    const files = [...(node.files || [])].sort((a, b) => String(a.path || "").localeCompare(String(b.path || ""), "zh-CN"));
    const allPaths = collectNodeFilePaths(node);
    const checkedCount = allPaths.filter((path) => state.selection.has(path)).length;
    const expanded = state.expanded.has(node.path);
    return `
      <div class="tree-node">
        <div class="tree-row">
          <button type="button" class="tree-toggle ${childDirs.length ? "" : "empty"}" data-toggle-node="${ctx.escapeHtml(node.path)}">${childDirs.length ? (expanded ? "-" : "+") : ""}</button>
          <input type="checkbox" data-select-dir="${ctx.escapeHtml(node.path)}" ${allPaths.length && checkedCount === allPaths.length ? "checked" : ""}>
          <div class="tree-label">
            <div>${ctx.escapeHtml(node.name || "/")}</div>
            <div class="mono">${ctx.escapeHtml(node.path)} | ${allPaths.length} 个文件</div>
          </div>
        </div>
        ${expanded ? `
          <div>
            ${childDirs.map((child) => renderPendingNode(ctx, child, state)).join("")}
            ${files.map((file) => `
              <label class="tree-row">
                <span class="tree-toggle empty"></span>
                <input type="checkbox" data-select-file="${ctx.escapeHtml(file.path || "")}" ${state.selection.has(file.path) ? "checked" : ""}>
                <div class="tree-label">
                  <div>${ctx.escapeHtml((file.path || "").split("/").filter(Boolean).pop() || file.path || "")}</div>
                  <div class="mono">${ctx.escapeHtml(file.path || "")} | ${ctx.formatBytes(file.size)} | ${ctx.escapeHtml(file.reason || "-")}</div>
                </div>
              </label>
            `).join("")}
          </div>
        ` : ""}
      </div>
    `;
  }

  function syncPendingCheckboxState(root, state) {
    root.querySelectorAll("[data-select-dir]").forEach((box) => {
      const dir = box.getAttribute("data-select-dir");
      const paths = state.directoryFiles.get(dir) || [];
      const count = paths.filter((path) => state.selection.has(path)).length;
      box.checked = paths.length > 0 && count === paths.length;
      box.indeterminate = count > 0 && count < paths.length;
    });
  }

  function bindPendingEvents(ctx, items, state) {
    const root = document.getElementById("pending-tree");
    root.querySelectorAll("[data-toggle-node]").forEach((button) => {
      button.addEventListener("click", () => {
        const node = button.getAttribute("data-toggle-node");
        if (!node) return;
        if (state.expanded.has(node)) state.expanded.delete(node);
        else state.expanded.add(node);
        renderPendingTree(ctx, items);
      });
    });
    root.querySelectorAll("[data-select-file]").forEach((box) => {
      box.addEventListener("change", () => {
        const path = box.getAttribute("data-select-file");
        if (!path) return;
        if (box.checked) state.selection.add(path);
        else state.selection.delete(path);
        state.selectionTouched = true;
        ctx.setPendingState(state);
        syncPendingCheckboxState(root, state);
      });
    });
    root.querySelectorAll("[data-select-dir]").forEach((box) => {
      box.addEventListener("change", () => {
        const dir = box.getAttribute("data-select-dir");
        const paths = state.directoryFiles.get(dir) || [];
        for (const path of paths) {
          if (box.checked) state.selection.add(path);
          else state.selection.delete(path);
        }
        state.selectionTouched = true;
        ctx.setPendingState(state);
        renderPendingTree(ctx, items);
      });
    });
  }

  function renderPendingTree(ctx, items) {
    const root = document.getElementById("pending-tree");
    const list = Array.isArray(items) ? items : [];
    let state = ctx.getPendingState();
    ctx.setLatestPendingItems(list);
    if (!list.length) {
      root.textContent = ctx.currentLang() === "en" ? "No pending reupload files" : ctx.currentLang() === "mix" ? "暂无待补传文件 / No pending reupload files" : "暂无待补传文件";
      state = {
        selection: new Set(),
        selectionTouched: false,
        expanded: new Set(["/"]),
        directoryFiles: new Map(),
      };
      ctx.setPendingState(state);
      return;
    }
    const available = new Set(list.map((item) => item?.path).filter(Boolean));
    state.selection = new Set([...state.selection].filter((path) => available.has(path)));
    if (!state.selectionTouched && state.selection.size === 0) {
      state.selection = new Set(available);
    }
    const tree = buildPendingTree(list);
    state.directoryFiles = refreshPendingDirectoryMap(tree);
    if (state.expanded.size <= 1) {
      for (const item of list) {
        const parts = String(item.path || "").split("/").filter(Boolean);
        let current = "";
        for (let index = 0; index < Math.min(parts.length - 1, 2); index += 1) {
          current += `/${parts[index]}`;
          state.expanded.add(current);
        }
      }
    }
    const children = [...tree.directories.values()].sort((a, b) => a.path.localeCompare(b.path, "zh-CN"));
    root.innerHTML = `
      <div class="subtle" style="margin-bottom:10px;">${ctx.currentLang() === "en" ? `Total ${list.length} pending files. Expand, collapse, and select by real directory tree.` : ctx.currentLang() === "mix" ? `共 ${list.length} 个待补传文件 / Total ${list.length} pending files. 可按目录树展开、折叠和联动勾选。` : `共 ${list.length} 个待补传文件，可按目录树展开、折叠和联动勾选。`}</div>
      ${children.map((child) => renderPendingNode(ctx, child, state)).join("")}
    `;
    ctx.setPendingState(state);
    bindPendingEvents(ctx, list, state);
    syncPendingCheckboxState(root, state);
  }

  window.CloudPanBridgePendingUi = {
    renderPendingTree,
  };
})();
