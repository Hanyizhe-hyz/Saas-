import math
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="利润量化分析工具",
    page_icon="💰",
    layout="wide"
)

# =========================
# 页面样式
# =========================
st.markdown("""
<style>
.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #1a6dff;
    margin-bottom: 0.3rem;
}
.sub-title {
    color: #666;
    margin-bottom: 1.5rem;
}
.summary-card {
    background: #f8faff;
    border: 1px solid #e1e8ff;
    border-radius: 12px;
    padding: 18px;
    margin-top: 10px;
}
.analysis-box {
    background: #ffffff;
    border: 1px solid #f0f0f0;
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.03);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💰 利润量化分析工具</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">基于运费与汇率自动生成盈亏平衡曲线</div>', unsafe_allow_html=True)

# =========================
# 计算函数
# =========================
def calculate_metrics(
    shipping_cost_usd: float,
    exchange_rate: float,
    product_cost_cny: float,
    selling_price_cny: float,
    fixed_cost_cny: float,
):
    shipping_cost_cny = shipping_cost_usd * exchange_rate
    variable_cost_per_item = shipping_cost_cny + product_cost_cny
    profit_per_item = selling_price_cny - variable_cost_per_item
    margin = (profit_per_item / selling_price_cny * 100) if selling_price_cny > 0 else 0

    if profit_per_item > 0 and fixed_cost_cny > 0:
        break_even = math.ceil(fixed_cost_cny / profit_per_item)
        status = "break_even_exists"
    elif profit_per_item > 0 and fixed_cost_cny == 0:
        break_even = 0
        status = "immediate_profit"
    else:
        break_even = None
        status = "cannot_profit"

    return {
        "shipping_cost_cny": shipping_cost_cny,
        "variable_cost_per_item": variable_cost_per_item,
        "profit_per_item": profit_per_item,
        "margin": margin,
        "break_even": break_even,
        "status": status,
    }


def build_chart_data(
    shipping_cost_cny: float,
    product_cost_cny: float,
    selling_price_cny: float,
    fixed_cost_cny: float,
    sales_range: int,
):
    labels = list(range(0, sales_range + 1))
    variable_cost_per_item = shipping_cost_cny + product_cost_cny

    total_cost = [fixed_cost_cny + variable_cost_per_item * x for x in labels]
    total_revenue = [selling_price_cny * x for x in labels]
    profit = [r - c for r, c in zip(total_revenue, total_cost)]

    return pd.DataFrame({
        "销量": labels,
        "总成本": total_cost,
        "总收入": total_revenue,
        "利润": profit
    })


def generate_analysis_text(metrics, selling_price_cny, fixed_cost_cny, product_cost_cny):
    profit_per_item = metrics["profit_per_item"]
    margin = metrics["margin"]
    break_even = metrics["break_even"]
    variable_cost_per_item = metrics["variable_cost_per_item"]
    shipping_cost_cny = metrics["shipping_cost_cny"]
    status = metrics["status"]

    if status == "break_even_exists":
        return f"""
**结论：当前方案可盈利。**

- 单件利润为 **{profit_per_item:.2f} CNY**
- 单件利润率为 **{margin:.1f}%**
- 需要销售 **{break_even} 件** 才能覆盖固定成本 **{fixed_cost_cny:.2f} CNY**

**建议：**
1. 超过盈亏平衡点后，每多销售一件可新增 **{profit_per_item:.2f} CNY** 利润。  
2. 可以进一步优化运费与产品成本，提高利润率。  
3. 若用于比赛展示，可强调“系统可自动测算盈亏平衡点与利润敏感性”。  
"""

    if status == "immediate_profit":
        return f"""
**结论：当前方案从第 1 件开始盈利。**

- 单件利润为 **{profit_per_item:.2f} CNY**
- 单件利润率为 **{margin:.1f}%**
- 当前固定成本为 **0 CNY**，因此无需等待盈亏平衡点。

**建议：**
1. 可以进一步扩大销量，放大盈利规模。  
2. 若后续增加广告费、内容投放费、人工费，可重新测算固定成本。  
"""

    return f"""
**结论：当前方案无法盈利。**

- 单件亏损为 **{abs(profit_per_item):.2f} CNY**
- 当前变动成本为 **{variable_cost_per_item:.2f} CNY**
- 当前售价为 **{selling_price_cny:.2f} CNY**

**建议：**
1. 降低运输成本，当前运输成本折合 **{shipping_cost_cny:.2f} CNY/件**
2. 降低产品成本，当前产品成本为 **{product_cost_cny:.2f} CNY/件**
3. 提高销售价格
4. 做“文化转译溢价”验证，看是否能提升售价空间
"""


# =========================
# 侧边输入
# =========================
left_col, right_col = st.columns([1, 1.6])

with left_col:
    st.subheader("📊 成本与汇率参数")

    shipping_cost_usd = st.slider("运输成本 (USD/件)", 1.0, 50.0, 15.3, 0.1)
    exchange_rate = st.slider("汇率 (USD/CNY)", 6.0, 8.0, 6.85, 0.01)
    product_cost_cny = st.number_input("产品成本 (CNY/件)", min_value=0.0, value=45.0, step=1.0)
    selling_price_cny = st.number_input("销售价格 (CNY/件)", min_value=0.0, value=120.0, step=1.0)
    fixed_cost_cny = st.number_input("固定成本 (CNY)", min_value=0.0, value=1000.0, step=100.0)
    sales_range = st.selectbox("销售量分析范围 (件)", [100, 200, 500, 1000], index=1)

    metrics = calculate_metrics(
        shipping_cost_usd,
        exchange_rate,
        product_cost_cny,
        selling_price_cny,
        fixed_cost_cny
    )

    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    st.subheader("盈亏平衡分析摘要")

    c1, c2 = st.columns(2)
    c1.metric("运输成本/件 (CNY)", f"{metrics['shipping_cost_cny']:.2f}")
    c2.metric("产品成本/件 (CNY)", f"{product_cost_cny:.2f}")

    c3, c4 = st.columns(2)
    c3.metric("总变动成本/件", f"{metrics['variable_cost_per_item']:.2f}")
    c4.metric("毛利润/件", f"{metrics['profit_per_item']:.2f}")

    c5, c6 = st.columns(2)
    if metrics["break_even"] is None:
        c5.metric("盈亏平衡点", "无法盈利")
    else:
        c5.metric("盈亏平衡点", f"{metrics['break_even']} 件")

    c6.metric("临界利润率", f"{metrics['margin']:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.subheader("📈 盈亏平衡曲线分析")

    df = build_chart_data(
        metrics["shipping_cost_cny"],
        product_cost_cny,
        selling_price_cny,
        fixed_cost_cny,
        sales_range
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["销量"],
        y=df["总成本"],
        mode="lines",
        name="总成本曲线"
    ))
    fig.add_trace(go.Scatter(
        x=df["销量"],
        y=df["总收入"],
        mode="lines",
        name="总收入曲线"
    ))

    if metrics["break_even"] is not None and metrics["break_even"] <= sales_range:
        be_x = metrics["break_even"]
        be_y = fixed_cost_cny + metrics["variable_cost_per_item"] * be_x
        fig.add_trace(go.Scatter(
            x=[be_x],
            y=[be_y],
            mode="markers+text",
            name="盈亏平衡点",
            text=[f"BE={be_x}"],
            textposition="top center",
            marker=dict(size=10)
        ))

    fig.update_layout(
        height=520,
        xaxis_title="销售数量 (件)",
        yaxis_title="金额 (CNY)",
        legend_title="图例",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
    st.subheader("分析结论")
    st.markdown(
        generate_analysis_text(
            metrics,
            selling_price_cny,
            fixed_cost_cny,
            product_cost_cny
        )
    )
    st.markdown('</div>', unsafe_allow_html=True)