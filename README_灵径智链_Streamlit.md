# 灵径智链 Streamlit 统一平台 Demo

## 运行方式

```bash
pip install -r requirements_lingjing.txt
streamlit run lingjing_platform.py
```

## 当前集成模块

- 平台总览
- 文化风控数据库
- ProfitLab 利润量化
  - 盈亏分析
  - 情景模拟
  - 多 SKU 对比
  - AI 顾问
- Puente 履约清关
  - 订单追踪
  - 数据看板
  - 清关中心
  - 系统工具

## 说明

这是一个基于现有两个原型整合出的单文件 Streamlit Demo，重点是：

1. 把三大功能集成为同一平台
2. 尽量贴近你们现有原型的视觉结构
3. 让后续接真实接口和真实数据库更容易

## 下一步建议

1. 把文化风控规则库抽成 JSON / 数据库表
2. 把 ProfitLab 参数接入真实物流、平台佣金和广告成本
3. 把 Puente 订单追踪接入真实 API
4. 增加登录、角色权限和项目保存
5. 把文件预审替换成 OCR / 文档识别流程
