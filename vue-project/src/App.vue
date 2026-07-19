<script setup>
import { computed, onMounted, ref } from "vue";

const activeView = ref("funds");
const activeSectorId = ref("");
const fundFlowData = ref(null);
const isLoadingFundFlow = ref(false);
const fundFlowError = ref("");

const navItems = [
  { id: "funds", label: "主力资金" },
  { id: "analysis", label: "个股分析" },
];

const analysisItems = [
  { label: "趋势强度", value: "偏强", detail: "均线多头排列，短期动能保持" },
  { label: "资金关注", value: "高", detail: "近 5 日主力净流入排名靠前" },
  { label: "风险提示", value: "中", detail: "高位震荡时注意成交量变化" },
];

const sectors = computed(() => fundFlowData.value?.sectors ?? []);
const summary = computed(() => fundFlowData.value?.summary ?? null);
const activeSector = computed(() => {
  return sectors.value.find((sector) => sector.id === activeSectorId.value) ?? sectors.value[0] ?? null;
});

async function loadFundFlows() {
  isLoadingFundFlow.value = true;
  fundFlowError.value = "";

  try {
    const response = await fetch("http://127.0.0.1:8000/api/sectors/fund-flows");

    if (!response.ok) {
      throw new Error(`接口返回 ${response.status}`);
    }

    const data = await response.json();
    fundFlowData.value = data;
    activeSectorId.value = data.sectors?.[0]?.id ?? "";
  } catch (error) {
    fundFlowError.value = error instanceof Error ? error.message : "资金数据加载失败";
  } finally {
    isLoadingFundFlow.value = false;
  }
}

onMounted(loadFundFlows);
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark">CH</span>
        <div>
          <strong>长虹证券看板</strong>
          <span>A 股资金与个股研判</span>
        </div>
      </div>

      <nav class="nav-tabs" aria-label="主导航">
        <button
          v-for="item in navItems"
          :key="item.id"
          type="button"
          :class="{ active: activeView === item.id }"
          @click="activeView = item.id"
        >
          {{ item.label }}
        </button>
      </nav>
    </header>

    <main class="workspace">
      <section class="hero">
        <p class="eyebrow">Market Dashboard</p>
        <h1>主力动向与个股机会一屏掌握</h1>
        <p class="intro">聚焦资金流、趋势强弱和风险信号，给日常盯盘一个清爽入口。</p>
      </section>

      <section v-if="activeView === 'funds'" class="funds-layout">
        <div v-if="isLoadingFundFlow" class="state-panel">正在加载板块资金数据...</div>
        <div v-else-if="fundFlowError" class="state-panel error">
          <strong>资金数据加载失败</strong>
          <span>请先启动 Python 后端：PYTHONPATH=src python3 -m python_project</span>
        </div>

        <template v-else-if="activeSector && summary">
          <section class="content-grid">
            <article class="summary-card highlight">
              <span>板块合计净流入</span>
              <strong>{{ summary.total_net_inflow_text }}</strong>
              <small>{{ summary.sector_count }} 个板块纳入监控</small>
            </article>
            <article class="summary-card">
              <span>最强板块</span>
              <strong>{{ summary.hot_sector }}</strong>
              <small>净流入 {{ summary.hot_sector_net_inflow_text }}</small>
            </article>
            <article class="summary-card">
              <span>更新时间</span>
              <strong class="time-text">{{ fundFlowData.updated_at }}</strong>
              <small>数据由 Python 后端提供</small>
            </article>
          </section>

          <section class="sector-tabs" aria-label="板块切换">
            <button
              v-for="sector in sectors"
              :key="sector.id"
              type="button"
              :class="{ active: activeSectorId === sector.id }"
              @click="activeSectorId = sector.id"
            >
              <span>{{ sector.name }}</span>
              <strong>{{ sector.net_inflow_text }}</strong>
            </button>
          </section>

          <section class="sector-overview">
            <article class="stock-card sector-focus">
              <p class="eyebrow">Sector Focus</p>
              <h2>{{ activeSector.name }}</h2>
              <p>{{ activeSector.description }}</p>
            </article>
            <article class="summary-card">
              <span>主力净流入</span>
              <strong>{{ activeSector.main_inflow_text }}</strong>
              <small>板块涨跌 {{ activeSector.change_percent_text }}</small>
            </article>
            <article class="summary-card">
              <span>成交额</span>
              <strong>{{ activeSector.turnover_text }}</strong>
              <small>资金活跃度参考</small>
            </article>
          </section>

          <article class="data-panel">
            <div class="panel-head">
              <h2>{{ activeSector.name }}资金流入排行</h2>
              <span>按主力净流入展示</span>
            </div>
            <div class="table">
              <div class="table-row table-head fund-table">
                <span>股票</span>
                <span>现价</span>
                <span>涨跌幅</span>
                <span>主力净流入</span>
                <span>占比</span>
                <span>状态</span>
              </div>
              <div
                v-for="stock in activeSector.stocks"
                :key="stock.code"
                class="table-row fund-table"
              >
                <span>
                  <strong>{{ stock.name }}</strong>
                  <small>{{ stock.code }}</small>
                </span>
                <span>{{ stock.price_text }}</span>
                <span :class="stock.change_percent >= 0 ? 'rise' : 'fall'">
                  {{ stock.change_percent_text }}
                </span>
                <span :class="stock.net_inflow >= 0 ? 'rise' : 'fall'">
                  {{ stock.net_inflow_text }}
                </span>
                <span>{{ stock.inflow_ratio_text }}</span>
                <span>{{ stock.signal }}</span>
              </div>
            </div>
          </article>
        </template>
      </section>

      <section v-else class="content-grid analysis-grid">
        <article class="stock-card">
          <p class="eyebrow">Stock Focus</p>
          <h2>贵州茅台 600519</h2>
          <div class="price-line">
            <strong>1,482.50</strong>
            <span>+1.28%</span>
          </div>
          <p>白酒龙头保持稳健走势，短期关注量能是否继续配合。</p>
        </article>

        <article v-for="item in analysisItems" :key="item.label" class="summary-card">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <small>{{ item.detail }}</small>
        </article>
      </section>
    </main>
  </div>
</template>
