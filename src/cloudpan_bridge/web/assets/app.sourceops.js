(function () {
  function renderDirectoryBrowser(ctx, data) {
    ctx.setCurrentDirectory(data?.path || "/", data?.parent_path || null);
    const currentPath = ctx.getCurrentDirectoryPath();
    document.getElementById("dir-current").textContent = `当前浏览: ${currentPath}`;
    ctx.setGroupedConfigValue(["ui", "browser", "current_path"], currentPath || "/");
    ctx.setGroupedConfigValue(["ui", "browser", "current_parent_path"], ctx.getCurrentParentPath() || "");
    ctx.scheduleUiPrefsPersist();
    ctx.renderSourceDriverSummary();
    const root = document.getElementById("dir-browser-list");
    const dirs = Array.isArray(data?.directories) ? data.directories : [];
    if (!dirs.length) {
      root.innerHTML = `<div class="subtle">这个目录下没有子目录，可以直接把它设为同步源目录。</div>`;
      return;
    }
    root.innerHTML = dirs.map((item) => `
      <div class="row-item">
        <div>
          <div>${ctx.escapeHtml(item.name || "")}</div>
          <div class="mono">${ctx.escapeHtml(item.path || "")}</div>
        </div>
        <button class="secondary" data-open-dir="${ctx.escapeHtml(item.path || "/")}">进入</button>
      </div>
    `).join("");
    root.querySelectorAll("[data-open-dir]").forEach((button) => {
      button.addEventListener("click", async () => {
        await ctx.browseDirectory(button.getAttribute("data-open-dir") || "/");
      });
    });
  }

  function renderMiaochuanDiagnosis(ctx, data) {
    const root = document.getElementById("miaochuan-diagnosis");
    if (!data) {
      root.textContent = ctx.currentLang() === "en"
        ? "No diagnosis result"
        : ctx.currentLang() === "mix"
          ? "暂无诊断结果 / No diagnosis result"
          : "暂无诊断结果";
      return;
    }
    const providerCounts = Object.entries(data.provider_counts || {})
      .map(([key, value]) => `${key}: ${value}`)
      .join(" | ") || "-";
    const sample = Array.isArray(data.sample) ? data.sample : [];
    root.innerHTML = `
      <div class="row-item">
        <div>
          <div>${ctx.currentLang() === "en" ? "Flash Upload JSON Diagnosis" : ctx.currentLang() === "mix" ? "秒传 JSON 诊断 / Flash Upload JSON Diagnosis" : "秒传 JSON 诊断"}</div>
          <div class="mono">${ctx.currentLang() === "en" ? "Total files" : ctx.currentLang() === "mix" ? "文件总数 / Total files" : "文件总数"}: ${data.total ?? 0}</div>
          <div class="mono">${ctx.currentLang() === "en" ? "Total size" : ctx.currentLang() === "mix" ? "总大小 / Total size" : "总大小"}: ${ctx.formatBytes(data.total_size || 0)}</div>
          <div class="mono">MD5: ${data.md5_count ?? 0} | GCID: ${data.gcid_count ?? 0}</div>
          <div class="mono">provider: ${ctx.escapeHtml(providerCounts)}</div>
        </div>
      </div>
      ${sample.map((item) => `
        <div class="row-item">
          <div>
            <div>${ctx.escapeHtml(item.path || "-")}</div>
            <div class="mono">provider=${ctx.escapeHtml(item.provider || "unknown")} | hashType=${ctx.escapeHtml(item.hashType || "-")} | size=${ctx.formatBytes(item.size || 0)}</div>
            <div class="mono">md5=${ctx.escapeHtml(item.etag || "-")} | gcid=${ctx.escapeHtml(item.gcid || "-")}</div>
          </div>
        </div>
      `).join("")}
      ${sample.length === 0 ? `<div class="subtle">${ctx.currentLang() === "en" ? "No sample rows available." : ctx.currentLang() === "mix" ? "没有可展示的样本行。 / No sample rows available." : "没有可展示的样本行。"}</div>` : ""}
    `;
  }

  function populateMountedSources(ctx, items) {
    const select = document.getElementById("mounted_source_select");
    const list = Array.isArray(items) ? items : [];
    if (!list.length) {
      select.innerHTML = `<option value="">${ctx.currentLang() === "en" ? "No mounts" : ctx.currentLang() === "mix" ? "暂无挂载 / No mounts" : "暂无挂载"}</option>`;
      return;
    }
    const sourcePath = String(document.getElementById("source_path").value || "").trim();
    const mountedSource = String(ctx.getGroupedConfigValue(["ui", "browser", "mounted_source"], "") || "").trim();
    select.innerHTML = list.map((item) => {
      const mountPath = item.mount_path || item.mountPath || item.path || "/";
      const driver = item.driver || item.driver_name || item.driverName || "-";
      const selected = mountedSource
        ? (mountedSource === String(mountPath) ? "selected" : "")
        : (sourcePath.startsWith(String(mountPath)) ? "selected" : "");
      return `<option value="${ctx.escapeHtml(mountPath)}" ${selected}>${ctx.escapeHtml(mountPath)} | ${ctx.escapeHtml(driver)}</option>`;
    }).join("");
  }

  function renderQueue(ctx, items) {
    const root = document.getElementById("queue-list");
    const list = Array.isArray(items) ? items : [];
    if (!list.length) {
      root.textContent = ctx.currentLang() === "en" ? "No queued directories" : ctx.currentLang() === "mix" ? "暂无目录队列 / No queued directories" : "暂无目录队列";
      return;
    }
    root.innerHTML = list.map((item) => `
      <div class="row-item">
        <div>
          <div>${ctx.escapeHtml(item.source_path)}</div>
          <div class="mono">${ctx.currentLang() === "en" ? "Status" : ctx.currentLang() === "mix" ? "状态 / Status" : "状态"}: ${ctx.escapeHtml(item.last_status || "idle")} ${item.last_run_at ? `| ${ctx.currentLang() === "en" ? "Last run" : ctx.currentLang() === "mix" ? "上次 / Last run" : "上次"}: ${ctx.escapeHtml(item.last_run_at)}` : ""}</div>
        </div>
        <button class="secondary" data-remove-queue="${ctx.escapeHtml(item.source_path)}">${ctx.currentLang() === "en" ? "Remove" : ctx.currentLang() === "mix" ? "移除 / Remove" : "移除"}</button>
      </div>
    `).join("");
    root.querySelectorAll("[data-remove-queue]").forEach((button) => {
      button.addEventListener("click", async () => {
        await ctx.call("/api/queue/remove", {
          method: "POST",
          body: JSON.stringify({ source_path: button.getAttribute("data-remove-queue") || "" }),
        });
        await ctx.refreshStatus();
      });
    });
  }

  function renderStorages(ctx, payload) {
    const root = document.getElementById("storage-list");
    const content = payload?.data?.content || payload?.data || [];
    const list = Array.isArray(content) ? content : [];
    ctx.setStorageRecords(list);
    populateMountedSources(ctx, list);
    const selectedMount = document.getElementById("mounted_source_select")?.value || "";
    const selectedStorage = list.find((item) => String(item.mount_path || item.mountPath || item.path || "/") === String(selectedMount));
    if (selectedStorage) ctx.applyProviderSelectionFromDriver(selectedStorage.driver || selectedStorage.driver_name || selectedStorage.driverName || "");
    if (!list.length) {
      root.textContent = ctx.currentLang() === "en" ? "No mounts" : ctx.currentLang() === "mix" ? "暂无挂载 / No mounts" : "暂无挂载";
      ctx.renderCapabilitySummary();
      ctx.applyWorkflowGates();
      return;
    }
    root.innerHTML = list.map((item) => {
      const mountPath = item.mount_path || item.mountPath || item.path || "/";
      const driver = item.driver || item.driver_name || item.driverName || "-";
      return `
        <div class="row-item">
          <div>
            <div>${ctx.escapeHtml(mountPath)}</div>
            <div class="mono">driver: ${ctx.escapeHtml(driver)} | ${ctx.currentLang() === "en" ? "status" : ctx.currentLang() === "mix" ? "状态 / status" : "状态"}: ${ctx.escapeHtml(String(item.status ?? "-"))}</div>
          </div>
        </div>
      `;
    }).join("");
    ctx.renderCapabilitySummary();
    ctx.applyWorkflowGates();
  }

  function renderDriverFields(ctx, info) {
    ctx.setCurrentDriverInfo(info);
    const fields = [...(info?.common || []), ...(info?.additional || [])];
    const root = document.getElementById("driver-fields");
    document.getElementById("driver-notice").textContent = ctx.currentLang() === "en"
      ? `${info?.name || "-"}: ${fields.length} fields generated from OpenList driver metadata.`
      : ctx.currentLang() === "mix"
        ? `${info?.name || "-"}：共 ${fields.length} 个字段 / ${fields.length} fields generated from OpenList driver metadata.`
        : `${info?.name || "-"}：共 ${fields.length} 个字段，已按 OpenList 驱动描述动态生成。`;
    root.innerHTML = fields.map((field) => {
      const type = String(field.type || "string").toLowerCase();
      const id = `driver-field-${field.name}`;
      if (type === "bool") {
        return `
          <div>
            <label>${ctx.escapeHtml(ctx.driverFieldLabel(field.name))} ${field.required ? (ctx.currentLang() === "en" ? "(Required)" : ctx.currentLang() === "mix" ? "(必填 / Required)" : "(必填)") : ""}</label>
            <select id="${ctx.escapeHtml(id)}" data-driver-field="${ctx.escapeHtml(field.name)}">
              <option value="">${ctx.currentLang() === "en" ? "Default" : ctx.currentLang() === "mix" ? "默认 / Default" : "默认"}</option>
              <option value="true" ${String(field.default) === "True" || String(field.default) === "true" ? "selected" : ""}>${ctx.currentLang() === "en" ? "true" : ctx.currentLang() === "mix" ? "是 / true" : "是"}</option>
              <option value="false" ${String(field.default) === "False" || String(field.default) === "false" ? "selected" : ""}>${ctx.currentLang() === "en" ? "false" : ctx.currentLang() === "mix" ? "否 / false" : "否"}</option>
            </select>
            <div class="mono">${ctx.escapeHtml(ctx.driverFieldHelp(field.help || ""))}</div>
          </div>
        `;
      }
      return `
        <div>
          <label>${ctx.escapeHtml(ctx.driverFieldLabel(field.name))} ${field.required ? (ctx.currentLang() === "en" ? "(Required)" : ctx.currentLang() === "mix" ? "(必填 / Required)" : "(必填)") : ""}</label>
          <input id="${ctx.escapeHtml(id)}" data-driver-field="${ctx.escapeHtml(field.name)}" value="${ctx.escapeHtml(field.default || "")}">
          <div class="mono">${ctx.escapeHtml(ctx.driverFieldHelp(field.help || "") || ctx.driverFieldOptions(field.options || "") || String(field.options || ""))}</div>
        </div>
      `;
    }).join("");
    ctx.renderDriverGuide(info?.name || "");
    ctx.renderProviderCapturePanel();
    ctx.renderCapabilitySummary();
  }

  window.CloudPanBridgeSourceOps = {
    renderDirectoryBrowser,
    renderMiaochuanDiagnosis,
    populateMountedSources,
    renderQueue,
    renderStorages,
    renderDriverFields,
  };
})();
