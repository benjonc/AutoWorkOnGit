# 使用案例示例

本文档展示如何使用自动化工作流系统完成实际项目。

## 🎯 案例1: 构建RESTful API

### 需求描述

```
创建一个博客API，包括:
1. 用户注册和登录
2. 文章的CRUD操作
3. 评论功能
4. 分页和搜索

技术栈: FastAPI + SQLAlchemy + PostgreSQL
```

### 执行流程

#### Phase 1: 需求收集

```bash
$ poetry run python -m python_project

🤖 欢迎使用自动化工作流系统!

请描述你的项目需求:
> 创建一个博客API...

系统会询问:
- 需要用户认证吗? → 是的，使用JWT
- 需要权限控制吗? → 是的，只有作者能编辑自己的文章
- 需要API文档吗? → 是的，使用OpenAPI

✅ 需求文档已生成: docs/requirements/requirements.md
```

#### Phase 2: 任务分析

```
📊 分析需求并拆分任务...

任务依赖图:
  Phase 1: [数据库设计]
  Phase 2: [用户认证] [文章CRUD] [评论功能]
  Phase 3: [集成测试]

✅ 生成12个任务:
  TASK-001: 设计数据库模型
  TASK-002: 实现用户注册API
  TASK-003: 实现用户登录API
  TASK-004: 实现文章创建API
  TASK-005: 实现文章查询API
  TASK-006: 实现文章更新API
  TASK-007: 实现文章删除API
  TASK-008: 实现评论创建API
  TASK-009: 实现评论查询API
  TASK-010: 实现评论删除API
  TASK-011: 实现分页和搜索
  TASK-012: 编写集成测试
```

#### Phase 3: 并行执行

```
🚀 启动并行执行 (最多5个Agent)

Phase 1:
  [Agent-001] TASK-001: 设计数据库模型
    → 创建分支: agent/code/001_db-models
    → 实现: src/models/user.py, src/models/post.py
    → 创建PR #10
    ✅ 审核通过，已合并

Phase 2 (并行启动3个Agent):
  [Agent-002] TASK-002: 实现用户注册API
    → 创建分支: agent/code/002_user-register
    → 实现: src/api/auth.py
    → 创建PR #11

  [Agent-003] TASK-003: 实现用户登录API
    → 创建分支: agent/code/003_user-login
    → 实现: src/api/auth.py (无冲突)
    → 创建PR #12

  [Agent-004] TASK-004: 实现文章创建API
    → 创建分支: agent/code/004_post-create
    → 实现: src/api/posts.py
    → 创建PR #13

  审核中...
  ✅ PR #11 审核通过
  ✅ PR #12 审核通过
  ⚠️ PR #13 需要修改: 缺少权限检查

  [Agent-005] 创建修复Issue #013: 添加权限检查
    → 修复PR #13
    → 重新审核
    ✅ 通过，已合并
```

#### Phase 4: 最终结果

```
📈 工作流完成!

统计:
  ✅ 任务完成: 12/12
  📝 PR创建: 14个 (包含2个修复PR)
  🔀 代码合并: 成功
  📝 Issues关闭: 12个

生成的文件:
  src/
  ├── models/
  │   ├── user.py
  │   ├── post.py
  │   └── comment.py
  ├── api/
  │   ├── auth.py
  │   ├── posts.py
  │   └── comments.py
  └── tests/
      ├── test_auth.py
      ├── test_posts.py
      └── test_comments.py

API端点:
  POST   /api/auth/register
  POST   /api/auth/login
  GET    /api/posts
  POST   /api/posts
  PUT    /api/posts/{id}
  DELETE /api/posts/{id}
  POST   /api/posts/{id}/comments
  GET    /api/posts/{id}/comments

文档:
  - docs/requirements/requirements.md
  - docs/api/openapi.yaml
  - README.md (已更新)
```

### 运行时间

```
总耗时: 2小时15分钟

分解:
  需求收集: 10分钟
  任务分析: 5分钟
  执行阶段: 1小时50分钟
  审核合并: 10分钟
```

## 🎯 案例2: 微服务拆分

### 需求描述

```
将单体电商应用拆分为:
1. 用户服务 (User Service)
2. 订单服务 (Order Service)
3. 商品服务 (Product Service)
4. 通知服务 (Notification Service)

保持数据一致性，逐步迁移
```

### 执行策略

#### 阶段性拆分

```
Phase 1: 准备工作
  TASK-001: 绘制服务边界图
  TASK-002: 设计API契约
  TASK-003: 配置服务发现

Phase 2: 数据库拆分
  TASK-004: 用户数据库迁移
  TASK-005: 订单数据库迁移
  TASK-006: 商品数据库迁移

Phase 3: 服务实现
  TASK-007: 实现用户服务
  TASK-008: 实现订单服务
  TASK-009: 实现商品服务
  TASK-010: 实现通知服务

Phase 4: 集成和测试
  TASK-011: 服务间通信
  TASK-012: 端到端测试
```

### 依赖管理

```python
# 依赖图
dependencies = {
    "TASK-007": ["TASK-001", "TASK-004"],  # 用户服务依赖边界设计和数据库
    "TASK-008": ["TASK-001", "TASK-005"],  # 订单服务依赖边界设计和数据库
    "TASK-011": ["TASK-007", "TASK-008", "TASK-009"],  # 集成依赖所有服务
}

# 执行计划
[
  ["TASK-001", "TASK-002", "TASK-003"],  # Phase 1: 并行3个任务
  ["TASK-004", "TASK-005", "TASK-006"],  # Phase 2: 并行3个任务
  ["TASK-007", "TASK-008", "TASK-009", "TASK-010"],  # Phase 3: 并行4个任务
  ["TASK-011", "TASK-012"],  # Phase 4: 并行2个任务
]
```

### 冲突处理

```
检测到潜在冲突:
  - src/models/order.py 被 TASK-005 和 TASK-008 同时修改

解决方案:
  1. TASK-005 创建基础模型
  2. TASK-008 建立依赖，等待TASK-005完成
  3. TASK-008 在TASK-005的基础上扩展
```

## 🎯 案例3: 遗留代码重构

### 需求描述

```
重构老旧Python项目:
1. 从Python 3.7升级到3.11
2. 从Flask迁移到FastAPI
3. 添加类型注解
4. 提高测试覆盖率到80%
```

### 智能重构策略

#### Step 1: 代码分析

```python
# 系统自动分析代码库
analysis = {
    "total_files": 150,
    "lines_of_code": 25000,
    "test_coverage": "35%",
    "type_hints": "12%",
    "deprecated_apis": ["flask.ext.*", "six"],
}
```

#### Step 2: 分组重构

```
分组策略:
  Group A: 核心业务逻辑 (高优先级)
  Group B: API端点 (中优先级)
  Group C: 工具函数 (低优先级)

每个文件的重构任务:
  1. 添加类型注解
  2. 更新依赖导入
  3. 迁移到FastAPI
  4. 添加单元测试
```

#### Step 3: 渐进式迁移

```
Week 1: 核心模块 (10个文件)
  [Agent-001~005] 并行重构
  ✅ 覆盖率: 35% → 50%

Week 2: API层 (30个文件)
  [Agent-001~010] 并行重构
  ✅ 覆盖率: 50% → 70%

Week 3: 剩余模块 (110个文件)
  [Agent-001~015] 并行重构
  ✅ 覆盖率: 70% → 82%
```

### 质量保证

```
每个重构任务包含:
  ✅ 类型检查 (mypy)
  ✅ 代码格式化 (black)
  ✅ Linter检查 (ruff)
  ✅ 单元测试 (pytest)
  ✅ 文档更新

自动验证:
  - 所有测试通过
  - 类型检查无错误
  - 覆盖率达标
```

## 🎯 案例4: 文档生成

### 需求描述

```
为现有项目生成完整文档:
1. API文档 (OpenAPI)
2. 架构文档
3. 用户指南
4. 开发者文档
```

### 执行流程

```
Phase 1: 代码分析
  TASK-001: 分析API端点
  TASK-002: 分析数据模型
  TASK-003: 分析架构模式

Phase 2: 文档生成 (并行)
  TASK-004: 生成API文档
  TASK-005: 生成架构图
  TASK-006: 生成用户指南
  TASK-007: 生成开发指南

Phase 3: 集成和审核
  TASK-008: 整合文档
  TASK-009: 审核一致性
```

### 生成示例

```markdown
# API文档自动生成示例

## POST /api/users

创建新用户

### 请求

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

### 响应

```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "created_at": "datetime"
}
```

### 错误码

- 400: 请求参数无效
- 409: 用户名已存在
```

## 🎯 案例5: CI/CD流水线设置

### 需求描述

```
设置完整的CI/CD流水线:
1. 代码检查 (Lint + Format)
2. 单元测试
3. 集成测试
4. 自动部署

平台: GitHub Actions
```

### 生成的流水线

```yaml
# .github/workflows/ci.yml (自动生成)

name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Ruff
        run: poetry run ruff check .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: poetry run pytest --cov

  deploy:
    needs: [lint, test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

## 📊 性能统计

### 平均执行时间

| 项目规模 | 任务数 | 并行Agent | 总耗时 |
|---------|-------|----------|--------|
| 小型 (<50 files) | 5-10 | 3 | 30分钟 |
| 中型 (50-200 files) | 10-30 | 5 | 2小时 |
| 大型 (>200 files) | 30-100 | 10 | 1天 |

### 资源消耗

```
API调用:
  - GitHub API: ~5次/任务
  - Claude API: ~10次/任务

计算资源:
  - CPU: 平均30% (峰值80%)
  - 内存: 平均500MB (峰值2GB)
  - 磁盘: ~100MB临时文件
```

## 🎓 最佳实践

### 1. 清晰的需求描述

```
✅ 好的需求:
"创建用户认证API，支持邮箱+密码注册，使用JWT token，
包含密码加密(bcrypt)，需要单元测试"

❌ 模糊的需求:
"做个登录功能"
```

### 2. 合理的并行度

```
小型项目: max_parallel_agents = 3
中型项目: max_parallel_agents = 5
大型项目: max_parallel_agents = 10

注意: 过高的并行度会导致:
  - 分支冲突增加
  - 资源竞争
  - API限流
```

### 3. 阶段性验证

```
每完成一个阶段，进行人工验证:
  ✓ 代码符合预期
  ✓ 测试全部通过
  ✓ 文档已更新

如果发现问题，及时调整后续任务
```

### 4. 保留人工审核点

```
关键决策需要人工确认:
  - 架构设计
  - 数据库schema变更
  - 安全相关代码
  - 性能优化方案
```

---

**提示**: 这些案例都可以在 `examples/` 目录找到完整的代码和运行日志
