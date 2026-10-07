/* 人生域登记表（PLAN v2 §二轴一）——域是个人宪法：一行一域，定了少动。
   规矩：有首张卡才建（正本 frontmatter domain: 首次出现该域时）；渲染层按本表顺序展示，
   insight（_data/insight.js）里没有数据的启用域如实显示「还没长」。
   候选域只登记注释，首卡落地时启用并移入上方列表。 */
window.MARVIS_DOMAINS = [
  { id: 'shiye', name: '事业', color: '#4C82B8', desc: '秋招、项目、工作输出与职业决策' },
  { id: 'xueshi', name: '学识', color: '#7F9C7A', desc: '技术学习、阅读与思想框架' },
  { id: 'guanxi', name: '关系', color: '#D85A30', desc: '人、沟通、出牌与家庭' },
  { id: 'shenxin', name: '身心', color: '#993C1D', desc: '睡眠饮食运动、心态与情绪' }
];
/* 候选域（未启用）：财富（理财、消费决策、风险）· 审美（鉴赏、生活趣味） */
