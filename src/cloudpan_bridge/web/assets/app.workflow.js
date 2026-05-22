(function () {
  const bridgeView = window.CloudPanBridgeBridgeView || {};

  function renderCapabilitySummary(ctx) {
    const {
      currentDriverContext,
      normalizeDriverKey,
      providerRegistryPayload,
      capabilityAssessmentCache,
      sourceAnalyzeCache,
      currentLang,
      strategyQuickActions,
      escapeHtml,
      capabilityLevelText,
      strategyModeText,
      quickActionsRoot,
      root,
    } = ctx;
    if (!root || !quickActionsRoot) return;
    const context = currentDriverContext();
    const normalized = normalizeDriverKey(context.driver || "");
    const matrix = providerRegistryPayload?.driver_matrix || {};
    const capability = matrix[normalized] || null;
    const assessment = capabilityAssessmentCache && normalizeDriverKey(capabilityAssessmentCache.driver || "") === normalized
      ? capabilityAssessmentCache
      : null;
    if (!capability) {
      quickActionsRoot.innerHTML = "";
      root.innerHTML = currentLang() === "en"
        ? "No capability matrix matched for the current driver yet. Treat it conservatively and verify hash availability first."
        : currentLang() === "mix"
          ? "当前驱动暂未命中内置能力矩阵，建议按保守模式处理，先验证哈希可用性。 / Treat it conservatively first."
          : "当前驱动暂未命中内置能力矩阵，建议按保守模式处理，先验证哈希可用性。";
      return;
    }
    const sourceProfile = capability.sourceProfile || {};
    const targetProfile = capability.targetProfile || {};
    const notes = capability.notes || {};
    const assessedLevel = assessment?.assessedLevel || capability.level;
    const sourceMappingContext = assessment?.sourceMappingContext || providerRegistryPayload?.current_source_context || {};
    const sourceEnrichment = assessment?.sourceEnrichment || capability?.sourceEnrichment || {};
    const bridgeRuntime = sourceEnrichment.bridge_runtime || {};
    const bridgePreparation = sourceEnrichment.bridge_preparation_summary || bridgeRuntime.preparation || {};
    const bridgeMaturity = sourceEnrichment.bridge_maturity_summary || {};
    const bridgeThrottle = bridgePreparation.throttle_defaults || {};
    const bridgeFallbackPolicy = bridgePreparation.fallback_policy || {};
    const targetHashAcceptance = assessment?.targetHashAcceptance || {};
    const captureCacheAvailable = !!bridgePreparation.capture_cache_available;
    const captureCacheLookupModes = Array.isArray(bridgePreparation.capture_cache_lookup_modes) ? bridgePreparation.capture_cache_lookup_modes : [];
    const captureCacheHashFields = Array.isArray(bridgePreparation.capture_cache_hash_fields) ? bridgePreparation.capture_cache_hash_fields : [];
    const captureCacheSummary = captureCacheAvailable
      ? `entries=${bridgePreparation.capture_cache_entry_count ?? 0} | lookup=${captureCacheLookupModes.join(", ") || "-"} | hashes=${captureCacheHashFields.join(", ") || "-"}`
      : "-";
    const rationale = assessment?.rationale || {};
    const strategy = assessment?.strategy || {};
    const sourceTargetRoute = assessment?.sourceTargetRoute || sourceAnalyzeCache?.sourceTargetRoute || {};
    const likelyHashes = Array.isArray(sourceProfile.likelyHashes) ? sourceProfile.likelyHashes : [];
    const analysisSummary = sourceAnalyzeCache?.summary || {};
    const analysisLine = sourceAnalyzeCache
      ? `${currentLang() === "en" ? "Current analysis" : currentLang() === "mix" ? "当前分析 / Current analysis" : "当前分析"}: MD5=${analysisSummary.md5_ready ?? 0}, GCID=${analysisSummary.gcid_ready ?? 0}, ${currentLang() === "en" ? "Fast fingerprints" : currentLang() === "mix" ? "可快传指纹 / Fast fingerprints" : "可快传指纹"}=${analysisSummary.fast_upload_ready ?? 0}/${analysisSummary.total ?? 0}`
      : `${currentLang() === "en" ? "Current analysis" : currentLang() === "mix" ? "当前分析 / Current analysis" : "当前分析"}: ${currentLang() === "en" ? "not run yet" : currentLang() === "mix" ? "尚未运行 / not run yet" : "尚未运行"}`;
    const recommendedFlow = currentLang() === "en"
      ? (capability.recommendedFlowEn || capability.recommendedFlow || "")
      : currentLang() === "mix"
        ? `${capability.recommendedFlow || ""} / ${capability.recommendedFlowEn || ""}`.trim()
        : (capability.recommendedFlow || "");
    const notesText = currentLang() === "en"
      ? (notes.en || "")
      : currentLang() === "mix"
        ? `${notes.zh || ""} / ${notes.en || ""}`.trim()
        : (notes.zh || "");
    const rationaleText = currentLang() === "en"
      ? (rationale.en || "")
      : currentLang() === "mix"
        ? `${rationale.zh || ""} / ${rationale.en || ""}`.trim()
        : (rationale.zh || "");
    const throttleHintText = currentLang() === "en"
      ? (strategy?.throttleHint?.en || "")
      : currentLang() === "mix"
        ? `${strategy?.throttleHint?.zh || ""} / ${strategy?.throttleHint?.en || ""}`.trim()
        : (strategy?.throttleHint?.zh || "");
    const suggestedActions = Array.isArray(strategy?.suggestedActions) ? strategy.suggestedActions : [];
    const supportsFingerprintEnrichment = !!sourceProfile.supportsFingerprintEnrichment;
    const suggestedText = suggestedActions.length
      ? suggestedActions.map((item, index) => {
          const text = currentLang() === "en"
            ? (item?.en || "")
            : currentLang() === "mix"
              ? `${item?.zh || ""} / ${item?.en || ""}`.trim()
              : (item?.zh || "");
          return `${index + 1}. ${text}`;
        }).join("<br>")
      : "-";
    const executionFlags = [
      `${currentLang() === "en" ? "Analyze first" : currentLang() === "mix" ? "先分析 / Analyze first" : "先分析"}=${strategy?.shouldAnalyzeFirst ? "yes" : "no"}`,
      `${currentLang() === "en" ? "Prefer leaf mode" : currentLang() === "mix" ? "叶子目录优先 / Prefer leaf mode" : "叶子目录优先"}=${strategy?.preferLeafMode ? "yes" : "no"}`,
      `${currentLang() === "en" ? "Prefer pending tree" : currentLang() === "mix" ? "待补传树优先 / Prefer pending tree" : "待补传树优先"}=${strategy?.preferPendingTree ? "yes" : "no"}`,
    ].join(" | ");
    const transferPreviewText = sourceAnalyzeCache?.transferPlanPreview
      ? bridgeView.formatCountMap(ctx, sourceAnalyzeCache.transferPlanPreview.mode_counts || {}, (_ctx, key) => bridgeView.transferModeText(ctx, key))
      : "-";
    const enrichBatch = sourceAnalyzeCache?.sourceEnrichmentBatch || {};
    const enrichBatchText = Object.entries(enrichBatch.candidate_hash_counts || {}).map(([k, v]) => `${k}:${v}`).join(" | ") || "-";
    const enrichPendingText = bridgeView.formatCountMap(ctx, enrichBatch.pending_reason_counts || {}, bridgeView.bridgePendingReasonText);
    const transferReasonText = bridgeView.formatCountMap(ctx, sourceAnalyzeCache?.transferPlanPreview?.reason_code_counts || {}, bridgeView.transferReasonCodeText);
    const transferNextActionText = bridgeView.formatCountMap(ctx, sourceAnalyzeCache?.transferPlanPreview?.next_action_hint_counts || {}, bridgeView.nextActionHintText);
    const transferStageText = bridgeView.formatCountMap(ctx, sourceAnalyzeCache?.transferPlanPreview?.bridge_provider_stage_counts || {}, bridgeView.bridgeProviderStageText);
    const transferMaturityText = bridgeView.formatCountMap(ctx, sourceAnalyzeCache?.transferPlanPreview?.bridge_maturity_level_counts || {}, bridgeView.bridgeMaturityText);
    const transferExpectedGapText = Object.entries(sourceAnalyzeCache?.transferPlanPreview?.bridge_missing_expected_hash_counts || {}).map(([k, v]) => `${k}:${v}`).join(" | ") || "-";
    const transferTargetFastGapText = Object.entries(sourceAnalyzeCache?.transferPlanPreview?.missing_target_fast_hash_counts || {}).map(([k, v]) => `${k}:${v}`).join(" | ") || "-";
    const transferRecoverableFastGapText = Object.entries(sourceAnalyzeCache?.transferPlanPreview?.bridge_missing_recoverable_fast_hash_counts || {}).map(([k, v]) => `${k}:${v}`).join(" | ") || "-";
    const bridgeThrottleText = [
      `mode=${bridgeThrottle.rate_mode || "-"}`,
      `page=${bridgeThrottle.page_size ?? "-"}`,
      `req=${bridgeThrottle.request_interval_ms ?? "-"}ms`,
      `dir=${bridgeThrottle.directory_interval_ms ?? "-"}ms`,
      `small_batch=${bridgeThrottle.small_batch_only ? "yes" : "no"}`,
    ].join(" | ");
    const bridgeFallbackText = [
      `auto_download=${bridgeFallbackPolicy.allow_auto_download ? "yes" : "no"}`,
      `selected_only=${bridgeFallbackPolicy.download_selected_only ? "yes" : "no"}`,
      `pending_first=${bridgeFallbackPolicy.pending_only_when_hash_missing ? "yes" : "no"}`,
    ].join(" | ");
    const quickActions = strategyQuickActions(strategy?.recommendedMode || "analyze_first", strategy);
    quickActionsRoot.innerHTML = quickActions.map((item) => (
      `<button class="secondary" type="button" data-capability-action="${escapeHtml(item.key)}">${escapeHtml(item.label)}</button>`
    )).join("");
    root.innerHTML = `
      <div><strong>${escapeHtml(context.driver || "-")}</strong> -> <strong>${escapeHtml(targetProfile.labelZh || targetProfile.label || "Guangya")}</strong></div>
      <div class="mono">${currentLang() === "en" ? "Source mapping" : currentLang() === "mix" ? "源映射 / Source mapping" : "源映射"}: requested=${escapeHtml(sourceMappingContext.requested_driver || context.mountedDriver || context.driver || "-")} | override=${escapeHtml(sourceMappingContext.source_profile_override || context.overrideProfile || "-")} | effective=${escapeHtml(sourceMappingContext.effective_driver || context.driver || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Capability level" : currentLang() === "mix" ? "静态等级 / Capability level" : "静态等级"}: ${escapeHtml(capabilityLevelText(capability.level))}</div>
      <div class="mono">${currentLang() === "en" ? "Runtime assessment" : currentLang() === "mix" ? "动态判断 / Runtime assessment" : "动态判断"}: ${escapeHtml(capabilityLevelText(assessedLevel))}</div>
      <div class="mono">${currentLang() === "en" ? "Execution mode" : currentLang() === "mix" ? "执行模式 / Execution mode" : "执行模式"}: ${escapeHtml(strategyModeText(strategy?.recommendedMode || "analyze_first"))}</div>
      <div class="mono">${currentLang() === "en" ? "Likely hashes" : currentLang() === "mix" ? "常见哈希 / Likely hashes" : "常见哈希"}: ${escapeHtml(likelyHashes.join(", ") || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Fingerprint enrichment" : currentLang() === "mix" ? "补指纹能力 / Fingerprint enrichment" : "补指纹能力"}: ${supportsFingerprintEnrichment ? (currentLang() === "en" ? "declared" : currentLang() === "mix" ? "已声明 / declared" : "已声明") : (currentLang() === "en" ? "unknown" : currentLang() === "mix" ? "未知 / unknown" : "未知")}</div>
      <div class="mono">${currentLang() === "en" ? "Enrichment runtime" : currentLang() === "mix" ? "补指纹运行态 / Enrichment runtime" : "补指纹运行态"}: supported=${escapeHtml(String(!!sourceEnrichment.supported))} | capture_ready=${escapeHtml(String(!!sourceEnrichment.capture_ready))} | preferred=${escapeHtml((sourceEnrichment.preferred_hashes || []).join(", ") || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Bridge runtime" : currentLang() === "mix" ? "桥接运行态 / Bridge runtime" : "桥接运行态"}: status=${escapeHtml(bridgeRuntime.status || "-")} | next=${escapeHtml(bridgeRuntime.next_action || "-")} | missing=${escapeHtml((bridgeRuntime.missing_keys || []).join(", ") || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Bridge maturity" : currentLang() === "mix" ? "桥接成熟度 / Bridge maturity" : "桥接成熟度"}: ${escapeHtml(bridgeView.bridgeMaturityText(ctx, bridgeMaturity.level || "-"))} | ${escapeHtml(bridgeMaturity.summary || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Bridge preparation" : currentLang() === "mix" ? "桥接准备态 / Bridge preparation" : "桥接准备态"}: ${escapeHtml(bridgeView.bridgeExecutionStateText(ctx, bridgePreparation.execution_state || "-"))} | ${escapeHtml(bridgeView.bridgeTransportHintText(ctx, bridgePreparation.transport_hint || "-"))}</div>
      <div class="mono">${currentLang() === "en" ? "Expected fingerprints" : currentLang() === "mix" ? "预期补指纹 / Expected fingerprints" : "预期补指纹"}: ${escapeHtml(bridgeView.bridgeExpectationText(ctx, bridgePreparation.fingerprint_expectation || []))} | ${currentLang() === "en" ? "Preferred hashes" : currentLang() === "mix" ? "优先哈希 / Preferred hashes" : "优先哈希"}=${escapeHtml((bridgePreparation.preferred_hashes || []).join(", ") || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Matched fields" : currentLang() === "mix" ? "命中字段 / Matched fields" : "命中字段"}=${escapeHtml((bridgePreparation.selected_field_names || []).join(", ") || "-")} | ${currentLang() === "en" ? "Throttle defaults" : currentLang() === "mix" ? "默认节流 / Throttle defaults" : "默认节流"}=${escapeHtml(bridgeThrottleText)}</div>
      <div class="mono">${currentLang() === "en" ? "Fallback boundary" : currentLang() === "mix" ? "降级边界 / Fallback boundary" : "降级边界"}=${escapeHtml(bridgeFallbackText)} | ${currentLang() === "en" ? "Policy" : currentLang() === "mix" ? "策略说明 / Policy" : "策略说明"}=${escapeHtml(bridgeFallbackPolicy.summary || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Capture cache" : currentLang() === "mix" ? "抓取缓存 / Capture cache" : "抓取缓存"}: ${escapeHtml(captureCacheSummary)}</div>
      <div class="mono">${currentLang() === "en" ? "Recommended rate profile" : currentLang() === "mix" ? "推荐频率 / Recommended rate profile" : "推荐频率"}: ${escapeHtml(sourceProfile.recommendedRateProfile || "-")}</div>
      <div class="mono">${escapeHtml(analysisLine)}</div>
      <div class="mono">${currentLang() === "en" ? "Bridge candidate hashes" : currentLang() === "mix" ? "桥接候选哈希 / Bridge candidate hashes" : "桥接候选哈希"}: ${escapeHtml(enrichBatchText)}</div>
      <div class="mono">${currentLang() === "en" ? "Bridge pending reasons" : currentLang() === "mix" ? "桥接挂起原因 / Bridge pending reasons" : "桥接挂起原因"}: ${escapeHtml(enrichPendingText)}</div>
      <div class="mono">${currentLang() === "en" ? "Transfer preview" : currentLang() === "mix" ? "传输预览 / Transfer preview" : "传输预览"}: ${escapeHtml(transferPreviewText)}</div>
      <div class="mono">${currentLang() === "en" ? "Transfer reason buckets" : currentLang() === "mix" ? "传输原因分桶 / Transfer reason buckets" : "传输原因分桶"}: ${escapeHtml(transferReasonText)}</div>
      <div class="mono">${currentLang() === "en" ? "Next action buckets" : currentLang() === "mix" ? "下一步动作分桶 / Next action buckets" : "下一步动作分桶"}: ${escapeHtml(transferNextActionText)}</div>
      <div class="mono">${currentLang() === "en" ? "Bridge provider stages" : currentLang() === "mix" ? "桥接阶段分桶 / Bridge provider stages" : "桥接阶段分桶"}: ${escapeHtml(transferStageText)}</div>
      <div class="mono">${currentLang() === "en" ? "Bridge maturity buckets" : currentLang() === "mix" ? "桥接成熟度分桶 / Bridge maturity buckets" : "桥接成熟度分桶"}: ${escapeHtml(transferMaturityText)}</div>
      <div class="mono">${currentLang() === "en" ? "Missing expected hashes" : currentLang() === "mix" ? "仍缺预期哈希 / Missing expected hashes" : "仍缺预期哈希"}: ${escapeHtml(transferExpectedGapText)}</div>
      <div class="mono">${currentLang() === "en" ? "Target fast-hash gaps" : currentLang() === "mix" ? "目标端快传缺口 / Target fast-hash gaps" : "目标端快传缺口"}: ${escapeHtml(transferTargetFastGapText)}</div>
      <div class="mono">${currentLang() === "en" ? "Recoverable fast-hash gaps" : currentLang() === "mix" ? "可补齐快传缺口 / Recoverable fast-hash gaps" : "可补齐快传缺口"}: ${escapeHtml(transferRecoverableFastGapText)}</div>
      <div class="mono">${currentLang() === "en" ? "Source->target route" : currentLang() === "mix" ? "源到目标路线 / Source->target route" : "源到目标路线"}: ${escapeHtml(bridgeView.sourceTargetRouteBucketText(ctx, sourceTargetRoute.decision_bucket || "-"))} | ${currentLang() === "en" ? "focus" : currentLang() === "mix" ? "关注点 / focus" : "关注点"}=${escapeHtml(bridgeView.sourceTargetRouteFocusText(ctx, sourceTargetRoute.next_focus || "-"))}</div>
      <div class="mono">${currentLang() === "en" ? "Route honesty" : currentLang() === "mix" ? "路线边界 / Route honesty" : "路线边界"}: ${escapeHtml(bridgeView.sourceTargetRouteHonestyText(ctx, sourceTargetRoute.route_honesty || "-"))} | ${currentLang() === "en" ? "preferred mode" : currentLang() === "mix" ? "建议执行 / preferred mode" : "建议执行"}=${escapeHtml(bridgeView.transferModeText(ctx, sourceTargetRoute.preferred_execution_mode || "-"))}</div>
      <div class="mono">${currentLang() === "en" ? "Route fast hashes" : currentLang() === "mix" ? "路线快传哈希 / Route fast hashes" : "路线快传哈希"}: native=${escapeHtml((sourceTargetRoute.native_fast_candidate_hashes || []).join(", ") || "-")} | bridge=${escapeHtml((sourceTargetRoute.bridge_recoverable_fast_hashes || []).join(", ") || "-")} | cache=${escapeHtml((sourceTargetRoute.capture_cache_fast_hashes || []).join(", ") || "-")} | fallback=${escapeHtml(bridgeView.transferModeText(ctx, sourceTargetRoute.fallback_execution_mode || "-"))}</div>
      <div class="mono">${currentLang() === "en" ? "Target hash acceptance" : currentLang() === "mix" ? "目标端哈希接受度 / Target hash acceptance" : "目标端哈希接受度"}: direct=${escapeHtml((targetHashAcceptance.directNativeAccepts || []).join(", ") || "-")} | bridge=${escapeHtml((targetHashAcceptance.bridgeRecoverableAccepts || []).join(", ") || "-")} | cache=${escapeHtml((targetHashAcceptance.captureCacheAccepts || []).join(", ") || "-")} | unsupported=${escapeHtml((targetHashAcceptance.declaredButTargetUnsupported || []).join(", ") || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Acceptance summary" : currentLang() === "mix" ? "接受度摘要 / Acceptance summary" : "接受度摘要"}: ${escapeHtml(currentLang() === "en" ? (targetHashAcceptance.summary?.en || targetHashAcceptance.summary?.zh || "-") : currentLang() === "mix" ? `${targetHashAcceptance.summary?.zh || "-"} / ${targetHashAcceptance.summary?.en || "-"}` : (targetHashAcceptance.summary?.zh || targetHashAcceptance.summary?.en || "-"))}</div>
      <div class="mono">${currentLang() === "en" ? "Route summary" : currentLang() === "mix" ? "路线摘要 / Route summary" : "路线摘要"}: ${escapeHtml(sourceTargetRoute.summary || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Suggested path" : currentLang() === "mix" ? "建议路径 / Suggested path" : "建议路径"}: ${escapeHtml(recommendedFlow || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Runtime rationale" : currentLang() === "mix" ? "动态理由 / Runtime rationale" : "动态理由"}: ${escapeHtml(rationaleText || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Throttle hint" : currentLang() === "mix" ? "节奏建议 / Throttle hint" : "节奏建议"}: ${escapeHtml(throttleHintText || "-")}</div>
      <div class="mono">${currentLang() === "en" ? "Execution flags" : currentLang() === "mix" ? "执行偏好 / Execution flags" : "执行偏好"}: ${escapeHtml(executionFlags)}</div>
      <div class="mono">${currentLang() === "en" ? "Suggested actions" : currentLang() === "mix" ? "建议动作 / Suggested actions" : "建议动作"}:<br>${suggestedText}</div>
      <div class="mono">${currentLang() === "en" ? "Notes" : currentLang() === "mix" ? "说明 / Notes" : "说明"}: ${escapeHtml(notesText || "-")}</div>
    `;
  }

  function renderSourceAnalyze(ctx, data) {
    const { currentLang, escapeHtml, formatBytes, setSourceAnalyzeCache } = ctx;
    setSourceAnalyzeCache(data || null);
    const root = document.getElementById("source-analyze-summary");
    const summary = data?.summary || {};
    const decision = data?.fastUploadDecision || {};
    const enrichment = data?.sourceEnrichment || {};
    const enrichBatch = data?.sourceEnrichmentBatch || {};
    const bridgeRuntime = enrichment.bridge_runtime || {};
    const bridgePreparation = enrichment.bridge_preparation_summary || bridgeRuntime.preparation || {};
    const bridgeMaturity = enrichment.bridge_maturity_summary || {};
    const sourceTargetRoute = data?.sourceTargetRoute || {};
    const bridgeThrottle = bridgePreparation.throttle_defaults || {};
    const bridgeFallbackPolicy = bridgePreparation.fallback_policy || {};
    const captureCacheAvailable = !!bridgePreparation.capture_cache_available;
    const captureCacheLookupModes = Array.isArray(bridgePreparation.capture_cache_lookup_modes) ? bridgePreparation.capture_cache_lookup_modes : [];
    const captureCacheHashFields = Array.isArray(bridgePreparation.capture_cache_hash_fields) ? bridgePreparation.capture_cache_hash_fields : [];
    const captureCacheSummary = captureCacheAvailable
      ? `entries=${bridgePreparation.capture_cache_entry_count ?? 0} | lookup=${captureCacheLookupModes.join(", ") || "-"} | hashes=${captureCacheHashFields.join(", ") || "-"}`
      : "-";
    const transferPreview = data?.transferPlanPreview || {};
    const entries = Array.isArray(data?.entries) ? data.entries : [];
    if (!data) {
      root.textContent = currentLang() === "en" ? "No analysis result" : currentLang() === "mix" ? "暂无分析结果 / No analysis result" : "暂无分析结果";
      return;
    }
    const providerCounts = Object.entries(summary.provider_counts || {}).map(([key, value]) => `${key}: ${value}`).join(" | ") || "-";
    const hashCounts = Object.entries(summary.hash_type_counts || {}).map(([key, value]) => `${key}: ${value}`).join(" | ") || "-";
    const candidateCounts = Object.entries(enrichBatch.candidate_hash_counts || {}).map(([key, value]) => `${key}: ${value}`).join(" | ") || "-";
    const pendingCounts = bridgeView.formatCountMap(ctx, enrichBatch.pending_reason_counts || {}, bridgeView.bridgePendingReasonText);
    const bridgeStateCounts = bridgeView.formatCountMap(ctx, enrichBatch.bridge_execution_state_counts || {}, bridgeView.bridgeExecutionStateText);
    const bridgeStageCounts = bridgeView.formatCountMap(ctx, enrichBatch.provider_stage_counts || {}, bridgeView.bridgeProviderStageText);
    const previewModeCounts = bridgeView.formatCountMap(ctx, transferPreview.mode_counts || {}, (_ctx, key) => bridgeView.transferModeText(ctx, key));
    const previewReasonCounts = bridgeView.formatCountMap(ctx, transferPreview.reason_code_counts || {}, bridgeView.transferReasonCodeText);
    const previewNextActionCounts = bridgeView.formatCountMap(ctx, transferPreview.next_action_hint_counts || {}, bridgeView.nextActionHintText);
    const previewMaturityCounts = bridgeView.formatCountMap(ctx, transferPreview.bridge_maturity_level_counts || {}, bridgeView.bridgeMaturityText);
    const previewExpectedGapText = Object.entries(transferPreview.bridge_missing_expected_hash_counts || {}).map(([k, v]) => `${k}:${v}`).join(" | ") || "-";
    const previewTargetFastGapText = Object.entries(transferPreview.missing_target_fast_hash_counts || {}).map(([k, v]) => `${k}:${v}`).join(" | ") || "-";
    const previewRecoverableFastGapText = Object.entries(transferPreview.bridge_missing_recoverable_fast_hash_counts || {}).map(([k, v]) => `${k}:${v}`).join(" | ") || "-";
    const recommendation = summary.missing_md5 > 0
      ? (summary.gcid_ready > 0
        ? (currentLang() === "en"
          ? "Some files do not have MD5 but do have GCID. Prefer metadata sync first, then inspect pending items carefully."
          : currentLang() === "mix"
            ? "部分文件没有 MD5 但有 GCID，建议先走元数据秒传，再重点检查待补传。 / Prefer metadata sync first, then inspect pending items carefully."
            : "部分文件没有 MD5 但有 GCID，建议先走元数据秒传，再重点检查待补传。")
        : (currentLang() === "en"
          ? "Some files do not have MD5. Avoid aggressive auto-download and inspect source/provider compatibility first."
          : currentLang() === "mix"
            ? "部分文件没有 MD5，建议先确认源端兼容性，不要过激进地自动补传。 / Avoid aggressive auto-download first."
            : "部分文件没有 MD5，建议先确认源端兼容性，不要过激进地自动补传。"))
      : (currentLang() === "en"
        ? "Most files are MD5-ready. This directory is suitable for normal metadata-first sync."
        : currentLang() === "mix"
          ? "大多数文件已具备 MD5，适合正常先秒传再补传。 / This directory looks good for metadata-first sync."
          : "大多数文件已具备 MD5，适合正常先秒传再补传。");
    root.innerHTML = `
      <div class="row-item">
        <div>
          <div>${escapeHtml(data.source_path || "-")}</div>
          <div class="mono">${currentLang() === "en" ? "Total files" : currentLang() === "mix" ? "文件总数 / Total files" : "文件总数"}: ${summary.total ?? 0} | ${currentLang() === "en" ? "Plan total" : currentLang() === "mix" ? "待同步 / Plan total" : "待同步"}: ${data.plan_total ?? 0} | ${currentLang() === "en" ? "Removed" : currentLang() === "mix" ? "源端已删除 / Removed" : "源端已删除"}: ${data.removed_total ?? 0}</div>
          <div class="mono">${currentLang() === "en" ? "MD5 ready" : currentLang() === "mix" ? "具备 MD5 / MD5 ready" : "具备 MD5"}: ${summary.md5_ready ?? 0} | GCID: ${summary.gcid_ready ?? 0} | ${currentLang() === "en" ? "Missing MD5" : currentLang() === "mix" ? "缺少 MD5 / Missing MD5" : "缺少 MD5"}: ${summary.missing_md5 ?? 0}</div>
          <div class="mono">${currentLang() === "en" ? "Fast upload decision" : currentLang() === "mix" ? "秒传决策 / Fast upload decision" : "秒传决策"}: ${escapeHtml(decision.level || "-")} | ${escapeHtml(decision.bucket || "-")}</div>
          <div class="mono">${currentLang() === "en" ? "Enrichment runtime" : currentLang() === "mix" ? "补指纹运行态 / Enrichment runtime" : "补指纹运行态"}: supported=${escapeHtml(String(!!enrichment.supported))} | capture_ready=${escapeHtml(String(!!enrichment.capture_ready))} | preferred=${escapeHtml((enrichment.preferred_hashes || []).join(", ") || "-")}</div>
          <div class="mono">${currentLang() === "en" ? "Bridge runtime" : currentLang() === "mix" ? "桥接运行态 / Bridge runtime" : "桥接运行态"}: status=${escapeHtml(bridgeRuntime.status || "-")} | next=${escapeHtml(bridgeRuntime.next_action || "-")} | missing=${escapeHtml((bridgeRuntime.missing_keys || []).join(", ") || "-")}</div>
          <div class="mono">${currentLang() === "en" ? "Bridge maturity" : currentLang() === "mix" ? "桥接成熟度 / Bridge maturity" : "桥接成熟度"}: ${escapeHtml(bridgeView.bridgeMaturityText(ctx, bridgeMaturity.level || "-"))} | ${escapeHtml(bridgeMaturity.summary || "-")}</div>
          <div class="mono">${currentLang() === "en" ? "Bridge preparation" : currentLang() === "mix" ? "桥接准备态 / Bridge preparation" : "桥接准备态"}: ${escapeHtml(bridgeView.bridgeExecutionStateText(ctx, bridgePreparation.execution_state || "-"))} | ${escapeHtml(bridgeView.bridgeTransportHintText(ctx, bridgePreparation.transport_hint || "-"))}</div>
          <div class="mono">${currentLang() === "en" ? "Expected fingerprints" : currentLang() === "mix" ? "预期补指纹 / Expected fingerprints" : "预期补指纹"}: ${escapeHtml(bridgeView.bridgeExpectationText(ctx, bridgePreparation.fingerprint_expectation || []))} | ${currentLang() === "en" ? "Preferred hashes" : currentLang() === "mix" ? "优先哈希 / Preferred hashes" : "优先哈希"}=${escapeHtml((bridgePreparation.preferred_hashes || []).join(", ") || "-")}</div>
          <div class="mono">${currentLang() === "en" ? "Throttle defaults" : currentLang() === "mix" ? "默认节流 / Throttle defaults" : "默认节流"}=${escapeHtml([`mode=${bridgeThrottle.rate_mode || "-"}`, `page=${bridgeThrottle.page_size ?? "-"}`, `req=${bridgeThrottle.request_interval_ms ?? "-"}ms`, `dir=${bridgeThrottle.directory_interval_ms ?? "-"}ms`, `small_batch=${bridgeThrottle.small_batch_only ? "yes" : "no"}`].join(" | "))}</div>
          <div class="mono">${currentLang() === "en" ? "Fallback boundary" : currentLang() === "mix" ? "降级边界 / Fallback boundary" : "降级边界"}=${escapeHtml([`auto_download=${bridgeFallbackPolicy.allow_auto_download ? "yes" : "no"}`, `selected_only=${bridgeFallbackPolicy.download_selected_only ? "yes" : "no"}`, `pending_first=${bridgeFallbackPolicy.pending_only_when_hash_missing ? "yes" : "no"}`].join(" | "))} | ${currentLang() === "en" ? "Policy" : currentLang() === "mix" ? "策略说明 / Policy" : "策略说明"}=${escapeHtml(bridgeFallbackPolicy.summary || "-")}</div>
          <div class="mono">${currentLang() === "en" ? "Capture cache" : currentLang() === "mix" ? "抓取缓存 / Capture cache" : "抓取缓存"}: ${escapeHtml(captureCacheSummary)}</div>
          <div class="mono">${currentLang() === "en" ? "Bridge states" : currentLang() === "mix" ? "桥接执行态 / Bridge states" : "桥接执行态"}: ${escapeHtml(bridgeStateCounts)}</div>
          <div class="mono">${currentLang() === "en" ? "Bridge stages" : currentLang() === "mix" ? "桥接阶段 / Bridge stages" : "桥接阶段"}: ${escapeHtml(bridgeStageCounts)}</div>
          <div class="mono">${currentLang() === "en" ? "Bridge candidate hashes" : currentLang() === "mix" ? "桥接候选哈希 / Bridge candidate hashes" : "桥接候选哈希"}: ${escapeHtml(candidateCounts)}</div>
          <div class="mono">${currentLang() === "en" ? "Bridge pending reasons" : currentLang() === "mix" ? "桥接挂起原因 / Bridge pending reasons" : "桥接挂起原因"}: ${escapeHtml(pendingCounts)}</div>
          <div class="mono">${currentLang() === "en" ? "Transfer preview" : currentLang() === "mix" ? "传输预览 / Transfer preview" : "传输预览"}: ${escapeHtml(previewModeCounts)}</div>
          <div class="mono">${currentLang() === "en" ? "Transfer reason buckets" : currentLang() === "mix" ? "传输原因分桶 / Transfer reason buckets" : "传输原因分桶"}: ${escapeHtml(previewReasonCounts)}</div>
          <div class="mono">${currentLang() === "en" ? "Next action buckets" : currentLang() === "mix" ? "下一步动作分桶 / Next action buckets" : "下一步动作分桶"}: ${escapeHtml(previewNextActionCounts)}</div>
          <div class="mono">${currentLang() === "en" ? "Bridge maturity buckets" : currentLang() === "mix" ? "桥接成熟度分桶 / Bridge maturity buckets" : "桥接成熟度分桶"}: ${escapeHtml(previewMaturityCounts)}</div>
          <div class="mono">${currentLang() === "en" ? "Missing expected hashes" : currentLang() === "mix" ? "仍缺预期哈希 / Missing expected hashes" : "仍缺预期哈希"}: ${escapeHtml(previewExpectedGapText)}</div>
          <div class="mono">${currentLang() === "en" ? "Target fast-hash gaps" : currentLang() === "mix" ? "目标端快传缺口 / Target fast-hash gaps" : "目标端快传缺口"}: ${escapeHtml(previewTargetFastGapText)}</div>
          <div class="mono">${currentLang() === "en" ? "Recoverable fast-hash gaps" : currentLang() === "mix" ? "可补齐快传缺口 / Recoverable fast-hash gaps" : "可补齐快传缺口"}: ${escapeHtml(previewRecoverableFastGapText)}</div>
          <div class="mono">${currentLang() === "en" ? "Source->target route" : currentLang() === "mix" ? "源到目标路线 / Source->target route" : "源到目标路线"}: ${escapeHtml(bridgeView.sourceTargetRouteBucketText(ctx, sourceTargetRoute.decision_bucket || "-"))} | ${currentLang() === "en" ? "focus" : currentLang() === "mix" ? "关注点 / focus" : "关注点"}=${escapeHtml(bridgeView.sourceTargetRouteFocusText(ctx, sourceTargetRoute.next_focus || "-"))}</div>
          <div class="mono">${currentLang() === "en" ? "Route honesty" : currentLang() === "mix" ? "路线边界 / Route honesty" : "路线边界"}: ${escapeHtml(bridgeView.sourceTargetRouteHonestyText(ctx, sourceTargetRoute.route_honesty || "-"))} | ${currentLang() === "en" ? "preferred mode" : currentLang() === "mix" ? "建议执行 / preferred mode" : "建议执行"}=${escapeHtml(bridgeView.transferModeText(ctx, sourceTargetRoute.preferred_execution_mode || "-"))}</div>
          <div class="mono">${currentLang() === "en" ? "Route cache hashes" : currentLang() === "mix" ? "缓存快传哈希 / Route cache hashes" : "缓存快传哈希"}: ${escapeHtml((sourceTargetRoute.capture_cache_fast_hashes || []).join(", ") || "-")}</div>
          <div class="mono">${currentLang() === "en" ? "Route summary" : currentLang() === "mix" ? "路线摘要 / Route summary" : "路线摘要"}: ${escapeHtml(sourceTargetRoute.summary || "-")}</div>
          <div class="mono">provider: ${escapeHtml(providerCounts)}</div>
          <div class="mono">hash: ${escapeHtml(hashCounts)}</div>
          <div class="mono">${escapeHtml((currentLang() === "en" ? decision?.rationale?.en : currentLang() === "mix" ? `${decision?.rationale?.zh || ""} / ${decision?.rationale?.en || ""}`.trim() : decision?.rationale?.zh) || "-")}</div>
          <div class="mono">${escapeHtml(recommendation)}</div>
        </div>
      </div>
      ${entries.map((item) => `
        <div class="row-item">
          <div>
            <div>${escapeHtml(item.path || "")}</div>
            <div class="mono">provider=${escapeHtml(item.provider || "-")} | hashType=${escapeHtml(item.hashType || "-")} | size=${escapeHtml(String(item.size ?? 0))}</div>
            <div class="mono">md5=${escapeHtml(item.md5 || "-")} | gcid=${escapeHtml(item.gcid || "-")} | sourceId=${escapeHtml(item.sourceId || "-")}</div>
            <div class="mono">${currentLang() === "en" ? "planned" : currentLang() === "mix" ? "计划模式 / planned" : "计划模式"}=${escapeHtml(bridgeView.transferModeText(ctx, item.transferPlan?.mode || "-"))} | ${currentLang() === "en" ? "reason" : currentLang() === "mix" ? "原因 / reason" : "原因"}=${escapeHtml(bridgeView.transferReasonCodeText(ctx, item.transferPlan?.reason_code || "-"))}</div>
            <div class="mono">${currentLang() === "en" ? "next action" : currentLang() === "mix" ? "下一步 / next action" : "下一步"}=${escapeHtml(bridgeView.nextActionHintText(ctx, item.transferPlan?.next_action_hint || "-"))}</div>
            <div class="mono">${currentLang() === "en" ? "bridge stage" : currentLang() === "mix" ? "桥接阶段 / bridge stage" : "桥接阶段"}=${escapeHtml(bridgeView.bridgeProviderStageText(ctx, item.transferPlan?.bridge_provider_stage || "-"))} | ${currentLang() === "en" ? "maturity" : currentLang() === "mix" ? "成熟度 / maturity" : "成熟度"}=${escapeHtml(bridgeView.bridgeMaturityText(ctx, item.transferPlan?.bridge_maturity_level || "-"))}</div>
            <div class="mono">${currentLang() === "en" ? "pending" : currentLang() === "mix" ? "挂起 / pending" : "挂起"}=${escapeHtml(bridgeView.bridgePendingReasonText(ctx, item.transferPlan?.bridge_pending_reason || "-"))} | ${currentLang() === "en" ? "honesty" : currentLang() === "mix" ? "边界 / honesty" : "边界"}=${escapeHtml(bridgeView.bridgeHonestyText(ctx, item.transferPlan?.bridge_maturity_honesty || "-"))}</div>
            <div class="mono">${currentLang() === "en" ? "expected" : currentLang() === "mix" ? "预期哈希 / expected" : "预期哈希"}=${escapeHtml((item.transferPlan?.bridge_expected_hashes || []).join(", ") || "-")} | ${currentLang() === "en" ? "missing" : currentLang() === "mix" ? "仍缺 / missing" : "仍缺"}=${escapeHtml((item.transferPlan?.bridge_missing_expected_hashes || []).join(", ") || "-")}</div>
            <div class="mono">${currentLang() === "en" ? "target fast" : currentLang() === "mix" ? "目标快传 / target fast" : "目标快传"}=${escapeHtml((item.transferPlan?.target_fast_hashes || []).join(", ") || "-")} | ${currentLang() === "en" ? "fast gap" : currentLang() === "mix" ? "快传缺口 / fast gap" : "快传缺口"}=${escapeHtml((item.transferPlan?.missing_target_fast_hashes || []).join(", ") || "-")}</div>
            <div class="mono">${currentLang() === "en" ? "recoverable fast" : currentLang() === "mix" ? "可补快传 / recoverable fast" : "可补快传"}=${escapeHtml((item.transferPlan?.bridge_recoverable_fast_hashes || []).join(", ") || "-")} | ${currentLang() === "en" ? "recoverable gap" : currentLang() === "mix" ? "可补缺口 / recoverable gap" : "可补缺口"}=${escapeHtml((item.transferPlan?.bridge_missing_recoverable_fast_hashes || []).join(", ") || "-")}</div>
          </div>
        </div>
      `).join("")}
      ${data.truncated ? `<div class="subtle">${currentLang() === "en" ? "Only the first preview rows are shown here. Full export has been written to the local export file." : currentLang() === "mix" ? "这里只展示前几条样本，完整结果已写入本地导出文件。 / Only preview rows are shown here." : "这里只展示前几条样本，完整结果已写入本地导出文件。"}</div>` : ""}
    `;
  }

  function renderSourceDriverSummary(ctx) {
    const {
      currentDriverContext,
      providerRegistryPayload,
      capabilityAssessmentCache,
      currentDirectoryPath,
      configCache,
      getGroupedConfigValue,
      escapeHtml,
    } = ctx;
    const root = document.getElementById("source-driver-summary");
    const humanRoot = document.getElementById("source-driver-human-summary");
    if (!root) return;
    const context = currentDriverContext();
    const backendContext = providerRegistryPayload?.current_source_context || {};
    const assessedContext = capabilityAssessmentCache?.sourceMappingContext || {};
    const runtimeContext = window.__cpbStatusCache?.sync?.current_source_context || {};
    const sourcePath = String(document.getElementById("source_path")?.value || configCache?.source_path || "/").trim() || "/";
    const browsingPath = String(currentDirectoryPath || "/").trim() || "/";
    const selectedMount = String(document.getElementById("mounted_source_select")?.value || "").trim();
    const rateMode = String(document.getElementById("rate_limit_mode")?.value || configCache?.rate_limit_mode || "safe").trim() || "safe";
    const sourceRuntime = window.__cpbStatusCache?.source_runtime || {};
    const sourceEnrichment = window.__cpbStatusCache?.sourceEnrichment || {};
    const bridgeRuntime = sourceEnrichment.bridge_runtime || {};
    const bridgePreparation = sourceEnrichment.bridge_preparation_summary || bridgeRuntime.preparation || {};
    const bridgeMaturity = sourceEnrichment.bridge_maturity_summary || {};
    const sourceTargetRoute = sourceRuntime.source_target_route || {};
    const bridgeThrottle = bridgePreparation.throttle_defaults || {};
    const bridgeFallbackPolicy = bridgePreparation.fallback_policy || {};
    const humanLines = [];
    const mountedDriverLabel = context.mountedDriver || context.driver || "-";
    const routeMode = String(sourceRuntime.selected_source_mode || "-");
    const enrichReady = !!sourceEnrichment.capture_ready;
    const fastCandidate = Array.isArray(sourceTargetRoute.native_fast_candidate_hashes) && sourceTargetRoute.native_fast_candidate_hashes.length
      ? sourceTargetRoute.native_fast_candidate_hashes.join(", ")
      : Array.isArray(sourceTargetRoute.bridge_recoverable_fast_hashes) && sourceTargetRoute.bridge_recoverable_fast_hashes.length
        ? sourceTargetRoute.bridge_recoverable_fast_hashes.join(", ")
        : "-";
    if (humanRoot) {
      const lang = ctx.currentLang();
      const mountText = selectedMount || browsingPath || sourcePath || "/";
      const routeText = routeMode === "openlist_mount"
        ? (lang === "en" ? "Currently browsing via OpenList mount." : lang === "mix" ? "当前通过 OpenList 挂载浏览。 / Browsing via OpenList mount." : "当前通过 OpenList 挂载浏览。")
        : routeMode === "provider_direct"
          ? (lang === "en" ? "Provider direct route is preferred for this source." : lang === "mix" ? "当前更偏向走网盘直连。 / Provider direct route is preferred." : "当前更偏向走网盘直连。")
          : (lang === "en" ? "Source route will be chosen automatically." : lang === "mix" ? "当前会自动选择执行路线。 / Source route is selected automatically." : "当前会自动选择执行路线。");
      const enrichText = enrichReady
        ? (lang === "en" ? "Login capture cache is available for richer source metadata." : lang === "mix" ? "已具备登录抓取缓存，可补更多源端元数据。 / Capture cache is available." : "已具备登录抓取缓存，可补更多源端元数据。")
        : (lang === "en" ? "No extra capture cache is active yet; normal mount browsing still works." : lang === "mix" ? "暂未启用额外抓取缓存，但普通挂载浏览不受影响。 / Normal browsing still works." : "暂未启用额外抓取缓存，但普通挂载浏览不受影响。");
      const fastText = fastCandidate && fastCandidate !== "-"
        ? (lang === "en" ? `Potential fast-upload hashes: ${fastCandidate}.` : lang === "mix" ? `当前可能可用的快传指纹：${fastCandidate}。 / Potential fast-upload hashes: ${fastCandidate}.` : `当前可能可用的快传指纹：${fastCandidate}。`)
        : (lang === "en" ? "No fast-upload hash advantage has been identified yet." : lang === "mix" ? "当前还没识别到明显的快传指纹优势。 / No fast-upload hash advantage identified yet." : "当前还没识别到明显的快传指纹优势。");
      humanLines.push(
        lang === "en"
          ? `Current source mount: ${mountText} | Driver: ${mountedDriverLabel} | Rate preset: ${rateMode}`
          : lang === "mix"
            ? `当前源挂载：${mountText} | 驱动：${mountedDriverLabel} | 节奏：${rateMode} / Current source mount: ${mountText}`
            : `当前源挂载：${mountText} | 驱动：${mountedDriverLabel} | 节奏：${rateMode}`
      );
      humanLines.push(routeText);
      humanLines.push(enrichText);
      humanLines.push(fastText);
      humanRoot.innerHTML = humanLines.map((line) => `<div>${escapeHtml(line)}</div>`).join("");
    }
    const captureCacheAvailable = !!bridgePreparation.capture_cache_available;
    const captureCacheLookupModes = Array.isArray(bridgePreparation.capture_cache_lookup_modes) ? bridgePreparation.capture_cache_lookup_modes : [];
    const captureCacheHashFields = Array.isArray(bridgePreparation.capture_cache_hash_fields) ? bridgePreparation.capture_cache_hash_fields : [];
    const captureCacheSummary = captureCacheAvailable
      ? `entries=${bridgePreparation.capture_cache_entry_count ?? 0} lookup=${captureCacheLookupModes.join(", ") || "-"} hashes=${captureCacheHashFields.join(", ") || "-"}`
      : "-";
    root.innerHTML = `
      <div class="mono">driver=${escapeHtml(context.driver || "-")} | mount=${escapeHtml(selectedMount || "-")} | rate=${escapeHtml(rateMode)}</div>
      <div class="mono">mounted_driver=${escapeHtml(context.mountedDriver || "-")} | override=${escapeHtml(context.overrideProfile || "-")}</div>
      <div class="mono">backend_effective=${escapeHtml(assessedContext.effective_driver || backendContext.effective_driver || "-")} | backend_override=${escapeHtml(assessedContext.source_profile_override || backendContext.source_profile_override || "-")}</div>
      <div class="mono">runtime_mount=${escapeHtml(runtimeContext.mount_path || "-")} | runtime_effective=${escapeHtml(runtimeContext.effective_driver || "-")}</div>
      <div class="mono">route_pref=${escapeHtml(sourceRuntime.requested_provider_preference || "-")} | route_selected=${escapeHtml(sourceRuntime.selected_source_mode || "-")} | route_provider=${escapeHtml(sourceRuntime.selected_provider_key || "-")}</div>
      <div class="mono">enrich_supported=${escapeHtml(String(!!sourceEnrichment.supported))} | capture_ready=${escapeHtml(String(!!sourceEnrichment.capture_ready))} | bridge=${escapeHtml(sourceEnrichment.bridge_status || "-")} | preferred=${escapeHtml((sourceEnrichment.preferred_hashes || []).join(", ") || "-")}</div>
      <div class="mono">bridge_maturity=${escapeHtml(bridgeView.bridgeMaturityText(ctx, bridgeMaturity.level || "-"))} | honesty=${escapeHtml(bridgeMaturity.honesty || "-")}</div>
      <div class="mono">bridge_transport=${escapeHtml(bridgeView.bridgeTransportHintText(ctx, bridgePreparation.transport_hint || "-"))} | expected=${escapeHtml(bridgeView.bridgeExpectationText(ctx, bridgePreparation.fingerprint_expectation || []))} | preferred=${escapeHtml((bridgePreparation.preferred_hashes || []).join(", ") || "-")}</div>
      <div class="mono">bridge_fields=${escapeHtml((bridgePreparation.selected_field_names || []).join(", ") || "-")} | prep_state=${escapeHtml(bridgeView.bridgeExecutionStateText(ctx, bridgePreparation.execution_state || "-"))}</div>
      <div class="mono">bridge_cache=${escapeHtml(captureCacheSummary)}</div>
      <div class="mono">bridge_throttle=mode:${escapeHtml(String(bridgeThrottle.rate_mode || "-"))} page:${escapeHtml(String(bridgeThrottle.page_size ?? "-"))} req:${escapeHtml(String(bridgeThrottle.request_interval_ms ?? "-"))}ms dir:${escapeHtml(String(bridgeThrottle.directory_interval_ms ?? "-"))}ms small_batch:${escapeHtml(String(!!bridgeThrottle.small_batch_only))}</div>
      <div class="mono">bridge_fallback=auto:${escapeHtml(String(!!bridgeFallbackPolicy.allow_auto_download))} selected_only:${escapeHtml(String(!!bridgeFallbackPolicy.download_selected_only))} pending_first:${escapeHtml(String(!!bridgeFallbackPolicy.pending_only_when_hash_missing))}</div>
      <div class="mono">bridge_next=${escapeHtml(bridgeRuntime.next_action || "-")} | missing=${escapeHtml((bridgeRuntime.missing_keys || []).join(", ") || "-")}</div>
      <div class="mono">route_bucket=${escapeHtml(sourceTargetRoute.decision_bucket || "-")} | route_focus=${escapeHtml(sourceTargetRoute.next_focus || "-")} | route_honesty=${escapeHtml(sourceTargetRoute.route_honesty || "-")}</div>
      <div class="mono">route_native=${escapeHtml((sourceTargetRoute.native_fast_candidate_hashes || []).join(", ") || "-")} | route_bridge=${escapeHtml((sourceTargetRoute.bridge_recoverable_fast_hashes || []).join(", ") || "-")} | route_cache=${escapeHtml((sourceTargetRoute.capture_cache_fast_hashes || []).join(", ") || "-")} | route_mode=${escapeHtml(sourceTargetRoute.preferred_execution_mode || "-")} | route_fallback=${escapeHtml(sourceTargetRoute.fallback_execution_mode || "-")}</div>
      <div class="mono">source_path=${escapeHtml(sourcePath)} | browsing=${escapeHtml(browsingPath)}</div>
      ${sourceRuntime.selection_reason ? `<div>${escapeHtml(sourceRuntime.selection_reason)}</div>` : ""}
      ${sourceRuntime.fallback_reason ? `<div>${escapeHtml(sourceRuntime.fallback_reason)}</div>` : ""}
    `;
  }

  function renderTaskModeSummary(ctx) {
    const {
      activeTargetKey,
      configCache,
      capabilityAssessmentCache,
      sourceAnalyzeCache,
      capabilityLevelText,
      currentLang,
      translateDriverText,
      escapeHtml,
    } = ctx;
    const root = document.getElementById("task-mode-summary");
    if (!root) return;
    const sourcePath = String(document.getElementById("source_path")?.value || configCache?.source_path || "/").trim() || "/";
    const targetKey = activeTargetKey();
    const targetPath = String(document.getElementById("target_path")?.value || configCache?.target_path || "/").trim() || "/";
    const autoThreshold = String(document.getElementById("auto_download_threshold_mb")?.value || configCache?.auto_download_threshold_mb || "0").trim() || "0";
    const deleteRemoved = Boolean(document.getElementById("delete_removed")?.checked);
    const deleteRealTarget = Boolean(document.getElementById("target_delete_removed")?.checked);
    const sourcePreference = String(document.getElementById("source_provider_preference")?.value || configCache?.source_provider_preference || "auto").trim() || "auto";
    const recommendedMode = String(capabilityAssessmentCache?.strategy?.recommendedMode || "-");
    const assessedLevel = capabilityLevelText(capabilityAssessmentCache?.assessedLevel || capabilityAssessmentCache?.level || "unsupported");
    const rationale = capabilityAssessmentCache?.rationale
      ? translateDriverText(capabilityAssessmentCache.rationale.zh || "", capabilityAssessmentCache.rationale.en || "")
      : "";
    const sourceRuntime = window.__cpbStatusCache?.source_runtime || {};
    const sourceTargetRoute = sourceAnalyzeCache?.sourceTargetRoute || sourceRuntime.source_target_route || {};
    const statusTargetPreflight = window.__cpbStatusCache?.target_preflight || {};
    const statusTargetCapability = statusTargetPreflight?.adapter_capability || {};
    const transferPreviewText = sourceAnalyzeCache?.transferPlanPreview
      ? bridgeView.formatCountMap(ctx, sourceAnalyzeCache.transferPlanPreview.mode_counts || {}, (_ctx, key) => bridgeView.transferModeText(ctx, key))
      : "-";
    const previewReasonText = sourceAnalyzeCache?.transferPlanPreview
      ? bridgeView.formatCountMap(ctx, sourceAnalyzeCache.transferPlanPreview.reason_code_counts || {}, bridgeView.transferReasonCodeText)
      : "-";
    const previewNextActionText = sourceAnalyzeCache?.transferPlanPreview
      ? bridgeView.formatCountMap(ctx, sourceAnalyzeCache.transferPlanPreview.next_action_hint_counts || {}, bridgeView.nextActionHintText)
      : "-";
    const previewTargetFastGapText = sourceAnalyzeCache?.transferPlanPreview
      ? Object.entries(sourceAnalyzeCache.transferPlanPreview.missing_target_fast_hash_counts || {}).map(([k, v]) => `${k}:${v}`).join(" | ") || "-"
      : "-";
    const bridgePreparation = sourceRuntime.source_enrichment?.bridge_preparation_summary || sourceRuntime.source_enrichment?.bridge_runtime?.preparation || {};
    const captureCacheAvailable = !!bridgePreparation.capture_cache_available;
    const captureCacheLookupModes = Array.isArray(bridgePreparation.capture_cache_lookup_modes) ? bridgePreparation.capture_cache_lookup_modes : [];
    const captureCacheHashFields = Array.isArray(bridgePreparation.capture_cache_hash_fields) ? bridgePreparation.capture_cache_hash_fields : [];
    const captureCacheSummary = captureCacheAvailable
      ? `entries=${bridgePreparation.capture_cache_entry_count ?? 0} | lookup=${captureCacheLookupModes.join(", ") || "-"} | hashes=${captureCacheHashFields.join(", ") || "-"}`
      : "-";
    const routeBucket = String(sourceTargetRoute.decision_bucket || "-");
    const selectedMode = String(sourceRuntime.selected_source_mode || "-");
    const hasFast = !!statusTargetCapability.supports_fast_upload;
    const nextFocus = String(sourceTargetRoute.next_focus || "-");
    root.innerHTML = `
      <div class="summary-stack">
        <div><strong>${escapeHtml(sourcePath)}</strong> -> <strong>${escapeHtml(targetKey)}:${escapeHtml(targetPath)}</strong></div>
        <div class="summary-pill ${sourcePath === "/" || targetPath === "/" ? "warn" : ""}">${escapeHtml(currentLang() === "en" ? `Current route: ${selectedMode}` : currentLang() === "mix" ? `当前路线：${selectedMode} / Current route` : `当前路线：${selectedMode}`)}</div>
        <div class="summary-pill ${hasFast ? "" : "warn"}">${escapeHtml(currentLang() === "en" ? `Target fast upload: ${hasFast ? "available" : "fallback only"}` : currentLang() === "mix" ? `目标端快传：${hasFast ? "可用" : "仅降级"} / Target fast upload` : `目标端快传：${hasFast ? "可用" : "仅降级"}`)}</div>
        <div class="mono">${currentLang() === "en" ? "Recommended mode" : currentLang() === "mix" ? "建议模式 / Recommended mode" : "建议模式"}=${escapeHtml(recommendedMode)} | level=${escapeHtml(assessedLevel)} | auto_small_mb=${escapeHtml(autoThreshold)}</div>
        <div class="mono">${currentLang() === "en" ? "Source preference" : currentLang() === "mix" ? "源端偏好 / Source preference" : "源端偏好"}=${escapeHtml(sourcePreference)} | ${currentLang() === "en" ? "next focus" : currentLang() === "mix" ? "下一步关注 / next focus" : "下一步关注"}=${escapeHtml(nextFocus)} | ${currentLang() === "en" ? "route bucket" : currentLang() === "mix" ? "路线分桶 / route bucket" : "路线分桶"}=${escapeHtml(routeBucket)}</div>
        <div class="mono">${currentLang() === "en" ? "Transfer preview" : currentLang() === "mix" ? "传输预览 / Transfer preview" : "传输预览"}=${escapeHtml(transferPreviewText)}</div>
        <div class="mono">${currentLang() === "en" ? "Fast hashes" : currentLang() === "mix" ? "目标快传哈希 / Fast hashes" : "目标快传哈希"}=${escapeHtml((statusTargetCapability.fast_upload_hashes || []).join(", ") || "-")} | ${currentLang() === "en" ? "fallback" : currentLang() === "mix" ? "降级 / fallback" : "降级"}=${escapeHtml((statusTargetCapability.fallback_modes || []).join(", ") || "-")}</div>
        <div class="mono">${currentLang() === "en" ? "Cache and bridge" : currentLang() === "mix" ? "缓存与桥接 / Cache and bridge" : "缓存与桥接"}=${escapeHtml(captureCacheSummary)}</div>
        <div class="mono">${currentLang() === "en" ? "Delete policy" : currentLang() === "mix" ? "删除策略 / Delete policy" : "删除策略"}=${deleteRemoved ? "state:on" : "state:off"} | ${deleteRealTarget ? "target:on" : "target:off"}</div>
        ${sourceRuntime.selection_reason ? `<div>${escapeHtml(sourceRuntime.selection_reason)}</div>` : ""}
        ${sourceRuntime.fallback_reason ? `<div>${escapeHtml(sourceRuntime.fallback_reason)}</div>` : ""}
        ${rationale ? `<div>${escapeHtml(rationale)}</div>` : ""}
      </div>
    `;
  }

  function renderWorkflowSummaries(ctx, syncState = {}, runtimeState = {}) {
    ctx.renderOverviewRouteSummary(syncState, runtimeState);
    renderSourceDriverSummary(ctx);
    renderTaskModeSummary(ctx);
    ctx.applyWorkflowGates();
  }

  window.CloudPanBridgeWorkflow = {
    renderCapabilitySummary,
    renderSourceAnalyze,
    renderSourceDriverSummary,
    renderTaskModeSummary,
    renderWorkflowSummaries,
  };
})();
