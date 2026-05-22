(function () {
  function renderSync(ctx, sync) {
    const currentLang = ctx.currentLang;
    const escapeHtml = ctx.escapeHtml;
    if (!sync) return;
    const running = sync?.running ? (currentLang() === "en" ? "running" : currentLang() === "mix" ? "运行中 / running" : "运行中") : (currentLang() === "en" ? "idle" : currentLang() === "mix" ? "空闲 / idle" : "空闲");
    const summary = sync?.last_summary || {};
    const queue = sync?.queue_runner || {};
    const task = sync?.current_task || {};
    const mapping = sync?.current_source_context || queue?.source_mapping_context || {};
    document.getElementById("sync-summary").innerHTML = `
      <div class="badge">${escapeHtml(running)}</div>
      <div class="mono">${currentLang() === "en" ? "Last error" : currentLang() === "mix" ? "最近错误 / Last error" : "最近错误"}: ${escapeHtml(sync?.last_error || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Current task" : currentLang() === "mix" ? "当前任务 / Current task" : "当前任务"}: ${escapeHtml(task.mode || "-")} | ${escapeHtml(task.source_path || "-")} -> ${escapeHtml(task.target_key || "-")}:${escapeHtml(task.target_path || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Source mapping" : currentLang() === "mix" ? "源映射 / Source mapping" : "源映射"}: mount=${escapeHtml(mapping.mount_path || "-")} | requested=${escapeHtml(mapping.requested_driver || "-")} | override=${escapeHtml(mapping.source_profile_override || "-")} | effective=${escapeHtml(mapping.effective_driver || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Current queue source" : currentLang() === "mix" ? "当前队列目录 / Current queue source" : "当前队列目录"}: ${escapeHtml(queue.current_source || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Remaining" : currentLang() === "mix" ? "待处理剩余 / Remaining" : "待处理剩余"}: ${queue.remaining ?? "-"}</div>
      <div class="mono">${currentLang() === "en" ? "Last summary" : currentLang() === "mix" ? "最近结果 / Last summary" : "最近结果"}: total=${summary.total ?? 0}, direct=${summary.direct_success ?? 0}, downloaded=${summary.downloaded_success ?? 0}, failed=${summary.failed ?? 0}</div>
    `;
  }

  function renderRuntime(ctx, runtime) {
    const currentLang = ctx.currentLang;
    const escapeHtml = ctx.escapeHtml;
    const runtimeMode = runtime?.mode_label || ctx.getOpenListModeLabel(runtime?.mode || document.getElementById("openlist_mode")?.value);
    const canInstall = Boolean(runtime?.install_required);
    const yesText = currentLang() === "en" ? "yes" : currentLang() === "mix" ? "是 / yes" : "是";
    const noText = currentLang() === "en" ? "no" : currentLang() === "mix" ? "否 / no" : "否";
    document.getElementById("runtime-summary").innerHTML = `
      <div class="badge">${escapeHtml(runtimeMode || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Configured" : currentLang() === "mix" ? "配置地址 / Configured" : "配置地址"}: ${escapeHtml(runtime?.configured_url || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Active" : currentLang() === "mix" ? "实际地址 / Active" : "实际地址"}: ${escapeHtml(runtime?.active_url || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Running" : currentLang() === "mix" ? "运行状态 / Running" : "运行状态"}: ${runtime?.running ? yesText : noText} ${runtime?.pid ? `(pid ${runtime.pid})` : ""}</div>
      <div class="mono">${currentLang() === "en" ? "Binary" : currentLang() === "mix" ? "可执行文件 / Binary" : "可执行文件"}: ${escapeHtml(runtime?.binary || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Data dir" : currentLang() === "mix" ? "数据目录 / Data dir" : "数据目录"}: ${escapeHtml(runtime?.data_dir || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Docker CLI" : currentLang() === "mix" ? "Docker CLI / Docker CLI" : "Docker CLI"}: ${escapeHtml(runtime?.docker_cli || "-")} ${runtime?.docker_available ? "" : `(${currentLang() === "en" ? "missing" : currentLang() === "mix" ? "未检测到 / missing" : "未检测到"})`}</div>
      <div class="mono">${currentLang() === "en" ? "Docker daemon" : currentLang() === "mix" ? "Docker daemon / Docker daemon" : "Docker daemon"}: ${runtime?.docker_daemon_available ? yesText : noText}</div>
      <div class="mono">${currentLang() === "en" ? "Docker image" : currentLang() === "mix" ? "Docker 镜像 / Docker image" : "Docker 镜像"}: ${escapeHtml(runtime?.docker_image || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Docker container" : currentLang() === "mix" ? "Docker 容器 / Docker container" : "Docker 容器"}: ${escapeHtml(runtime?.docker_container_name || "-")} ${runtime?.docker_container_exists ? "" : `(${currentLang() === "en" ? "not created" : currentLang() === "mix" ? "未创建 / not created" : "未创建"})`}</div>
      <div class="mono">${currentLang() === "en" ? "Install required" : currentLang() === "mix" ? "需要拉取 / Install required" : "需要拉取"}: ${canInstall ? yesText : noText}</div>
      <div class="mono">${escapeHtml(runtime?.message || "")}</div>
      ${runtime?.suggested_action ? `<div class="mono">${escapeHtml(runtime.suggested_action)}</div>` : ""}
    `;
    const noticeEl = document.getElementById("runtime-action-notice");
    if (noticeEl) {
      const fallbackMessage = runtime?.running && runtime?.active_url
        ? (currentLang() === "en"
          ? `OpenList runtime is ready: ${runtime.active_url}`
          : currentLang() === "mix"
            ? `OpenList runtime 已就绪: ${runtime.active_url} / Runtime ready`
            : `OpenList runtime 已就绪: ${runtime.active_url}`)
        : (currentLang() === "en"
          ? "Runtime status is ready."
          : currentLang() === "mix"
            ? "运行时状态已更新。 / Runtime status is ready."
            : "运行时状态已更新。");
      const waitingTexts = [
        "",
        "等待运行时检查。",
        "Waiting for runtime check.",
        "等待运行时检查。 / Waiting for runtime check.",
        "运行时状态已更新。",
        "Runtime status is ready.",
        "运行时状态已更新。 / Runtime status is ready.",
      ];
      const existing = String(noticeEl.textContent || "").trim();
      if (runtime?.message) {
        noticeEl.textContent = runtime.message;
      } else if (waitingTexts.includes(existing)) {
        noticeEl.textContent = fallbackMessage;
      }
    }
    const installBtn = document.getElementById("install-runtime");
    if (installBtn) {
      installBtn.disabled = !canInstall;
    }
    ctx.applyOpenListModeUi?.();
  }

  function renderCapture(ctx, capture, targetStateSummary = null) {
    const currentLang = ctx.currentLang;
    const escapeHtml = ctx.escapeHtml;
    const captured = capture?.captured || {};
    const missing = !captured.authorization && !captured.access_token && !captured.refresh_token;
    const activeTarget = String(targetStateSummary?.target_key || ctx.activeTargetKey?.() || "guangya");
    const targetFields = Array.isArray(targetStateSummary?.fields) ? targetStateSummary.fields : [];
    const isGuangya = activeTarget === "guangya";
    const nonGuangyaBadge = targetStateSummary?.has_state
      ? (currentLang() === "en" ? "configured" : currentLang() === "mix" ? "已配置 / configured" : "已配置")
      : (currentLang() === "en" ? "empty" : currentLang() === "mix" ? "未配置 / empty" : "未配置");
    const nonGuangyaMessage = currentLang() === "en"
      ? `Current target is ${activeTarget}. Guangya capture details are hidden because this target is not using Guangya auth fields.`
      : currentLang() === "mix"
        ? `当前目标端为 ${activeTarget}，这里不再展示 Guangya 抓取细节，因为该目标端不使用 Guangya 鉴权字段。 / Guangya capture details are hidden.`
        : `当前目标端为 ${activeTarget}，这里不再展示 Guangya 抓取细节，因为该目标端不使用 Guangya 鉴权字段。`;
    const targetStateLine = targetStateSummary
      ? `<div class="mono">${currentLang() === "en" ? "Active target state" : currentLang() === "mix" ? "当前目标端状态 / Active target state" : "当前目标端状态"}: ${escapeHtml(activeTarget)} | ${currentLang() === "en" ? "fields" : currentLang() === "mix" ? "字段 / fields" : "字段"}=${targetStateSummary.field_count ?? 0} | ${escapeHtml(targetFields.join(", ") || "-")}</div>`
      : "";
    document.getElementById("capture-summary").innerHTML = `
      <div class="badge">${escapeHtml(isGuangya ? (capture?.status || "idle") : nonGuangyaBadge)}</div>
      <div class="mono">${escapeHtml(isGuangya ? (capture?.message || "") : nonGuangyaMessage)}</div>
      ${targetStateLine}
      ${isGuangya ? `<div class="mono">Authorization: ${captured.authorization ? (currentLang() === "en" ? "captured" : currentLang() === "mix" ? "已抓取 / captured" : "已抓取") : (currentLang() === "en" ? "missing" : currentLang() === "mix" ? "未抓取 / missing" : "未抓取")}</div>` : ""}
      ${isGuangya ? `<div class="mono">Access Token: ${captured.access_token ? (currentLang() === "en" ? "captured" : currentLang() === "mix" ? "已抓取 / captured" : "已抓取") : (currentLang() === "en" ? "missing" : currentLang() === "mix" ? "未抓取 / missing" : "未抓取")}</div>` : ""}
      ${isGuangya ? `<div class="mono">Refresh Token: ${captured.refresh_token ? (currentLang() === "en" ? "captured" : currentLang() === "mix" ? "已抓取 / captured" : "已抓取") : (currentLang() === "en" ? "missing" : currentLang() === "mix" ? "未抓取 / missing" : "未抓取")}</div>` : ""}
      ${isGuangya && missing ? `<div class="mono">${currentLang() === "en" ? "Hint: click Guangya capture to auto-fill the login data." : currentLang() === "mix" ? "提示 / Hint: 点击光鸭抓取按钮自动回填登录信息。" : "提示: 需要点击“打开光鸭登录并自动抓取”完成自动回填。"}</div>` : ""}
    `;
  }

  window.CloudPanBridgeRuntimeView = {
    renderSync,
    renderRuntime,
    renderCapture,
  };
})();
