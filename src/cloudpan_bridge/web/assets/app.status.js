(function () {
  function renderLogs(ctx, records) {
    const root = document.getElementById("logs");
    if (!root) return;
    root.textContent = (records || []).map((row) => `[${row.ts}] [${row.level}] ${row.message}`).join("\n");
    root.scrollTop = root.scrollHeight;
  }

  function renderOverviewRouteSummary(ctx, syncState = {}, runtimeState = {}) {
    const root = document.getElementById("overview-route-summary");
    if (!root) return;
    const currentTask = syncState?.current_task || {};
    const currentSourceContext = syncState?.current_source_context || {};
    const sourcePath = String(currentTask.source_path || document.getElementById("source_path")?.value || ctx.getConfigCache()?.source_path || ctx.getCurrentDirectoryPath() || "/").trim() || "/";
    const targetKey = String(currentTask.target_key || document.getElementById("target_key")?.value || ctx.getConfigCache()?.target_key || "guangya").trim() || "guangya";
    const targetPath = String(currentTask.target_path || document.getElementById("target_path")?.value || ctx.getConfigCache()?.target_path || "/").trim() || "/";
    const mode = ctx.normalizeOpenListMode(document.getElementById("openlist_mode")?.value || ctx.getConfigCache()?.openlist_mode || "external_local");
    const queueSize = Array.isArray(syncState?.source_queue) ? syncState.source_queue.length : 0;
    const pendingSize = Array.isArray(syncState?.persistent_pending) ? syncState.persistent_pending.length : 0;
    const activeUrl = String(document.getElementById("effective_openlist_url")?.value || runtimeState?.active_url || ctx.getConfigCache()?.openlist_url || "-").trim() || "-";
    const sourceRuntime = window.__cpbStatusCache?.source_runtime || {};
    root.innerHTML = `
      <div class="mono">OpenList Mode: ${ctx.escapeHtml(ctx.getOpenListModeLabel(mode))}</div>
      <div class="mono">OpenList URL: ${ctx.escapeHtml(activeUrl)}</div>
      <div class="mono">Source: ${ctx.escapeHtml(sourcePath)}</div>
      <div class="mono">Target: ${ctx.escapeHtml(targetKey)} -> ${ctx.escapeHtml(targetPath)}</div>
      <div class="mono">Source Mapping: mount=${ctx.escapeHtml(currentSourceContext.mount_path || "-")} | effective=${ctx.escapeHtml(currentSourceContext.effective_driver || "-")}</div>
      <div class="mono">Source Route: pref=${ctx.escapeHtml(sourceRuntime.requested_provider_preference || "-")} | selected=${ctx.escapeHtml(sourceRuntime.selected_source_mode || "-")} | provider=${ctx.escapeHtml(sourceRuntime.selected_provider_key || "-")}</div>
      <div class="mono">Queue: ${queueSize} | Pending: ${pendingSize}</div>
    `;
  }

  window.CloudPanBridgeStatusView = {
    renderLogs,
    renderOverviewRouteSummary,
  };
})();
