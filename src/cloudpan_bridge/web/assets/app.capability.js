(function () {
  function strategyModeText(ctx, mode) {
    const mapping = {
      analyze_first: {
        zh: "先分析再决定",
        en: "Analyze first",
      },
      direct_metadata_first: {
        zh: "优先直接秒传/元数据导入",
        en: "Direct metadata-first sync",
      },
      leaf_metadata_then_pending: {
        zh: "最底层边扫边秒传，再进待补传树",
        en: "Leaf sync first, pending tree next",
      },
      stream_relay_first: {
        zh: "优先中转流传输",
        en: "Relay streaming first",
      },
      pending_tree_first: {
        zh: "优先待补传树分目录补传",
        en: "Pending-tree-first reupload",
      },
      manual_verify_first: {
        zh: "先人工核对能力与登录态",
        en: "Manual verification first",
      },
    };
    const text = mapping[String(mode || "").toLowerCase()] || mapping.analyze_first;
    return ctx.currentLang() === "en" ? text.en : ctx.currentLang() === "mix" ? `${text.zh} / ${text.en}` : text.zh;
  }

  function coverageNextActionText(ctx, action) {
    const mapping = {
      add_profile_first: { zh: "先补 source profile", en: "Add source profile first" },
      add_guide: { zh: "补接入流程说明", en: "Add setup guide" },
      add_capture_spec: { zh: "补登录抓取定义", en: "Add capture spec" },
      assess_target_capability: { zh: "补目标能力判断", en: "Assess target capability" },
      covered: { zh: "当前已覆盖", en: "Already covered" },
    };
    const text = mapping[String(action || "").toLowerCase()] || mapping.add_profile_first;
    return ctx.currentLang() === "en" ? text.en : ctx.currentLang() === "mix" ? `${text.zh} / ${text.en}` : text.zh;
  }

  function strategyQuickActions(ctx, mode, strategy) {
    const actions = [];
    const isGuangya = ctx.activeTargetKey() === "guangya";
    const push = (key, labelZh, labelEn) => actions.push({
      key,
      label: ctx.currentLang() === "en" ? labelEn : ctx.currentLang() === "mix" ? `${labelZh} / ${labelEn}` : labelZh,
    });
    if (strategy?.shouldAnalyzeFirst) push("analyze", "先分析当前目录", "Analyze current directory");
    if (mode === "direct_metadata_first") {
      if (isGuangya) push("to-miaochuan", "去秒传页", "Open flash-upload tab");
      else push("to-execute", "去执行页", "Open execution tab");
      push("run-direct", "直接同步当前目录", "Run direct sync");
    } else if (mode === "leaf_metadata_then_pending") {
      push("run-leaf-direct", "最底层边扫边秒传", "Run leaf scan sync");
      push("to-pending", "查看待补传树", "Open pending tree");
    } else if (mode === "pending_tree_first") {
      push("to-pending", "去补传页", "Open pending tab");
      push("run-leaf-full", "最底层边扫边同步+补传", "Run leaf sync with fallback");
    } else if (mode === "stream_relay_first") {
      push("to-execute", "去执行页", "Open execution tab");
      push("run-direct", "直接同步当前目录", "Run direct sync");
    } else if (mode === "manual_verify_first") {
      push("to-mounts", "去挂载与驱动说明", "Open mounts and guides");
      push("to-about", "查看能力矩阵说明", "Open capability reference");
    }
    return actions;
  }

  function performCapabilityQuickAction(ctx, actionKey) {
    const actions = {
      analyze: () => {
        ctx.activateTab("source");
        document.getElementById("analyze-source")?.click();
      },
      "to-miaochuan": () => ctx.activateTab("miaochuan"),
      "to-pending": () => ctx.activateTab("pending"),
      "to-task": () => ctx.activateTab("task"),
      "to-execute": () => ctx.activateTab("execute"),
      "to-mounts": () => ctx.activateTab("mounts"),
      "to-about": () => ctx.activateTab("about"),
      "run-direct": () => {
        ctx.activateTab("execute");
        document.getElementById("run-direct")?.click();
      },
      "run-leaf-direct": () => {
        ctx.activateTab("execute");
        document.getElementById("run-leaf-direct")?.click();
      },
      "run-leaf-full": () => {
        ctx.activateTab("execute");
        document.getElementById("run-leaf-full")?.click();
      },
    };
    actions[actionKey]?.();
  }

  window.CloudPanBridgeCapabilityView = {
    strategyModeText,
    coverageNextActionText,
    strategyQuickActions,
    performCapabilityQuickAction,
  };
})();
