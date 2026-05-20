(function () {
  function renderAboutRegistry(ctx) {
    const summaryRoot = document.getElementById("about-summary");
    const sourceRoot = document.getElementById("about-source-profiles");
    const targetRoot = document.getElementById("about-target-profiles");
    const matrixRoot = document.getElementById("about-driver-matrix");
    const coverageRoot = document.getElementById("about-coverage-audit");
    const coverageBacklogRoot = document.getElementById("about-coverage-backlog");
    const coverageActionStatsRoot = document.getElementById("about-coverage-action-stats");
    const coveragePlanRoot = document.getElementById("about-coverage-plan");
    if (!summaryRoot || !sourceRoot || !targetRoot || !matrixRoot || !coverageRoot || !coverageBacklogRoot || !coverageActionStatsRoot || !coveragePlanRoot) return;
    const providerRegistryPayload = ctx.getProviderRegistryPayload();
    const coverageAuditCache = ctx.getCoverageAuditCache();
    const sourceProfiles = Object.values(providerRegistryPayload?.source_profiles || {});
    const targetProfiles = Object.values(providerRegistryPayload?.target_profiles || {});
    const driverMatrix = Object.values(providerRegistryPayload?.driver_matrix || {});
    summaryRoot.innerHTML = `
      <div><strong>CloudPan Bridge</strong></div>
      <div class="mono">${ctx.currentLang() === "en" ? "Master plan" : ctx.currentLang() === "mix" ? "主计划 / Master plan" : "主计划"}: docs/cloudpan-bridge-master-plan.md</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Research plan" : ctx.currentLang() === "mix" ? "调研计划 / Research plan" : "调研计划"}: docs/cloudpan-bridge-research-plan.md</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Source profiles" : ctx.currentLang() === "mix" ? "源端 profiles / Source profiles" : "源端 profiles"}: ${sourceProfiles.length}</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Target profiles" : ctx.currentLang() === "mix" ? "目标端 profiles / Target profiles" : "目标端 profiles"}: ${targetProfiles.length}</div>
      <div class="mono">${ctx.currentLang() === "en" ? "Driver matrix rows" : ctx.currentLang() === "mix" ? "矩阵条目 / Driver matrix rows" : "矩阵条目"}: ${driverMatrix.length}</div>
    `;

    if (!sourceProfiles.length) {
      sourceRoot.textContent = ctx.currentLang() === "en" ? "No source profiles loaded." : ctx.currentLang() === "mix" ? "暂无源端 profiles / No source profiles loaded." : "暂无源端 profiles";
    } else {
      sourceRoot.innerHTML = sourceProfiles.map((item) => `
        <div class="row-item">
          <div>
            <div>${ctx.escapeHtml(item.labelZh || item.label || item.key || "-")}</div>
            <div class="mono">key=${ctx.escapeHtml(item.key || "-")} | ${ctx.currentLang() === "en" ? "rate" : ctx.currentLang() === "mix" ? "频率 / rate" : "频率"}=${ctx.escapeHtml(item.recommendedRateProfile || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "login mode" : ctx.currentLang() === "mix" ? "登录模式 / login mode" : "登录模式"}=${ctx.escapeHtml(item.loginMode || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "hashes" : ctx.currentLang() === "mix" ? "哈希 / hashes" : "哈希"}=${ctx.escapeHtml((item.likelyHashes || []).join(", ") || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "supported hash fields" : ctx.currentLang() === "mix" ? "支持哈希字段 / supported hash fields" : "支持哈希字段"}=${ctx.escapeHtml((item.hashFieldsSupported || []).join(", ") || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "fingerprint enrichment" : ctx.currentLang() === "mix" ? "补指纹能力 / fingerprint enrichment" : "补指纹能力"}=${item.supportsFingerprintEnrichment ? (ctx.currentLang() === "en" ? "declared" : ctx.currentLang() === "mix" ? "已声明 / declared" : "已声明") : (ctx.currentLang() === "en" ? "unknown" : ctx.currentLang() === "mix" ? "未知 / unknown" : "未知")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "download links" : ctx.currentLang() === "mix" ? "下载链路 / download links" : "下载链路"}=${ctx.escapeHtml(item.downloadLinkSupported || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "aliases" : ctx.currentLang() === "mix" ? "驱动别名 / aliases" : "驱动别名"}=${ctx.escapeHtml((item.driverAliases || []).join(", ") || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "capture strategy" : ctx.currentLang() === "mix" ? "抓取策略 / capture strategy" : "抓取策略"}=${ctx.escapeHtml((ctx.currentLang() === "en" ? item.captureStrategyEn : ctx.currentLang() === "mix" ? `${item.captureStrategy || ""} / ${item.captureStrategyEn || ""}`.trim() : item.captureStrategy) || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "default mount values" : ctx.currentLang() === "mix" ? "默认挂载值 / default mount values" : "默认挂载值"}=${ctx.escapeHtml(JSON.stringify(item.defaultMountValues || {}))}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "doc links" : ctx.currentLang() === "mix" ? "文档链接 / doc links" : "文档链接"}=${ctx.escapeHtml((item.docLinks || []).join(", ") || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "risk notes" : ctx.currentLang() === "mix" ? "风险说明 / risk notes" : "风险说明"}=${ctx.escapeHtml((ctx.currentLang() === "en" ? item.riskNotes?.en : ctx.currentLang() === "mix" ? `${item.riskNotes?.zh || ""} / ${item.riskNotes?.en || ""}`.trim() : item.riskNotes?.zh) || "-")}</div>
          </div>
        </div>
      `).join("");
    }

    if (!targetProfiles.length) {
      targetRoot.textContent = ctx.currentLang() === "en" ? "No target profiles loaded." : ctx.currentLang() === "mix" ? "暂无目标端 profiles / No target profiles loaded." : "暂无目标端 profiles";
    } else {
      const targetImplementationStatus = providerRegistryPayload?.target_implementation_status || {};
      targetRoot.innerHTML = targetProfiles.map((item) => `
        <div class="row-item">
          <div>
            <div>${ctx.escapeHtml(item.labelZh || item.label || item.key || "-")}</div>
            <div class="mono">key=${ctx.escapeHtml(item.key || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "implemented" : ctx.currentLang() === "mix" ? "已实现 / implemented" : "已实现"}=${targetImplementationStatus?.[item.key || ""]?.implemented ? "true" : "false"} | ${ctx.currentLang() === "en" ? "selectable" : ctx.currentLang() === "mix" ? "可选 / selectable" : "可选"}=${targetImplementationStatus?.[item.key || ""]?.selectable ? "true" : "false"}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "auth mode" : ctx.currentLang() === "mix" ? "鉴权模式 / auth mode" : "鉴权模式"}=${ctx.escapeHtml(item.authMode || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "token refresh" : ctx.currentLang() === "mix" ? "刷新方式 / token refresh" : "刷新方式"}=${ctx.escapeHtml(item.tokenRefresh || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "auto create dir" : ctx.currentLang() === "mix" ? "自动建目录 / auto create dir" : "自动建目录"}=${item.autoCreateDir ? "true" : "false"}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "fast hashes" : ctx.currentLang() === "mix" ? "快传指纹 / fast hashes" : "快传指纹"}=${ctx.escapeHtml((item.fastUploadHashes || []).join(", ") || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "fallback" : ctx.currentLang() === "mix" ? "降级方式 / fallback" : "降级方式"}=${ctx.escapeHtml((item.fallbackModes || []).join(", ") || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "research notes" : ctx.currentLang() === "mix" ? "调研备注 / research notes" : "调研备注"}=${ctx.escapeHtml((ctx.currentLang() === "en" ? item.researchNotes?.en : ctx.currentLang() === "mix" ? `${item.researchNotes?.zh || ""} / ${item.researchNotes?.en || ""}`.trim() : item.researchNotes?.zh) || "-")}</div>
          </div>
        </div>
      `).join("");
    }

    if (!driverMatrix.length) {
      matrixRoot.textContent = ctx.currentLang() === "en" ? "No matrix rows loaded." : ctx.currentLang() === "mix" ? "暂无矩阵条目 / No matrix rows loaded." : "暂无矩阵条目";
    } else {
      matrixRoot.innerHTML = driverMatrix
        .sort((a, b) => String(a.driver || "").localeCompare(String(b.driver || ""), "zh-CN"))
        .map((item) => {
          const sourceProfile = item.sourceProfile || {};
          const flow = ctx.currentLang() === "en"
            ? (item.recommendedFlowEn || item.recommendedFlow || "")
            : ctx.currentLang() === "mix"
              ? `${item.recommendedFlow || ""} / ${item.recommendedFlowEn || ""}`.trim()
              : (item.recommendedFlow || "");
          return `
            <div class="row-item">
              <div>
                <div>${ctx.escapeHtml(item.driver || "-")}</div>
                <div class="mono">${ctx.currentLang() === "en" ? "profile" : ctx.currentLang() === "mix" ? "profile / 档案" : "档案"}=${ctx.escapeHtml(sourceProfile.key || "-")} | ${ctx.currentLang() === "en" ? "level" : ctx.currentLang() === "mix" ? "等级 / level" : "等级"}=${ctx.escapeHtml(ctx.capabilityLevelText(item.level))}</div>
                <div class="mono">${ctx.currentLang() === "en" ? "suggested path" : ctx.currentLang() === "mix" ? "建议路径 / suggested path" : "建议路径"}=${ctx.escapeHtml(flow || "-")}</div>
              </div>
            </div>
          `;
        }).join("");
    }

    const auditRows = Array.isArray(coverageAuditCache?.rows) ? coverageAuditCache.rows : [];
    const auditTotals = coverageAuditCache?.totals || {};
    const gapBuckets = coverageAuditCache?.gapBuckets || {};
    const backlog = Array.isArray(coverageAuditCache?.backlog) ? coverageAuditCache.backlog : [];
    const executionPlan = coverageAuditCache?.executionPlan || {};
    const filters = ctx.currentCoverageFilters();
    const filteredAuditRows = auditRows.filter((item) => {
      if (filters.onlyGaps && (!Array.isArray(item.missingItems) || !item.missingItems.length)) return false;
      if (filters.onlyOnboardingReady && !item.onboardingReady) return false;
      if (filters.nextAction && String(item.nextAction || "") !== filters.nextAction) return false;
      if (filters.missingItem && (!Array.isArray(item.missingItems) || !item.missingItems.includes(filters.missingItem))) return false;
      if (filters.capabilityLevel && String(item.capabilityLevel || "") !== filters.capabilityLevel) return false;
      if (filters.profileKey && String(item.profileKey || "") !== filters.profileKey) return false;
      if (filters.onboardingStage && String(item.onboardingStage || "") !== filters.onboardingStage) return false;
      return true;
    });
    const filteredBacklog = backlog.filter((item) => {
      if (filters.onlyGaps && (!Array.isArray(item.missingItems) || !item.missingItems.length)) return false;
      if (filters.onlyOnboardingReady && !item.onboardingReady) return false;
      if (filters.nextAction && String(item.nextAction || "") !== filters.nextAction) return false;
      if (filters.missingItem && (!Array.isArray(item.missingItems) || !item.missingItems.includes(filters.missingItem))) return false;
      if (filters.capabilityLevel && String(item.capabilityLevel || "") !== filters.capabilityLevel) return false;
      if (filters.profileKey && String(item.profileKey || "") !== filters.profileKey) return false;
      if (filters.onboardingStage && String(item.onboardingStage || "") !== filters.onboardingStage) return false;
      return true;
    });
    const planWaves = Array.isArray(executionPlan?.waves) ? executionPlan.waves.filter((item) => {
      if (filters.nextAction && String(item.nextAction || "") !== filters.nextAction) return false;
      if (filters.onboardingStage && String(item.onboardingStage || "") !== filters.onboardingStage) return false;
      if (filters.capabilityLevel && Array.isArray(item.capabilityLevels) && item.capabilityLevels.length && !item.capabilityLevels.includes(filters.capabilityLevel)) return false;
      if (filters.profileKey && Array.isArray(item.profileKeys) && item.profileKeys.length && !item.profileKeys.includes(filters.profileKey)) return false;
      if (filters.missingItem && Array.isArray(item.missingItems) && item.missingItems.length && !item.missingItems.includes(filters.missingItem)) return false;
      return true;
    }) : [];
    if (!auditRows.length) {
      coverageBacklogRoot.textContent = ctx.currentLang() === "en"
        ? "The prioritized backlog will appear after OpenList driver coverage is available."
        : ctx.currentLang() === "mix"
          ? "OpenList 驱动覆盖可用后，这里会显示优先级 backlog。 / The prioritized backlog will appear after driver coverage is available."
          : "OpenList 驱动覆盖可用后，这里会显示优先级 backlog。";
      coverageActionStatsRoot.textContent = ctx.currentLang() === "en"
        ? "The next-action stats will appear after OpenList driver coverage is available."
        : ctx.currentLang() === "mix"
          ? "OpenList 驱动覆盖可用后，这里会显示下一步动作统计。 / The next-action stats will appear after driver coverage is available."
          : "OpenList 驱动覆盖可用后，这里会显示下一步动作统计。";
      coverageRoot.textContent = ctx.currentLang() === "en"
        ? "Coverage audit will appear after OpenList driver coverage is available."
        : ctx.currentLang() === "mix"
          ? "OpenList 驱动覆盖可用后，这里会显示覆盖审计结果。 / Coverage audit will appear after driver coverage is available."
          : "OpenList 驱动覆盖可用后，这里会显示覆盖审计结果。";
      coveragePlanRoot.textContent = ctx.currentLang() === "en"
        ? "Execution waves will appear after OpenList driver coverage is available."
        : ctx.currentLang() === "mix"
          ? "OpenList 驱动覆盖可用后，这里会显示执行波次建议。 / Execution waves will appear after driver coverage is available."
          : "OpenList 驱动覆盖可用后，这里会显示执行波次建议。";
      return;
    }

    const actionCounts = filteredAuditRows.reduce((acc, item) => {
      const key = String(item.nextAction || "unknown");
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});
    coverageBacklogRoot.innerHTML = filteredBacklog.length
      ? filteredBacklog.slice(0, 12).map((item, index) => `
          <div class="mono">${index + 1}. ${ctx.escapeHtml(item.driver || "-")} | P${item.priorityRank ?? "-"} | ${ctx.escapeHtml(ctx.coverageNextActionText(item.nextAction || ""))} | ${ctx.escapeHtml((item.missingItems || []).join(", ") || "-")}</div>
        `).join("")
      : (ctx.currentLang() === "en"
        ? "No backlog items match the current filter."
        : ctx.currentLang() === "mix"
          ? "当前筛选条件下没有 backlog 项。 / No backlog items match the current filter."
          : "当前筛选条件下没有 backlog 项。");
    coverageActionStatsRoot.innerHTML = Object.keys(actionCounts).length
      ? Object.entries(actionCounts).map(([key, count]) => `<div class="mono">${ctx.escapeHtml(ctx.coverageNextActionText(key))}: ${count}</div>`).join("")
      : (ctx.currentLang() === "en"
        ? "No next-action stats match the current filter."
        : ctx.currentLang() === "mix"
          ? "当前筛选条件下没有下一步动作统计。 / No next-action stats match the current filter."
          : "当前筛选条件下没有下一步动作统计。");
    coveragePlanRoot.innerHTML = planWaves.length
      ? planWaves.map((wave, index) => `
          <div class="mono">${index + 1}. P${wave.priorityRank ?? "-"} | ${ctx.escapeHtml(ctx.coverageNextActionText(wave.nextAction || ""))} | ${ctx.escapeHtml(wave.onboardingStage || "-")} | ${ctx.currentLang() === "en" ? "count" : ctx.currentLang() === "mix" ? "数量 / count" : "数量"}=${wave.count ?? 0}</div>
          <div class="mono">${ctx.currentLang() === "en" ? "drivers" : ctx.currentLang() === "mix" ? "驱动 / drivers" : "驱动"}=${ctx.escapeHtml((wave.drivers || []).join(", ") || "-")}</div>
          <div class="mono">${ctx.currentLang() === "en" ? "missing items" : ctx.currentLang() === "mix" ? "缺口 / missing items" : "缺口"}=${ctx.escapeHtml((wave.missingItems || []).join(", ") || "-")}</div>
          <div class="mono">${ctx.currentLang() === "en" ? "profiles" : ctx.currentLang() === "mix" ? "profiles / 档案" : "档案"}=${ctx.escapeHtml((wave.profileKeys || []).join(", ") || "-")}</div>
        `).join("")
      : (ctx.currentLang() === "en"
        ? "No execution waves match the current filter."
        : ctx.currentLang() === "mix"
          ? "当前筛选条件下没有执行波次建议。 / No execution waves match the current filter."
          : "当前筛选条件下没有执行波次建议。");
    coverageRoot.innerHTML = `
      <div class="subtle" style="margin-bottom:10px;">
        ${ctx.currentLang() === "en"
          ? `Total=${auditTotals.total ?? 0}, profile=${auditTotals.profile ?? 0}, guide=${auditTotals.guide ?? 0}, capture=${auditTotals.capture ?? 0}, capability=${auditTotals.capability ?? 0}`
          : ctx.currentLang() === "mix"
            ? `总数 / Total=${auditTotals.total ?? 0}, profile=${auditTotals.profile ?? 0}, guide=${auditTotals.guide ?? 0}, capture=${auditTotals.capture ?? 0}, capability=${auditTotals.capability ?? 0}`
            : `总数=${auditTotals.total ?? 0}，profile=${auditTotals.profile ?? 0}，guide=${auditTotals.guide ?? 0}，capture=${auditTotals.capture ?? 0}，capability=${auditTotals.capability ?? 0}`}
      </div>
      <div class="subtle" style="margin-bottom:10px;">
        ${ctx.currentLang() === "en"
          ? `fully covered=${gapBuckets.fullyCovered ?? 0}, missing profile=${gapBuckets.missingProfile ?? 0}, missing guide=${gapBuckets.missingGuide ?? 0}, missing capture=${gapBuckets.missingCapture ?? 0}, missing capability=${gapBuckets.missingCapability ?? 0}`
          : ctx.currentLang() === "mix"
            ? `完全覆盖 / fully covered=${gapBuckets.fullyCovered ?? 0}, 缺 profile / missing profile=${gapBuckets.missingProfile ?? 0}, 缺 guide / missing guide=${gapBuckets.missingGuide ?? 0}, 缺 capture / missing capture=${gapBuckets.missingCapture ?? 0}, 缺 capability / missing capability=${gapBuckets.missingCapability ?? 0}`
            : `完全覆盖=${gapBuckets.fullyCovered ?? 0}，缺 profile=${gapBuckets.missingProfile ?? 0}，缺 guide=${gapBuckets.missingGuide ?? 0}，缺 capture=${gapBuckets.missingCapture ?? 0}，缺 capability=${gapBuckets.missingCapability ?? 0}`}
      </div>
      <div class="subtle" style="margin-bottom:10px;">
        ${ctx.currentLang() === "en"
          ? `Visible rows=${filteredAuditRows.length}`
          : ctx.currentLang() === "mix"
            ? `当前可见条目 / Visible rows=${filteredAuditRows.length}`
            : `当前可见条目=${filteredAuditRows.length}`}
      </div>
      ${filteredAuditRows.map((item) => `
        <div class="row-item">
          <div>
            <div>${ctx.escapeHtml(item.driver || "-")}</div>
            <div class="mono">profile=${item.hasProfile ? "yes" : "no"} | guide=${item.hasGuide ? "yes" : "no"} | capture=${item.hasCapture ? "yes" : "no"} | capability=${item.hasCapability ? "yes" : "no"}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "inference" : ctx.currentLang() === "mix" ? "推断状态 / inference" : "推断状态"}=profile:${item.profileIsDynamic ? "dynamic" : "static"} | capture:${item.captureIsDynamic ? "dynamic" : "static"} | capability:${item.capabilityIsDynamic ? "dynamic" : "static"}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "level" : ctx.currentLang() === "mix" ? "等级 / level" : "等级"}=${ctx.escapeHtml(ctx.capabilityLevelText(item.capabilityLevel || "unsupported"))} | score=${item.coverageScore ?? 0}/4 | P${item.priorityRank ?? "-"}</div>
            <div class="mono">onboardingReady=${item.onboardingReady ? "yes" : "no"} | onboardingStage=${ctx.escapeHtml(item.onboardingStage || "-")}</div>
            <div class="mono">canonicalDriver=${ctx.escapeHtml(item.canonicalDriverKey || "generic")} | matchedGuide=${ctx.escapeHtml(item.matchedGuideKey || "-")}</div>
            <div class="mono">profileKey=${ctx.escapeHtml(item.profileKey || "generic")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "dynamic required keys" : ctx.currentLang() === "mix" ? "动态必需键 / dynamic required keys" : "动态必需键"}=${ctx.escapeHtml((item.dynamicRequiredKeys || []).join(", ") || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "dynamic matched fields" : ctx.currentLang() === "mix" ? "动态字段命中 / dynamic matched fields" : "动态字段命中"}=${ctx.escapeHtml((item.dynamicMatchedFields || []).join(", ") || "-")}</div>
            <div class="mono">guideDoc=${ctx.escapeHtml(item.guideDocUrl || "-")}</div>
            <div class="mono">captureSpec=${ctx.escapeHtml(item.captureSpecKey || "-")} | alias=${ctx.escapeHtml(item.captureMatchedAlias || "-")}</div>
            <div class="mono">captureLogin=${ctx.escapeHtml(item.captureLoginUrl || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "missing items" : ctx.currentLang() === "mix" ? "缺口 / missing items" : "缺口"}=${ctx.escapeHtml((item.missingItems || []).join(", ") || "-")}</div>
            <div class="mono">${ctx.currentLang() === "en" ? "next step" : ctx.currentLang() === "mix" ? "下一步 / next step" : "下一步"}=${ctx.escapeHtml(ctx.coverageNextActionText(item.nextAction || ""))}</div>
          </div>
        </div>
      `).join("")}
    `;
  }

  window.CloudPanBridgeRegistryView = {
    renderAboutRegistry,
  };
})();
