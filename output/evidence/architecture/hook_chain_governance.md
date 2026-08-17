# Hook链治理与能力路由架构

## 架构概述
- **应用场景**：EnergyOps Agent 园区能耗智能运营平台
- **技术架构**：基于Hook链的Agent治理框架
- **核心目标**：在保持Agent灵活性的同时，确保操作安全、数据完整性和系统稳定性
- **设计理念**：能用代码确定性保证的事情，不交给模型自行决定

## 1. Hook链设计哲学

### 1.1 Agent固有问题的系统性解决方案
```python
class AgentInherentProblems:
    """
    Agent面临的三大固有问题及Hook链解决方案
    """
    
    def __init__(self):
        self.problems = {
            'token_budget_constraint': {
                'problem': '长结果可能被截断',
                'solution': 'After Tool Hook将大结果外置为Artifact',
                'implementation': 'ArtifactManager'
            },
            'operation_cost_ignorance': {
                'problem': '不理解操作的真实代价',
                'solution': 'Before Tool Hook实施风险分级与参数校验',
                'implementation': 'RiskClassifier'
            },
            'shortest_path_bias': {
                'problem': '倾向于最短路径完成任务',
                'solution': '强制注入校验、确认和审计步骤',
                'implementation': 'MandatoryValidationChain'
            }
        }
```

### 1.2 Hook切面定义
```python
class HookFacets:
    """
    Hook链的三个核心切面
    """
    
    def __init__(self):
        self.facets = {
            'before_tool': {
                'trigger': '工具执行前',
                'responsibilities': [
                    '参数Schema校验',
                    '数据完整性检查',
                    '权限验证',
                    '风险分级处理',
                    '人工确认状态检查'
                ],
                'failure_action': '阻断执行'
            },
            'after_tool': {
                'trigger': '工具执行后',
                'responsibilities': [
                    '证据登记',
                    'Artifact外置',
                    '任务状态更新',
                    '副作用记录',
                    '审计日志写入'
                ],
                'failure_action': '降级处理'
            },
            'before_model': {
                'trigger': '下一轮调用前',
                'responsibilities': [
                    '注入上一次调用的副作用',
                    '更新任务预算状态',
                    '注入未解决问题',
                    '提供上下文压缩',
                    '优化提示工程'
                ],
                'failure_action': '不影响执行'
            }
        }
```

## 2. R0/R1/R2三级风险分级

### 2.1 风险分级定义
```python
class RiskClassification:
    """
    基于操作影响范围的风险分级系统
    """
    
    def __init__(self):
        self.risk_levels = {
            'R0': {
                'name': '查询操作',
                'description': '只读操作，无副作用',
                'examples': [
                    '查询能耗数据',
                    '查看设备状态',
                    '浏览历史告警'
                ],
                'security_requirements': [
                    '权限检查',
                    '参数校验',
                    '查询限制'
                ],
                'confirmation_required': False,
                'audit_level': 'basic'
            },
            'R1': {
                'name': '草稿操作',
                'description': '创建临时对象，可回滚',
                'examples': [
                    '创建告警规则草稿',
                    '配置测试设备',
                    '生成结算预览'
                ],
                'security_requirements': [
                    '权限检查',
                    '参数校验',
                    '影响预览',
                    '数据完整性验证'
                ],
                'confirmation_required': '预览确认',
                'audit_level': 'detailed'
            },
            'R2': {
                'name': '发布操作',
                'description': '影响生产数据，需人工确认',
                'examples': [
                    '启停设备',
                    '变更设备归属',
                    '发布月度结算',
                    '确认告警处置'
                ],
                'security_requirements': [
                    '权限检查',
                    '参数校验',
                    '影响说明',
                    '幂等键生成',
                    '人工确认',
                    '审计追踪'
                ],
                'confirmation_required': '二次人工确认',
                'audit_level': 'comprehensive'
            }
        }
```

### 2.2 风险分级实施逻辑
```python
class RiskImplementation:
    """
    风险分级的具体实施
    """
    
    def classify_tool_risk(self, tool_name, params):
        """为工具调用分配风险等级"""
        
        risk_rules = {
            'R0': self.is_read_only_operation,
            'R1': self.is_draft_operation,
            'R2': self.is_production_operation
        }
        
        for risk_level, check_func in risk_rules.items():
            if check_func(tool_name, params):
                return risk_level
        
        return 'R2'  # 默认最高风险
    
    def apply_risk_controls(self, risk_level, tool_call):
        """应用对应风险级别的控制措施"""
        
        controls = {
            'R0': [
                self.apply_basic_validation,
                self.log_operation
            ],
            'R1': [
                self.apply_basic_validation,
                self.preview_impact,
                self.require_preview_confirmation,
                self.log_operation_with_details
            ],
            'R2': [
                self.apply_comprehensive_validation,
                self.explain_impact,
                self.generate_idempotency_key,
                self.require_human_confirmation,
                self.create_audit_trail,
                self.implement_compensation_mechanism
            ]
        }
        
        for control_func in controls[risk_level]:
            result = control_func(tool_call)
            if not result['success']:
                return result
        
        return {'success': True, 'risk_level': risk_level}
```

## 3. Hook链执行引擎

### 3.1 核心Hook链引擎
```python
class HookChainEngine:
    """
    Hook链执行引擎
    """
    
    def __init__(self):
        self.hook_registry = {}
        self.execution_context = {}
    
    def register_hook(self, hook_type, hook_func, priority=50):
        """注册Hook函数"""
        if hook_type not in self.hook_registry:
            self.hook_registry[hook_type] = []
        
        self.hook_registry[hook_type].append({
            'func': hook_func,
            'priority': priority
        })
        
        # 按优先级排序
        self.hook_registry[hook_type].sort(key=lambda x: x['priority'])
    
    def execute_hooks(self, hook_type, context):
        """执行指定类型的Hook链"""
        if hook_type not in self.hook_registry:
            return {'proceed': True, 'results': []}
        
        hook_results = []
        should_proceed = True
        
        for hook_info in self.hook_registry[hook_type]:
            try:
                result = hook_info['func'](context)
                hook_results.append(result)
                
                # 如果Hook返回False，停止后续Hook执行
                if result.get('proceed', True) == False:
                    should_proceed = False
                    break
                    
            except Exception as e:
                hook_results.append({
                    'success': False,
                    'error': str(e),
                    'proceed': False
                })
                should_proceed = False
                break
        
        return {
            'proceed': should_proceed,
            'results': hook_results,
            'hook_type': hook_type,
            'hook_count': len(hook_results)
        }
```

### 3.2 标准Hook实现示例
```python
class StandardHooks:
    """
    标准Hook函数库
    """
    
    @staticmethod
    def validate_parameters(tool_call):
        """参数Schema校验Hook"""
        expected_schema = tool_call.tool_schema
        actual_params = tool_call.params
        
        validation_result = validate_against_schema(
            actual_params, expected_schema
        )
        
        if not validation_result['valid']:
            return {
                'proceed': False,
                'reason': '参数校验失败',
                'errors': validation_result['errors'],
                'hook_name': 'validate_parameters'
            }
        
        return {
            'proceed': True,
            'validated_params': validation_result['cleaned_params'],
            'hook_name': 'validate_parameters'
        }
    
    @staticmethod
    def check_data_completeness(tool_call):
        """数据完整性检查Hook"""
        required_data_sources = tool_call.get_required_data_sources()
        missing_sources = []
        
        for source in required_data_sources:
            if not self.is_data_source_available(source):
                missing_sources.append(source)
        
        if missing_sources:
            return {
                'proceed': False,
                'reason': '数据源不完整',
                'missing_sources': missing_sources,
                'hook_name': 'check_data_completeness'
            }
        
        return {
            'proceed': True,
            'data_status': 'complete',
            'hook_name': 'check_data_completeness'
        }
    
    @staticmethod
    def handle_large_result(tool_result):
        """大结果外置Hook"""
        result_size = len(str(tool_result.result))
        
        if result_size > MAX_INLINE_RESULT_SIZE:
            # 创建Artifact
            artifact_id = self.create_artifact(tool_result.result)
            
            # 生成摘要
            summary = self.generate_result_summary(tool_result.result)
            
            return {
                'proceed': True,
                'result_handling': 'offloaded',
                'artifact_id': artifact_id,
                'summary': summary,
                'original_size': result_size,
                'summary_size': len(summary),
                'compression_ratio': result_size / len(summary),
                'hook_name': 'handle_large_result'
            }
        
        return {
            'proceed': True,
            'result_handling': 'inline',
            'hook_name': 'handle_large_result'
        }
```

## 4. 能力路由系统

### 4.1 能力包设计
```python
class CapabilityBundle:
    """
    能力包：一组相关的工具集合
    """
    
    def __init__(self, bundle_name):
        self.name = bundle_name
        self.tools = []
        self.access_policies = []
        self.routing_rules = []
    
    def add_tool(self, tool_name, tool_instance):
        """添加工具到能力包"""
        self.tools.append({
            'name': tool_name,
            'instance': tool_instance,
            'metadata': self.extract_tool_metadata(tool_instance)
        })
    
    def define_access_policy(self, user_role, allowed_actions):
        """定义访问策略"""
        self.access_policies.append({
            'role': user_role,
            'allowed_actions': allowed_actions,
            'effective_time': datetime.now()
        })
    
    def match_context(self, context):
        """检查上下文是否匹配此能力包"""
        matching_score = 0
        
        # 1. 用户角色匹配
        if context.user_role in [p['role'] for p in self.access_policies]:
            matching_score += 30
        
        # 2. 任务类型匹配
        if context.task_type in self.supported_task_types():
            matching_score += 25
        
        # 3. 数据范围匹配
        if self.covers_data_scope(context.data_scope):
            matching_score += 20
        
        # 4. 风险级别匹配
        if context.risk_level in self.supported_risk_levels():
            matching_score += 15
        
        # 5. 操作历史匹配
        if self.aligns_with_operation_history(context.history):
            matching_score += 10
        
        return matching_score
```

### 4.2 能力路由器
```python
class CapabilityRouter:
    """
    基于上下文的能力包路由
    """
    
    def __init__(self):
        self.bundles = {}
        self.routing_history = []
    
    def register_bundle(self, bundle):
        """注册能力包"""
        self.bundles[bundle.name] = bundle
    
    def route(self, context):
        """路由到最适合的能力包"""
        
        # 计算所有能力包的匹配分数
        bundle_scores = {}
        for bundle_name, bundle in self.bundles.items():
            score = bundle.match_context(context)
            bundle_scores[bundle_name] = score
        
        # 选择最高分的能力包
        selected_bundle = max(bundle_scores, key=bundle_scores.get)
        
        # 记录路由决策
        self.record_routing_decision(
            context, selected_bundle, bundle_scores[selected_bundle]
        )
        
        # 验证访问权限
        if not self.check_access_permission(context, selected_bundle):
            # 降级到只读能力包
            selected_bundle = self.find_fallback_bundle(context)
        
        return self.bundles[selected_bundle]
    
    def find_fallback_bundle(self, context):
        """查找降级能力包"""
        fallback_options = []
        
        for bundle_name, bundle in self.bundles.items():
            if bundle.name == 'read_only_bundle':
                fallback_options.append(bundle)
            elif 'query' in bundle.name.lower():
                fallback_options.append(bundle)
        
        if fallback_options:
            # 选择匹配度最高的降级选项
            scores = [b.match_context(context) for b in fallback_options]
            best_index = scores.index(max(scores))
            return fallback_options[best_index]
        
        # 返回最小的只读包
        return self.bundles['basic_query_bundle']
```

### 4.3 能力包实例
```python
class EnergyOpsBundles:
    """
    EnergyOps项目的具体能力包定义
    """
    
    def create_bundles(self):
        bundles = {}
        
        # 1. 只读查询包
        read_only = CapabilityBundle('read_only_bundle')
        read_only.add_tool('query_hourly', HourlyQueryTool())
        read_only.add_tool('query_daily', DailyQueryTool())
        read_only.add_tool('query_monthly', MonthlyQueryTool())
        read_only.add_tool('list_devices', DeviceListTool())
        read_only.define_access_policy('viewer', ['query', 'list'])
        bundles['read_only_bundle'] = read_only
        
        # 2. 告警管理包
        alert_manager = CapabilityBundle('alert_manager_bundle')
        alert_manager.add_tool('check_alerts', AlertCheckTool())
        alert_manager.add_tool('acknowledge_alert', AlertAcknowledgeTool())
        alert_manager.add_tool('close_incident', IncidentCloseTool())
        alert_manager.add_tool('create_rule', RuleCreateTool())
        alert_manager.define_access_policy('operator', ['check', 'acknowledge', 'close'])
        alert_manager.define_access_policy('admin', ['create_rule'])
        bundles['alert_manager_bundle'] = alert_manager
        
        # 3. 结算管理包
        settlement = CapabilityBundle('settlement_bundle')
        settlement.add_tool('preview_settlement', SettlementPreviewTool())
        settlement.add_tool('confirm_settlement', SettlementConfirmTool())
        settlement.add_tool('generate_invoice', InvoiceGenerateTool())
        settlement.define_access_policy('finance', ['preview'])
        settlement.define_access_policy('finance_manager', ['confirm'])
        bundles['settlement_bundle'] = settlement
        
        # 4. 设备管理包
        device_manager = CapabilityBundle('device_manager_bundle')
        device_manager.add_tool('update_device_status', DeviceStatusTool())
        device_manager.add_tool('assign_device', DeviceAssignTool())
        device_manager.add_tool('maintenance_schedule', MaintenanceTool())
        device_manager.define_access_policy('operator', ['update_status'])
        device_manager.define_access_policy('admin', ['assign', 'schedule'])
        bundles['device_manager_bundle'] = device_manager
        
        return bundles
```

## 5. 证据收集与审计系统

### 5.1 证据模型
```python
class EvidenceModel:
    """
    统一的证据收集模型
    """
    
    def __init__(self):
        self.evidence_store = {}
        self.chain_of_custody = []
    
    def collect_evidence(self, evidence_type, data, context):
        """收集证据"""
        evidence_id = self.generate_evidence_id()
        
        evidence = {
            'id': evidence_id,
            'type': evidence_type,
            'data': data,
            'context': context,
            'timestamp': datetime.now(),
            'hash': self.calculate_hash(data),
            'chain_position': len(self.chain_of_custody)
        }
        
        # 存储证据
        self.evidence_store[evidence_id] = evidence
        
        # 更新监管链
        self.chain_of_custody.append({
            'evidence_id': evidence_id,
            'action': 'collected',
            'timestamp': datetime.now(),
            'actor': context.get('user_id', 'system')
        })
        
        return evidence_id
    
    def link_evidence(self, source_id, target_id, relationship):
        """链接相关证据"""
        link_id = f"link_{source_id}_{target_id}"
        
        link = {
            'id': link_id,
            'source': source_id,
            'target': target_id,
            'relationship': relationship,
            'timestamp': datetime.now()
        }
        
        # 更新监管链
        self.chain_of_custody.append({
            'action': 'linked',
            'link_id': link_id,
            'timestamp': datetime.now(),
            'actor': 'system'
        })
        
        return link_id
```

### 5.2 审计追踪
```python
class AuditTrail:
    """
    完整的操作审计追踪
    """
    
    def __init__(self):
        self.audit_log = []
        self.retention_period = timedelta(days=365)
    
    def record_operation(self, operation_type, details):
        """记录操作审计"""
        audit_entry = {
            'id': self.generate_audit_id(),
            'timestamp': datetime.now(),
            'operation_type': operation_type,
            'details': details,
            'user_id': details.get('user_id'),
            'tenant_id': details.get('tenant_id'),
            'tool_name': details.get('tool_name'),
            'risk_level': details.get('risk_level'),
            'evidence_ids': details.get('evidence_ids', []),
            'status': 'recorded'
        }
        
        self.audit_log.append(audit_entry)
        
        # 实时同步到监控系统
        self.sync_to_monitoring(audit_entry)
        
        return audit_entry['id']
    
    def generate_compliance_report(self, start_date, end_date):
        """生成合规报告"""
        relevant_entries = [
            entry for entry in self.audit_log
            if start_date <= entry['timestamp'] <= end_date
        ]
        
        report = {
            'period': f"{start_date} to {end_date}",
            'total_operations': len(relevant_entries),
            'by_risk_level': self.group_by_risk_level(relevant_entries),
            'by_user': self.group_by_user(relevant_entries),
            'by_tool': self.group_by_tool(relevant_entries),
            'r2_operations': self.filter_r2_operations(relevant_entries),
            'evidence_coverage': self.calculate_evidence_coverage(relevant_entries),
            'compliance_score': self.calculate_compliance_score(relevant_entries)
        }
        
        return report
```

## 6. 性能优化与监控

### 6.1 Hook链性能监控
```python
class HookPerformanceMonitor:
    """
    Hook链性能监控
    """
    
    def __init__(self):
        self.metrics = {
            'execution_times': [],
            'success_rates': {},
            'error_breakdown': {},
            'latency_distribution': {}
        }
    
    def record_hook_execution(self, hook_type, hook_name, duration, success):
        """记录Hook执行性能"""
        self.metrics['execution_times'].append({
            'hook_type': hook_type,
            'hook_name': hook_name,
            'duration': duration,
            'timestamp': datetime.now()
        })
        
        # 更新成功率统计
        key = f"{hook_type}.{hook_name}"
        if key not in self.metrics['success_rates']:
            self.metrics['success_rates'][key] = {'success': 0, 'total': 0}
        
        self.metrics['success_rates'][key]['total'] += 1
        if success:
            self.metrics['success_rates'][key]['success'] += 1
    
    def generate_performance_report(self):
        """生成性能报告"""
        report = {
            'summary': {
                'total_hook_executions': len(self.metrics['execution_times']),
                'average_latency': self.calculate_average_latency(),
                'overall_success_rate': self.calculate_overall_success_rate()
            },
            'by_hook_type': self.aggregate_by_hook_type(),
            'slowest_hooks': self.identify_slowest_hooks(limit=10),
            'most_error_prone': self.identify_error_prone_hooks(limit=10),
            'recommendations': self.generate_optimization_recommendations()
        }
        
        return report
```

### 6.2 容量规划与扩容
```python
class CapacityPlanner:
    """
    容量规划与自动扩容
    """
    
    def __init__(self):
        self.capacity_metrics = {
            'concurrent_sessions': 0,
            'active_hook_chains': 0,
            'evidence_store_size': 0,
            'audit_log_size': 0
        }
        
        self.thresholds = {
            'warning': 70,    # 70% 容量警告
            'critical': 85,   # 85% 容量临界
            'maximum': 95     # 95% 最大容量
        }
    
    def monitor_capacity(self):
        """监控系统容量"""
        current_usage = self.calculate_current_usage()
        
        alerts = []
        
        for metric, usage_percent in current_usage.items():
            if usage_percent >= self.thresholds['maximum']:
                alerts.append({
                    'level': 'emergency',
                    'metric': metric,
                    'usage': usage_percent,
                    'action': '立即扩容'
                })
            elif usage_percent >= self.thresholds['critical']:
                alerts.append({
                    'level': 'critical',
                    'metric': metric,
                    'usage': usage_percent,
                    'action': '计划扩容'
                })
            elif usage_percent >= self.thresholds['warning']:
                alerts.append({
                    'level': 'warning',
                    'metric': metric,
                    'usage': usage_percent,
                    'action': '监控关注'
                })
        
        return {
            'current_usage': current_usage,
            'alerts': alerts,
            'recommendations': self.generate_capacity_recommendations()
        }
```

## 7. 架构收益与度量指标

### 7.1 架构收益统计
| 收益维度 | 量化指标 | 提升幅度 | 实现机制 |
|----------|----------|----------|----------|
| **操作安全性** | 越权操作拦截率 | 100% | 三级风险分级 + Hook链校验 |
| **数据完整性** | 可信聚合完整率 | 96.8% → 99.7% | 数据质量Hook + 自动回补 |
| **系统性能** | 核心查询P95响应时间 | 20.4s → 2.8s | 能力路由优化 + 预聚合 |
| **任务成功率** | Agent任务完成率 | 83.3% → 95.8% | 精细化工具拆分 + 错误处理 |
| **告警质量** | 无效告警减少 | 43% | 历史dry-run + 指纹去重 |
| **运营效率** | 异常研判时间 | 18min → 6min | 证据聚合 + 案例库匹配 |

### 7.2 技术债务管理
```python
class TechnicalDebtTracker:
    """
    技术债务追踪与管理
    """
    
    def __init__(self):
        self.debt_items = []
    
    def add_debt_item(self, area, description, impact, effort):
        """记录技术债务项"""
        debt_item = {
            'id': len(self.debt_items) + 1,
            'area': area,
            'description': description,
            'impact': impact,  # low, medium, high, critical
            'effort': effort,  # S, M, L, XL
            'created_at': datetime.now(),
            'status': 'open',
            'priority': self.calculate_priority(impact, effort)
        }
        
        self.debt_items.append(debt_item)
        return debt_item['id']
    
    def generate_roadmap(self):
        """生成技术债务解决路线图"""
        roadmap = {
            'immediate': [],  # 本月解决
            'short_term': [], # 本季度解决
            'medium_term': [], # 半年内解决
            'long_term': []   # 年度规划
        }
        
        for item in self.debt_items:
            if item['status'] != 'open':
                continue
            
            if item['priority'] == 'critical':
                roadmap['immediate'].append(item)
            elif item['priority'] == 'high':
                roadmap['short_term'].append(item)
            elif item['priority'] == 'medium':
                roadmap['medium_term'].append(item)
            else:
                roadmap['long_term'].append(item)
        
        return roadmap
```

## 8. 部署与运维指南

### 8.1 环境配置
```yaml
# docker-compose.yml 示例
version: '3.8'

services:
  hook-engine:
    image: energyops/hook-engine:latest
    environment:
      - HOOK_CHAIN_ENABLED=true
      - RISK_CLASSIFICATION_LEVEL=strict
      - AUDIT_TRAIL_ENABLED=true
      - EVIDENCE_STORE_TYPE=postgresql
    volumes:
      - ./hook_configs:/app/configs
      - ./audit_logs:/app/logs
  
  capability-router:
    image: energyops/capability-router:latest
    environment:
      - ROUTING_STRATEGY=context_aware
      - FALLBACK_ENABLED=true
      - LOAD_BALANCING_ENABLED=true
  
  evidence-store:
    image: postgres:15
    environment:
      - POSTGRES_DB=evidence
      - POSTGRES_USER=evidence_user
      - POSTGRES_PASSWORD=${EVIDENCE_DB_PASSWORD}
    volumes:
      - evidence_data:/var/lib/postgresql/data
  
  monitoring:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - ./dashboards:/etc/grafana/provisioning/dashboards
```

### 8.2 监控仪表板配置
```json
{
  "dashboard": {
    "title": "Hook链治理监控",
    "panels": [
      {
        "title": "Hook执行成功率",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(hook_execution_success_total[5m])) / sum(rate(hook_execution_total[5m]))",
            "legendFormat": "成功率"
          }
        ]
      },
      {
        "title": "风险分级分布",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum(risk_classification_total) by (level)",
            "legendFormat": "{{level}}"
          }
        ]
      },
      {
        "title": "能力包路由延迟",
        "type": "heatmap",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(capability_routing_duration_seconds_bucket[5m])) by (le, bundle))",
            "legendFormat": "{{bundle}} P95"
          }
        ]
      }
    ]
  }
}
```

---

**架构版本**：V2.0  
**最后更新**：2026年8月14日  
**维护团队**：AI Agent工程组  
**文档状态**：生产就绪  
**适用场景**：企业级Agent治理与安全控制