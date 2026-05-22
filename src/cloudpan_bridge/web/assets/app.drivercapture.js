(function () {
  function maskValue(value) {
    const text = String(value || "");
    if (!text) return "";
    if (text.length <= 12) return `${text.slice(0, 2)}***${text.slice(-2)}`;
    return `${text.slice(0, 6)}***${text.slice(-4)}`;
  }

  function fieldStatus(ctx, value) {
    if (value) return ctx.currentLang() === "en" ? "captured" : ctx.currentLang() === "mix" ? "已抓取 / captured" : "已抓取";
    return ctx.currentLang() === "en" ? "missing" : ctx.currentLang() === "mix" ? "未抓取 / missing" : "未抓取";
  }

  function chooseRatePreset(ctx, driver, mode) {
    const normalizedDriver = String(driver || "").toLowerCase();
    if (mode === "custom") return null;
    for (const [key, preset] of Object.entries(ctx.RATE_PRESETS || {})) {
      if (key === "default" || key === "safe" || key === "balanced" || key === "fast") continue;
      if (normalizedDriver.includes(key)) return preset;
    }
    return ctx.RATE_PRESETS?.[mode] || ctx.RATE_PRESETS?.default || null;
  }

  function getDriverGuide(ctx, driver) {
    const normalized = ctx.normalizeDriverKey(driver);
    const blueprint = ctx.getDriverCaptureBlueprint();
    if (blueprint?.driver && ctx.normalizeDriverKey(blueprint.driver) === normalized && blueprint.guide) {
      return blueprint.guide;
    }
    const registry = ctx.getDriverGuideRegistry();
    return registry[normalized] || null;
  }

  function getGuideForProviderDefinition(ctx, definition) {
    if (definition?.guide) return definition.guide;
    const sourceProfile = definition?.source_profile || {};
    const aliases = Array.isArray(sourceProfile.driverAliases) ? sourceProfile.driverAliases : [];
    const recommendedDrivers = Array.isArray(definition?.recommended_drivers) ? definition.recommended_drivers : [];
    const candidates = [...recommendedDrivers, ...aliases, sourceProfile.key || "", definition?.key || ""];
    for (const item of candidates) {
      const guide = getDriverGuide(ctx, item);
      if (guide) return guide;
    }
    return null;
  }

  function guideDocCandidates(_ctx, guide) {
    const list = Array.isArray(guide?.docUrlCandidates) ? guide.docUrlCandidates : [];
    const merged = [];
    if (guide?.docUrl) merged.push(guide.docUrl);
    merged.push(...list);
    return [...new Set(merged.map((item) => String(item || "").trim()).filter(Boolean))];
  }

  function renderGuideIntoDialog(ctx, guide, titleText) {
    ctx.setCurrentDriverGuide(guide);
    const summary = document.getElementById("driver-guide-summary");
    const stepsRoot = document.getElementById("driver-guide-steps");
    const title = document.getElementById("driver-guide-title");
    const openDocButton = document.getElementById("open-driver-doc");
    const candidatesRoot = document.getElementById("driver-guide-doc-candidates");
    if (!guide) {
      const empty = ctx.currentLang() === "en"
        ? "This provider currently has no built-in special guide. You can still use the captured fields and the official docs manually."
        : ctx.currentLang() === "mix"
          ? "当前 provider 暂无内置专属流程说明，可先用抓取结果与动态字段，再手动参考官方文档。 / No built-in special guide yet."
          : "当前 provider 暂无内置专属流程说明，可先用抓取结果与动态字段，再手动参考官方文档。";
      if (summary) summary.textContent = empty;
      if (stepsRoot) stepsRoot.innerHTML = "";
      if (candidatesRoot) {
        candidatesRoot.textContent = ctx.currentLang() === "en"
          ? "No official doc candidates yet."
          : ctx.currentLang() === "mix"
            ? "当前没有官方文档候选链路。 / No official doc candidates yet."
            : "当前没有官方文档候选链路。";
      }
      if (title) {
        title.textContent = titleText || (ctx.currentLang() === "en" ? "Provider Access Guide" : ctx.currentLang() === "mix" ? "网盘接入流程 / Provider Access Guide" : "网盘接入流程");
      }
      if (openDocButton) openDocButton.disabled = true;
      return;
    }
    const summaryText = ctx.guideTextPair(guide.summary);
    if (summary) summary.textContent = summaryText;
    if (title) {
      title.textContent = titleText || (ctx.currentLang() === "en" ? "Provider Access Guide" : ctx.currentLang() === "mix" ? "网盘接入流程 / Provider Access Guide" : "网盘接入流程");
    }
    const zhSteps = Array.isArray(guide.steps?.zh) ? guide.steps.zh : [];
    const enSteps = Array.isArray(guide.steps?.en) ? guide.steps.en : [];
    const steps = ctx.currentLang() === "en" ? enSteps : ctx.currentLang() === "mix" ? zhSteps.map((item, index) => `${item}\n\n${enSteps[index] || ""}`) : zhSteps;
    if (stepsRoot) {
      stepsRoot.innerHTML = steps.map((item, index) => `
        <div class="guide-step">
          <strong>${index + 1}.</strong> ${ctx.escapeHtml(item)}
        </div>
      `).join("");
    }
    const candidates = guideDocCandidates(ctx, guide);
    if (candidatesRoot) {
      candidatesRoot.innerHTML = candidates.length
        ? `
          <div style="margin-bottom:8px;">${ctx.currentLang() === "en" ? "Official doc candidates" : ctx.currentLang() === "mix" ? "官方文档候选 / Official doc candidates" : "官方文档候选"}</div>
          ${candidates.map((item, index) => `<div class="mono"><a href="${ctx.escapeHtml(item)}" target="_blank" rel="noopener noreferrer">${ctx.escapeHtml(index === 0 ? item : `${index + 1}. ${item}`)}</a></div>`).join("")}
        `
        : (ctx.currentLang() === "en"
          ? "No official doc candidates yet."
          : ctx.currentLang() === "mix"
            ? "当前没有官方文档候选链路。 / No official doc candidates yet."
            : "当前没有官方文档候选链路。");
    }
    if (openDocButton) openDocButton.disabled = !candidates.length;
  }

  function renderDriverGuide(ctx, driver) {
    const guide = getDriverGuide(ctx, driver);
    ctx.setCurrentDriverGuide(guide);
    const inline = document.getElementById("driver-guide-inline");
    if (!guide) {
      const empty = ctx.currentLang() === "en"
        ? "This driver currently has no built-in special guide. You can still use the dynamic fields below or check the OpenList docs manually."
        : ctx.currentLang() === "mix"
          ? "当前驱动暂时没有内置专属流程说明，可先用下方动态字段，也可以手动查 OpenList 文档。 / No built-in special guide yet."
          : "当前驱动暂时没有内置专属流程说明，可先用下方动态字段，也可以手动查 OpenList 文档。";
      if (inline) inline.textContent = empty;
      renderGuideIntoDialog(ctx, null, ctx.currentLang() === "en" ? "Driver Access Guide" : ctx.currentLang() === "mix" ? "驱动接入流程 / Driver Access Guide" : "驱动接入流程");
      return;
    }
    const summaryText = ctx.guideTextPair(guide.summary);
    if (inline) {
      inline.innerHTML = `
        <div>${ctx.escapeHtml(summaryText)}</div>
        <div class="mono">${ctx.currentLang() === "en" ? "Official doc" : ctx.currentLang() === "mix" ? "官方文档 / Official doc" : "官方文档"}: ${ctx.escapeHtml(guide.docUrl || "")}</div>
      `;
    }
    renderGuideIntoDialog(ctx, guide, `${driver} ${ctx.currentLang() === "en" ? "Guide" : ctx.currentLang() === "mix" ? "接入流程 / Guide" : "接入流程"}`);
  }

  function applyDriverGuideDefaults(ctx) {
    const currentDriverGuide = ctx.getCurrentDriverGuide();
    if (!currentDriverGuide?.defaults) {
      ctx.setNotice("driver-notice", ctx.currentLang() === "en"
        ? "No built-in recommended defaults for this driver."
        : ctx.currentLang() === "mix"
          ? "当前驱动没有内置推荐默认值。 / No built-in recommended defaults."
          : "当前驱动没有内置推荐默认值。");
      return;
    }
    let changed = 0;
    const inputs = [...document.querySelectorAll("[data-driver-field]")];
    for (const [fieldName, value] of Object.entries(currentDriverGuide.defaults)) {
      const input = inputs.find((item) => ctx.normalizeDriverKey(item.getAttribute("data-driver-field") || "") === ctx.normalizeDriverKey(fieldName));
      if (input) {
        input.value = String(value);
        changed += 1;
      }
    }
    ctx.setNotice("driver-notice", ctx.currentLang() === "en"
      ? `Applied ${changed} recommended default values.`
      : ctx.currentLang() === "mix"
        ? `已套用 ${changed} 个推荐默认值。 / Applied ${changed} recommended defaults.`
        : `已套用 ${changed} 个推荐默认值。`);
  }

  function toggleDriverGuideDialog(_ctx, visible) {
    const dialog = document.getElementById("driver-guide-dialog");
    if (!dialog) return;
    dialog.classList.toggle("hidden", !visible);
  }

  function inferProviderFromDriver(ctx, driver) {
    const text = String(driver || "").toLowerCase();
    const definitions = ctx.getProviderDefinitions();
    const fromDefinitions = definitions.find((item) => {
      const list = Array.isArray(item?.recommended_drivers) ? item.recommended_drivers : [];
      return list.some((name) => String(name || "").toLowerCase() === text);
    });
    if (fromDefinitions?.key) return fromDefinitions.key;
    if (!text) return "189cloud";
    if (text.includes("quark")) return "quark";
    if (text.includes("123")) return "123pan";
    if (text.includes("baidu")) return "baidu";
    if (text.includes("thunder") || text.includes("xunlei")) return "thunder";
    if (text.includes("189")) return "189cloud";
    if (text.includes("aliyun") || text.includes("alipan")) return "aliyundriveopen";
    if (text.includes("onedrive")) return "onedrive";
    if (text.includes("pikpak")) return "pikpak";
    if (text.includes("139")) return "139yun";
    if (text.includes("guangya")) return "guangya";
    const blueprint = ctx.getDriverCaptureBlueprint();
    if (blueprint?.key) return blueprint.key;
    return "189cloud";
  }

  function renderProviderOptions(ctx, definitions) {
    const select = document.getElementById("provider-select");
    if (!select) return;
    const items = [...(Array.isArray(definitions) ? definitions : [])];
    const blueprint = ctx.getDriverCaptureBlueprint();
    if (blueprint?.key && !items.some((item) => item.key === blueprint.key)) {
      items.push(blueprint);
    }
    if (!items.length) {
      select.innerHTML = `<option value="">${ctx.currentLang() === "en" ? "No providers" : ctx.currentLang() === "mix" ? "暂无 provider / No providers" : "暂无 provider"}</option>`;
      return;
    }
    const current = select.value || inferProviderFromDriver(ctx, document.getElementById("driver-select")?.value || "");
    select.innerHTML = items.map((item) => {
      const selected = item.key === current ? "selected" : "";
      const profile = item.source_profile || {};
      const zh = String(profile.label_zh || item.label_zh || item.labelZh || item.label || item.key || "");
      const en = String(profile.label || item.label || item.key || zh || "");
      const label = ctx.currentLang() === "en" ? en : ctx.currentLang() === "mix" ? `${zh} / ${en}` : zh;
      return `<option value="${ctx.escapeHtml(item.key)}" ${selected}>${ctx.escapeHtml(label)}</option>`;
    }).join("");
  }

  function renderProviderCapturePanel(ctx) {
    const select = document.getElementById("provider-select");
    if (!select) return;
    const items = [...ctx.getProviderDefinitions()];
    const blueprint = ctx.getDriverCaptureBlueprint();
    if (blueprint?.key && !items.some((item) => item.key === blueprint.key)) {
      items.push(blueprint);
    }
    const provider = select.value || items[0]?.key || "189cloud";
    const definition = items.find((item) => item.key === provider);
    const currentProviderGuide = getGuideForProviderDefinition(ctx, definition);
    ctx.setCurrentProviderGuide(currentProviderGuide);
    const snapshots = ctx.getProviderSnapshots();
    const snapshot = snapshots?.[provider] || {};
    const captured = snapshot.captured || {};
    const captureMode = String(definition?.capture_mode || "browser");
    const requiredKeys = Array.isArray(definition?.required_keys) ? definition.required_keys : [];
    const recommended = Array.isArray(definition?.recommended_drivers) && definition.recommended_drivers.length
      ? definition.recommended_drivers
      : (ctx.PROVIDER_DRIVER_HINTS?.[provider] || []);
    const profile = definition?.source_profile || {};
    const loginModeText = ctx.currentLang() === "en"
      ? (profile.login_mode || profile.loginMode || "")
      : ctx.currentLang() === "mix"
        ? `${profile.login_mode || profile.loginMode || ""} / ${profile.login_mode || profile.loginMode || ""}`.trim()
        : (profile.login_mode || profile.loginMode || "");
    const hashText = Array.isArray(profile.hash_fields_supported || profile.hashFieldsSupported) ? (profile.hash_fields_supported || profile.hashFieldsSupported).join(", ") : "";
    const docLinks = Array.isArray(profile.doc_links || profile.docLinks) ? (profile.doc_links || profile.docLinks) : [];
    const rateText = profile.recommended_rate_profile || profile.recommendedRateProfile || "";
    const lines = requiredKeys.length
      ? requiredKeys.map((key) => `<div class="mono">${ctx.escapeHtml(key)}: ${fieldStatus(ctx, captured[key])}${captured[key] ? ` | ${ctx.escapeHtml(maskValue(captured[key]))}` : ""}</div>`).join("")
      : `<div class="mono">${ctx.currentLang() === "en" ? "No required fields declared." : ctx.currentLang() === "mix" ? "未声明必需字段 / No required fields declared." : "未声明必需字段。"}</div>`;
    document.getElementById("provider-driver-hint").innerHTML = `
      <div>${ctx.escapeHtml(definition?.description || "")}</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Login URL" : ctx.currentLang() === "mix" ? "登录地址 / Login URL" : "登录地址"}: ${ctx.escapeHtml(definition?.login_url || "-")}</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Recommended drivers" : ctx.currentLang() === "mix" ? "建议驱动 / Recommended drivers" : "建议驱动"}: ${ctx.escapeHtml(recommended.join(", ") || "-")}</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Login mode" : ctx.currentLang() === "mix" ? "登录模式 / Login mode" : "登录模式"}: ${ctx.escapeHtml(loginModeText || "-")}</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Recommended rate" : ctx.currentLang() === "mix" ? "推荐频率 / Recommended rate" : "推荐频率"}: ${ctx.escapeHtml(rateText || "-")}</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Hash fields" : ctx.currentLang() === "mix" ? "哈希字段 / Hash fields" : "哈希字段"}: ${ctx.escapeHtml(hashText || "-")}</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Docs" : ctx.currentLang() === "mix" ? "文档 / Docs" : "文档"}: ${docLinks.length ? docLinks.map((link) => `<a href="${ctx.escapeHtml(link)}" target="_blank" rel="noreferrer">${ctx.escapeHtml(link)}</a>`).join("<br>") : "-"}</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Built-in guide" : ctx.currentLang() === "mix" ? "内置流程说明 / Built-in guide" : "内置流程说明"}: ${currentProviderGuide ? (ctx.currentLang() === "en" ? "available" : ctx.currentLang() === "mix" ? "可查看 / available" : "可查看") : (ctx.currentLang() === "en" ? "not available" : ctx.currentLang() === "mix" ? "暂无 / not available" : "暂无")}</div>
    `;
    const loginUrlInput = document.getElementById("provider-login-url");
    if (loginUrlInput) {
      loginUrlInput.value = definition?.login_url || "";
    }
    const startButton = document.getElementById("start-provider-capture");
    if (startButton) {
      startButton.textContent = captureMode === "manual"
        ? (ctx.currentLang() === "en"
          ? "Open guide / manual credentials"
          : ctx.currentLang() === "mix"
            ? "查看说明并手动填写 / Open guide"
            : "查看说明并手动填写")
        : ctx.t("btn.start_provider_capture");
    }
    document.getElementById("provider-capture-summary").innerHTML = `
      <div class="badge">${ctx.escapeHtml(snapshot.status || "idle")}</div>
      <div class="mono">${ctx.escapeHtml(snapshot.message || "")}</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Capture mode" : ctx.currentLang() === "mix" ? "接入模式 / Capture mode" : "接入模式"}: ${ctx.escapeHtml(captureMode === "manual" ? (ctx.currentLang() === "en" ? "manual credentials" : ctx.currentLang() === "mix" ? "手动凭证 / manual credentials" : "手动凭证") : (ctx.currentLang() === "en" ? "browser capture" : ctx.currentLang() === "mix" ? "网页登录抓取 / browser capture" : "网页登录抓取"))}</div>
      ${lines}
      ${captured.cookie_header ? `<div class="mono">cookie_header: ${ctx.escapeHtml(maskValue(captured.cookie_header))}</div>` : ""}
    `;
  }

  function applyProviderSelectionFromDriver(ctx, driver) {
    const select = document.getElementById("provider-select");
    if (!select) return;
    const provider = inferProviderFromDriver(ctx, driver);
    if ([...select.options].some((item) => item.value === provider)) {
      select.value = provider;
      renderProviderCapturePanel(ctx);
    }
    ctx.renderCapabilitySummary();
  }

  async function applyCapturedProviderFields(ctx) {
    const provider = document.getElementById("provider-select")?.value || "";
    const driver = document.getElementById("driver-select")?.value || "";
    const data = await ctx.call("/api/provider/capture/prefill", {
      method: "POST",
      body: JSON.stringify({ provider, driver }),
    });
    const values = data?.values || {};
    let changed = 0;
    document.querySelectorAll("[data-driver-field]").forEach((el) => {
      const fieldName = el.getAttribute("data-driver-field") || "";
      const nextValue = values[fieldName] || "";
      if (nextValue && !el.value) {
        el.value = nextValue;
        changed += 1;
      }
    });
    const missingRequired = Array.isArray(data?.missing_required) ? data.missing_required : [];
    const missingText = missingRequired.length
      ? (ctx.currentLang() === "en"
        ? ` Missing required fields: ${missingRequired.join(", ")}`
        : ctx.currentLang() === "mix"
          ? ` 缺少必填字段 / Missing required fields: ${missingRequired.join(", ")}`
          : ` 缺少必填字段: ${missingRequired.join(", ")}`)
      : "";
    ctx.setNotice(
      "driver-notice",
      changed
        ? (ctx.currentLang() === "en"
          ? `Applied ${changed} captured values to the mount form.${missingText}`
          : ctx.currentLang() === "mix"
            ? `已写入 ${changed} 个抓取字段 / Applied ${changed} values.${missingText}`
            : `已写入 ${changed} 个抓取字段到当前挂载表单。${missingText}`)
        : (ctx.currentLang() === "en"
          ? `No matching captured values were found for the current mount form.${missingText}`
          : ctx.currentLang() === "mix"
            ? `当前挂载表单没有可匹配字段 / No matching captured values were found.${missingText}`
            : `当前挂载表单没有可匹配的抓取字段。${missingText}`)
    );
  }

  function applyRatePresetForMount(ctx, mountPath) {
    const mode = String(document.getElementById("rate_limit_mode")?.value || "safe");
    if (mode === "custom") return;
    const selected = ctx.getStorageRecords().find((item) => {
      const current = item.mount_path || item.mountPath || item.path || "/";
      return String(current) === String(mountPath);
    });
    const driver = selected?.driver || selected?.driver_name || selected?.driverName || "";
    const preset = chooseRatePreset(ctx, driver, mode);
    if (!preset) return;
    document.getElementById("openlist_page_size").value = String(preset.openlist_page_size);
    document.getElementById("openlist_request_interval_ms").value = String(preset.openlist_request_interval_ms);
    document.getElementById("queue_interval_ms").value = String(preset.queue_interval_ms);
    ctx.setNotice("sync-notice", `已按 ${driver || "默认驱动"} 应用 ${mode} 频率策略。`);
  }

  window.CloudPanBridgeDriverCapture = {
    getDriverGuide,
    getGuideForProviderDefinition,
    guideDocCandidates,
    renderGuideIntoDialog,
    renderDriverGuide,
    applyDriverGuideDefaults,
    toggleDriverGuideDialog,
    chooseRatePreset,
    inferProviderFromDriver,
    renderProviderOptions,
    renderProviderCapturePanel,
    applyProviderSelectionFromDriver,
    applyCapturedProviderFields,
    applyRatePresetForMount,
  };
})();
