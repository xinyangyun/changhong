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
  { id: "lessons", label: "经验教训" },
];

const sectors = computed(() => fundFlowData.value?.sectors ?? []);
const stocks = ref([
  { name: "贵州茅台", code: "600519", price: "1,482.50", change: "+1.28%", desc: "白酒龙头保持稳健走势，短期关注量能是否继续配合。" },
]);
const activeStockIndex = ref(0);

const showAddStock = ref(false);
const newStockCode = ref("");

function addStock() {
  if (!newStockCode.value) return;
  stocks.value.push({
    name: newStockCode.value,
    code: newStockCode.value,
    price: "待更新",
    change: "待更新",
    desc: "等待数据分析",
  });
  newStockCode.value = "";
  activeStockIndex.value = stocks.value.length - 1;
  showAddStock.value = false;
}

function removeStock(index) {
  stocks.value.splice(index, 1);
  if (activeStockIndex.value >= stocks.value.length) {
    activeStockIndex.value = Math.max(0, stocks.value.length - 1);
  }
}
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

      <section v-else-if="activeView === 'analysis'" class="funds-layout">
        <div class="sector-tabs" aria-label="个股切换">
          <button
            v-for="(stock, si) in stocks"
            :key="stock.code"
            type="button"
            :class="{ active: activeStockIndex === si }"
            @click="activeStockIndex = si"
          >
            <span>{{ stock.name }}</span>
            <strong>{{ stock.code }}</strong>
          </button>
          <button type="button" class="add-stock-tab" @click="showAddStock = true">＋</button>
        </div>

        <template v-if="stocks.length > 0">
          <div class="content-grid analysis-grid">
            <article class="stock-card">
              <p class="eyebrow">Stock Focus</p>
              <h2>{{ stocks[activeStockIndex].name }} {{ stocks[activeStockIndex].code }}</h2>
              <div class="price-line">
                <strong>{{ stocks[activeStockIndex].price }}</strong>
                <span>{{ stocks[activeStockIndex].change }}</span>
              </div>
              <p>{{ stocks[activeStockIndex].desc }}</p>
              <button type="button" class="delete-stock-btn" @click="removeStock(activeStockIndex)" v-if="stocks.length > 1">删除该股</button>
            </article>

            <article class="summary-card">
              <span>趋势强度</span>
              <strong>偏强</strong>
              <small>均线多头排列，短期动能保持</small>
            </article>
            <article class="summary-card">
              <span>资金关注</span>
              <strong>高</strong>
              <small>近 5 日主力净流入排名靠前</small>
            </article>
            <article class="summary-card">
              <span>风险提示</span>
              <strong>中</strong>
              <small>高位震荡时注意成交量变化</small>
            </article>
          </div>
        </template>

        <div v-if="showAddStock" class="add-item-area">
          <form class="add-form" @submit.prevent="addStock">
            <input v-model="newStockCode" placeholder="输入股票名称或代码" required />
            <div class="form-actions">
              <button type="submit" class="add-btn submit">确认添加</button>
              <button type="button" class="cancel-btn" @click="showAddStock = false">取消</button>
            </div>
          </form>
        </div>
      </section>

      <section v-else-if="activeView === 'lessons'" class="lessons-layout">
        <div class="content-grid lessons-grid">
          <article class="summary-card highlight">
            <span>投资格言</span>
            <strong>敬畏市场，知行合一</strong>
            <small>计划交易，交易计划</small>
          </article>
          <article class="summary-card">
            <span>总则</span>
            <strong>不预测，只应对</strong>
            <small>跟随趋势，做好风控</small>
          </article>
          <article class="summary-card">
            <span>核心纪律</span>
            <strong>截断亏损，让利润奔跑</strong>
            <small>止损不拖，止盈不贪</small>
          </article>
        </div>

        <article class="data-panel">
          <div class="panel-head">
            <h2>📋 交易经验教训清单</h2>
            <span>操作中总结，复盘后沉淀</span>
          </div>
          <div class="table">
            <div class="table-row table-head lesson-table">
              <span>类别</span>
              <span>经验教训</span>
              <span>改进措施</span>
            </div>
            <div class="table-row lesson-table">
              <span><strong>仓位管理</strong></span>
              <span>单票重仓导致回撤过大，心态失衡后操作变形</span>
              <span class="rise">单票仓位不超过 20%，分批进场</span>
            </div>
            <div class="table-row lesson-table">
              <span><strong>止损执行</strong></span>
              <span>心存侥幸未按计划止损，小亏变深套</span>
              <span class="rise">到止损位无条件执行，不看盘面</span>
            </div>
            <div class="table-row lesson-table">
              <span><strong>追涨杀跌</strong></span>
              <span>拉升时追高被套，恐慌时割肉在地板</span>
              <span class="rise">等回调低吸，不在急涨时追入</span>
            </div>
            <div class="table-row lesson-table">
              <span><strong>情绪管理</strong></span>
              <span>连续亏损后急于回本，频繁操作越亏越多</span>
              <span class="rise">连续亏损 2 笔暂停交易，复盘后再操作</span>
            </div>
            <div class="table-row lesson-table">
              <span><strong>复盘习惯</strong></span>
              <span>交易完不复盘，同样的错误反复犯</span>
              <span class="rise">每日收盘后写交易日志，每周总结</span>
            </div>
            <div class="table-row lesson-table">
              <span><strong>市场节奏</strong></span>
              <span>震荡市当趋势做，方向不明频繁开仓</span>
              <span class="rise">先判断市场环境，再制定交易策略</span>
            </div>
          </div>
        </article>

        <div class="content-grid" style="margin-top: 0">
          <article class="stock-card">
            <p class="eyebrow">Trading Wisdom</p>
            <h2>🎯 四不原则</h2>
            <p style="line-height: 2; margin-bottom: 4px">不逆势——趋势是你的朋友</p>
            <p style="line-height: 2; margin-bottom: 4px">不重仓——留得青山在</p>
            <p style="line-height: 2; margin-bottom: 4px">不扛单——止损要果断</p>
            <p style="line-height: 2; margin-bottom: 4px">不频繁——耐心等待机会</p>
          </article>
          <article class="stock-card">
            <p class="eyebrow">Mindset</p>
            <h2>🧠 心态修炼</h2>
            <p style="line-height: 2; margin-bottom: 4px">✅ 盈利不骄傲——市场永远有机会</p>
            <p style="line-height: 2; margin-bottom: 4px">✅ 亏损不气馁——每笔亏损都是学费</p>
            <p style="line-height: 2; margin-bottom: 4px">✅ 错过不遗憾——市场永远开门</p>
            <p style="line-height: 2; margin-bottom: 4px">✅ 做错不抱怨——只从自身找原因</p>
          </article>
          <article class="stock-card">
            <p class="eyebrow">Daily Checklist</p>
            <h2>📌 每日必做</h2>
            <p style="line-height: 2; margin-bottom: 4px">✅ 盘前：制定当日交易计划</p>
            <p style="line-height: 2; margin-bottom: 4px">✅ 盘中：严格执行计划</p>
            <p style="line-height: 2; margin-bottom: 4px">✅ 盘后：写交易日志并复盘</p>
            <p style="line-height: 2; margin-bottom: 4px">✅ 周末：总结本周，规划下周</p>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>
