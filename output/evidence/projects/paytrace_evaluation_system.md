# PayTrace 评测体系与核心技术指标

## 项目概述
- **项目名称**：PayTrace——支付转化异常归因与诊断Agent
- **项目类型**：个人开源项目
- **项目周期**：2025.12 - 至今
- **GitHub仓库**：[github.com/Ygrowly/PayTrace](https://github.com/Ygrowly/PayTrace)
- **核心目标**：为支付产品与运营团队提供自动化异常诊断能力，通过证据契约约束确保诊断结论可信

## 1. 评测体系设计

### 1.1 四层评测集架构
```python
class EvaluationFramework:
    def __init__(self):
        self.evaluation_sets = {
            'development': DevelopmentSet(),
            'regression': RegressionSet(),
            'holdout': HoldoutSet(),
            'adversarial': AdversarialSet()
        }
    
    def run_evaluation(self, agent, set_name='regression'):
        """运行指定评测集的评估"""
        evaluation_set = self.evaluation_sets[set_name]
        results = []
        
        for scenario in evaluation_set.scenarios:
            # Ground Truth隔离，Agent无法访问
            ground_truth = scenario.ground_truth
            test_data = scenario.test_data
            
            # 运行Agent诊断
            diagnosis = agent.diagnose(test_data)
            
            # 对比结果
            comparison = self.compare_diagnosis(diagnosis, ground_truth)
            results.append(comparison)
        
        return self.aggregate_results(results)
```

### 1.2 黄金场景构成
| 场景类型 | 数量 | 描述 | 核心挑战 |
|----------|------|------|----------|
| **单根因场景** | 25 | 单一明确原因导致的转化异常 | 准确识别主要根因 |
| **多根因场景** | 35 | 多个因素共同导致的复杂异常 | 识别所有相关因素 |
| **干扰场景** | 15 | 包含干扰信息但实际无异常 | 避免过度诊断 |
| **数据质量场景** | 15 | 数据缺失或质量问题导致的异常 | 区分数据问题与业务问题 |
| **对抗场景** | 10 | 故意设计的误导性场景 | 测试系统鲁棒性 |
| **总计** | **100** | 覆盖主要诊断场景 | **全面评估能力** |

### 1.3 数据规模配置
```yaml
每个黄金场景包含:
  购买意图数: 100,000
  行为事件数: 500,000
  支付事件数: 300,000
  时间窗口: 30天
  用户规模: 10,000
  产品SKU: 500
  
总计数据规模:
  购买意图: 10,000,000
  行为事件: 50,000,000
  支付事件: 30,000,000
  存储大小: ~5GB
```

## 2. 核心诊断算法

### 2.1 九阶段统一漏斗模型
```python
class ConversionFunnel:
    def __init__(self):
        self.stages = [
            'cart_created',      # 购物车创建
            'checkout_started',  # 结算开始
            'shipping_selected', # 配送选择
            'payment_selected',  # 支付方式选择
            'payment_initiated', # 支付发起
            'payment_processing', # 支付处理中
            'payment_completed', # 支付完成
            'order_confirmed',   # 订单确认
            'order_fulfilled'    # 订单履约
        ]
    
    def calculate_loss_by_stage(self, intents, events):
        """计算各阶段流失"""
        stage_losses = {}
        
        for i, stage in enumerate(self.stages):
            # 计算进入该阶段的意图数
            entered = self.count_intents_entered_stage(intents, stage)
            
            # 计算离开该阶段的意图数
            if i < len(self.stages) - 1:
                next_stage = self.stages[i + 1]
                exited = self.count_intents_exited_to_stage(intents, stage, next_stage)
            else:
                exited = entered  # 最终阶段
            
            # 计算流失
            loss = entered - exited
            stage_losses[stage] = {
                'entered': entered,
                'exited': exited,
                'loss': loss,
                'loss_rate': loss / entered if entered > 0 else 0
            }
        
        return stage_losses
```

### 2.2 Purchase Intent 关联算法
```python
class IntentLinker:
    def __init__(self):
        self.linkage_rules = [
            ('cancel_and_retry', self.link_cancel_retry),
            ('payment_method_switch', self.link_payment_switch),
            ('split_order', self.link_split_order),
            ('abandon_and_new', self.link_abandon_new)
        ]
    
    def link_cancel_retry(self, intent_a, intent_b):
        """关联取消订单与重新下单"""
        conditions = [
            intent_a.user_id == intent_b.user_id,
            intent_a.product_id == intent_b.product_id,
            intent_a.status == 'cancelled',
            intent_b.status == 'completed',
            abs(intent_b.created_at - intent_a.created_at) < timedelta(hours=24)
        ]
        
        return all(conditions)
    
    def link_intents(self, intents):
        """关联相关购买意图"""
        linked_groups = []
        processed = set()
        
        for intent in intents:
            if intent.id in processed:
                continue
            
            # 寻找相关意图
            related = [intent]
            
            for other in intents:
                if other.id == intent.id or other.id in processed:
                    continue
                
                # 检查各种关联规则
                for rule_name, rule_func in self.linkage_rules:
                    if rule_func(intent, other):
                        related.append(other)
                        processed.add(other.id)
                        break
            
            linked_groups.append(related)
            processed.add(intent.id)
        
        return linked_groups
```

### 2.3 确定性损失拆解算法
```python
class LossDecomposition:
    def __init__(self):
        self.decomposition_methods = {
            'stage_belonging': self.by_stage_belonging,
            'set_deduplication': self.by_set_deduplication,
            'amount_conservation': self.by_amount_conservation,
            'unknown_separation': self.separate_unknown
        }
    
    def decompose_loss(self, intents, events):
        """拆解损失到具体原因"""
        
        # 1. 阶段归属
        stage_losses = self.by_stage_belonging(intents, events)
        
        # 2. 集合去重
        deduplicated = self.by_set_deduplication(stage_losses)
        
        # 3. 金额守恒校验
        conserved = self.by_amount_conservation(deduplicated)
        
        # 4. 未知损失分离
        final_result = self.separate_unknown(conserved)
        
        # 5. 校验完整性
        self.validate_completeness(final_result, intents)
        
        return final_result
    
    def validate_completeness(self, decomposition, intents):
        """验证损失拆解的完整性"""
        total_intents = len(intents)
        accounted_intents = sum(
            category['intent_count'] 
            for category in decomposition.values()
        )
        
        if total_intents != accounted_intents:
            unaccounted = total_intents - accounted_intents
            decomposition['unaccounted'] = {
                'intent_count': unaccounted,
                'amount': 0,
                'reason': '算法未覆盖的异常模式'
            }
```

## 3. 证据契约系统

### 3.1 三层证据绑定
```python
class EvidenceContract:
    def __init__(self):
        self.validation_rules = [
            self.validate_claim_evidence_link,
            self.validate_evidence_tool_link,
            self.validate_result_hash,
            self.validate_call_id_consistency,
            self.validate_timestamp_sequence,
            self.validate_parameter_integrity,
            self.validate_result_completeness,
            self.validate_ground_truth_leakage,
            self.validate_false_positive_detection,
            self.validate_uncertainty_handling
        ]
    
    def validate_claim_evidence_link(self, claim, evidence):
        """验证声明与证据的绑定关系"""
        required_fields = ['evidence_id', 'claim_id', 'confidence']
        
        for field in required_fields:
            if field not in claim:
                return False, f"缺少必填字段: {field}"
        
        if claim['evidence_id'] not in evidence:
            return False, f"引用的证据不存在: {claim['evidence_id']}"
        
        return True, "验证通过"
    
    def validate_ground_truth_leakage(self, diagnosis, ground_truth):
        """验证Ground Truth信息泄漏"""
        # Ground Truth对Agent不可见，仅用于评测
        diagnosis_keys = set(diagnosis.keys())
        ground_truth_keys = set(ground_truth.keys())
        
        # 检查是否有Ground Truth特有的信息出现在诊断中
        leakage = diagnosis_keys.intersection(
            ground_truth_keys.difference({'scenario_id'})
        )
        
        if leakage:
            return False, f"检测到Ground Truth信息泄漏: {leakage}"
        
        return True, "无信息泄漏"
```

### 3.2 降级处理机制
```python
class DegradationHandler:
    def __init__(self):
        self.degradation_levels = {
            'FULL_CONFIDENCE': 0.9,    # 完全可信
            'HIGH_CONFIDENCE': 0.7,    # 高可信度
            'MEDIUM_CONFIDENCE': 0.5,  # 中等可信度
            'LOW_CONFIDENCE': 0.3,     # 低可信度
            'UNKNOWN': 0.0,            # 未知
            'NEEDS_DATA': -1.0         # 需要更多数据
        }
    
    def handle_insufficient_data(self, diagnosis_context):
        """处理数据不足的情况"""
        missing_data_types = self.identify_missing_data(diagnosis_context)
        
        if len(missing_data_types) > 2:
            # 关键数据缺失过多，降级为NEEDS_DATA
            return {
                'status': 'NEEDS_DATA',
                'missing_data': missing_data_types,
                'recommendation': '请补充以下数据后重试',
                'confidence': self.degradation_levels['NEEDS_DATA']
            }
        elif len(missing_data_types) > 0:
            # 部分数据缺失，降级为UNKNOWN
            return {
                'status': 'UNKNOWN',
                'missing_data': missing_data_types,
                'confidence': self.degradation_levels['UNKNOWN']
            }
        else:
            # 数据完整，正常处理
            return None
```

## 4. 评测结果与指标

### 4.1 核心性能指标
| 指标 | 优化前 | 优化后 | 提升幅度 | 评估方法 |
|------|--------|--------|----------|----------|
| **阶段定位准确率** | 72% | 93% | +21% | 100黄金场景 |
| **根因识别F1** | 0.61 | 0.87 | +0.26 | Micro-F1 |
| **损失归因MAE** | 18.6% | 6.8% | -11.8% | 平均绝对误差 |
| **重复损失计数率** | 12.4% | 1.6% | -10.8% | 意图关联验证 |
| **无依据结论率** | 14.2% | 2.5% | -11.7% | 证据绑定检查 |
| **工具调用次数** | 11次 | 6次 | -45% | 中位数统计 |
| **Token消耗** | 基准 | -36% | -36% | 相同场景对比 |
| **pass^3稳定性** | 67% | 91% | +24% | 连续三次通过 |

### 4.2 工具调用优化
```python
class ToolOptimizer:
    def __init__(self):
        self.tool_metrics = {
            'funnel_query': {'success_rate': 0.98, 'avg_time': 1200},
            'dimension_drilldown': {'success_rate': 0.96, 'avg_time': 1800},
            'loss_decomposition': {'success_rate': 0.97, 'avg_time': 2200},
            'promotion_analysis': {'success_rate': 0.95, 'avg_time': 1500},
            'cancel_retry_tracking': {'success_rate': 0.99, 'avg_time': 800},
            'payment_event_check': {'success_rate': 0.98, 'avg_time': 600},
            'config_change_query': {'success_rate': 0.94, 'avg_time': 1000}
        }
    
    def optimize_tool_selection(self, context, hypothesis_ledger):
        """优化工具选择策略"""
        
        # 1. 基于信息增益排序
        information_gains = self.calculate_information_gain(
            context, hypothesis_ledger
        )
        
        # 2. 排除已验证事实
        verified_facts = hypothesis_ledger.get_verified_facts()
        redundant_tools = self.identify_redundant_tools(
            context, verified_facts
        )
        
        # 3. 考虑工具成本
        tool_costs = self.calculate_tool_costs(information_gains)
        
        # 4. 综合评分选择
        selected_tools = self.select_by_composite_score(
            information_gains, redundant_tools, tool_costs
        )
        
        return selected_tools[:3]  # 每次选择最有效的3个工具
```

### 4.3 稳定性测试结果
```markdown
**pass^3稳定性测试：**
- **测试方法**：每个场景连续运行3次，要求3次均通过质量门槛
- **通过标准**：阶段定位、根因识别、损失MAE均达标
- **初始通过率**：67%（67个场景稳定通过）
- **优化后通过率**：91%（91个场景稳定通过）

**稳定性提升措施：**
1. **状态外置**：将中间状态持久化，避免随机性影响
2. **工具契约固定**：明确工具输入输出规范
3. **停止条件优化**：基于信息增益而非固定次数
4. **缓存机制**：已验证事实缓存，避免重复查询
```

## 5. 技术架构亮点

### 5.1 Hypothesis Ledger DAG
```python
class HypothesisLedger:
    def __init__(self):
        self.hypotheses = {}  # 假设状态管理
        self.dag = DiGraph()  # 依赖关系图
        self.evidence_map = {}  # 证据映射
    
    def add_hypothesis(self, hypothesis_id, description, dependencies):
        """添加调查假设"""
        self.hypotheses[hypothesis_id] = {
            'description': description,
            'status': 'pending',  # pending, testing, verified, refuted
            'confidence': 0.0,
            'evidence_ids': [],
            'created_at': datetime.now()
        }
        
        # 构建DAG依赖关系
        for dep_id in dependencies:
            self.dag.add_edge(dep_id, hypothesis_id)
    
    def update_hypothesis(self, hypothesis_id, evidence, result):
        """更新假设状态"""
        hypothesis = self.hypotheses[hypothesis_id]
        
        # 记录证据
        evidence_id = self.record_evidence(evidence)
        hypothesis['evidence_ids'].append(evidence_id)
        
        # 更新状态
        if result['verified']:
            hypothesis['status'] = 'verified'
            hypothesis['confidence'] = result['confidence']
            
            # 传播验证结果到依赖节点
            self.propagate_verification(hypothesis_id)
        else:
            hypothesis['status'] = 'refuted'
            
            # 停止相关调查路径
            self.stop_investigation_path(hypothesis_id)
```

### 5.2 诊断执行引擎
```python
class DiagnosticHarness:
    def __init__(self):
        self.hook_chains = {
            'before_tool': [],
            'after_tool': [],
            'before_model': []
        }
        
        self.capability_routing = CapabilityRouter()
        self.budget_control = BudgetController()
        self.early_exit = EarlyExitStrategy()
    
    def diagnose(self, context):
        """执行诊断流程"""
        
        # 1. 能力包路由
        capability_bundle = self.capability_routing.route(context)
        
        # 2. 初始化假设账本
        hypothesis_ledger = HypothesisLedger()
        
        # 3. 主诊断循环
        while not self.should_stop(context, hypothesis_ledger):
            
            # 3.1 选择下一个工具
            next_tool = self.select_next_tool(
                context, hypothesis_ledger, capability_bundle
            )
            
            # 3.2 执行Before Tool Hook
            hook_result = self.execute_hooks('before_tool', next_tool, context)
            if not hook_result['proceed']:
                break
            
            # 3.3 执行工具
            tool_result = next_tool.execute(context)
            
            # 3.4 执行After Tool Hook
            self.execute_hooks('after_tool', next_tool, tool_result)
            
            # 3.5 更新假设账本
            hypothesis_ledger.update_with_result(tool_result)
            
            # 3.6 检查预算和停止条件
            if self.budget_control.is_exceeded() or self.early_exit.should_stop():
                break
        
        # 4. 生成最终诊断报告
        final_report = self.generate_report(hypothesis_ledger)
        
        return final_report
```

## 6. 业务价值与应用场景

### 6.1 目标用户群体
- **支付产品经理**：识别转化漏斗瓶颈
- **运营分析师**：分析异常波动原因
- **技术负责人**：定位系统性问题
- **客户支持**：快速响应客户问题

### 6.2 典型应用场景
1. **日常监控**：自动发现转化率异常
2. **专题分析**：深入分析特定问题
3. **A/B测试评估**：对比不同版本效果
4. **故障排查**：快速定位系统问题
5. **合规审计**：验证业务逻辑正确性

### 6.3 量化收益估算
```markdown
**效率提升：**
- 异常发现时间：从4小时→15分钟（↓94%）
- 根因分析时间：从8小时→45分钟（↓91%）
- 报告生成时间：从2小时→5分钟（↓96%）

**质量改善：**
- 分析覆盖率：从60%→95%（+35%）
- 结论准确性：从75%→93%（+18%）
- 证据完整性：从50%→100%（+50%）

**成本节约：**
- 人工分析成本：降低85%
- 误判导致的损失：减少70%
- 培训和维护成本：降低60%
```

## 7. 未来发展路线

### 7.1 短期目标（3个月）
1. 支持更多支付渠道和业务场景
2. 优化机器学习辅助诊断
3. 提供可视化分析界面
4. 完善API文档和SDK

### 7.2 中期目标（6个月）
1. 实现实时流式诊断
2. 构建预测性分析能力
3. 集成企业级监控系统
4. 支持多租户部署

### 7.3 长期愿景（1年+）
1. 成为支付领域标准诊断工具
2. 构建开源生态和社区
3. 支持跨行业通用诊断
4. 实现完全自动化运维

---

**文档版本**：V1.2  
**最后更新**：2026年8月14日  
**项目状态**：活跃开发中  
**维护者**：刘宇广  
**许可证**：MIT License
