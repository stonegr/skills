---
name: config-management
description: 规范项目的配置管理，包括配置文件格式、优先级、命名规范、验证规则等。适用于创建新项目模板或优化现有项目的配置管理。
---

# Config Management

规范项目的配置管理，支持多格式配置文件、统一优先级、类型安全验证。

## 用途

适用场景：
- 创建新的项目模板时，需要标准化配置管理
- 优化现有项目的配置管理，统一配置格式
- 统一多个项目的配置文件格式和优先级
- 需要配置验证和类型安全的项目

## 触发方式

```
/config-management <action> [--lang=<lang>] [--framework=<framework>]
```

参数说明：
- `<action>`：必填，操作类型。支持：
  - `init`：初始化项目配置管理
  - `optimize`：优化现有配置管理
  - `validate`：验证配置管理
- `--lang=<lang>`：可选，项目语言。支持 `python / go / javascript / typescript`
- `--framework=<framework>`：可选，项目框架。如 `fastapi / gin / express / flask`

示例：
```
/config-management init --lang=python --framework=fastapi
/config-management optimize --lang=go --framework=gin
/config-management validate
```

## 配置管理规范

### 1. 配置文件格式

支持三种格式，必须同时提供：

| 格式 | 文件名 | 用途 |
|------|--------|------|
| 环境变量 | `.env` | 本地开发覆盖，不提交到git |
| YAML | `config.yaml` | 主配置文件，支持复杂结构 |
| JSON | `config.json` | 替代YAML，支持程序化生成 |

**示例文件**：
- `.env.example`：环境变量模板
- `config.example.yaml`：YAML配置模板
- `config.example.json`：JSON配置模板

### 2. 配置优先级（从高到低）

1. **系统环境变量**：最高优先级，用于生产环境覆盖
2. **`.env`文件**：本地开发覆盖，不提交到git
3. **配置文件**：`config.yaml` 或 `config.json`
4. **默认值**：代码中定义的默认值

**重要**：环境变量必须优先于.env文件，符合12-factor原则。

### 3. 配置项命名规范

| 场景 | 命名格式 | 示例 |
|------|----------|------|
| 环境变量 | 大写下划线，APP_前缀 | `APP_LOG_LEVEL`, `APP_SERVER_PORT` |
| YAML配置 | 小写下划线，嵌套用冒号 | `log.level`, `server.port` |
| JSON配置 | 小写下划线，嵌套用点 | `log.level`, `server.port` |
| 配置结构体 | 大驼峰 | `LogLevel`, `ServerPort` |

**环境变量映射**：
- 环境变量前缀：`APP_`（可配置）
- 嵌套映射：`.` → `_`，如 `log.level` → `APP_LOG_LEVEL`

### 4. 基础配置项（必须包含）

每个项目必须包含以下基础配置：

```yaml
# 应用基础配置
app:
  name: "项目名称"           # 项目名称
  env: "development"         # 环境：development/staging/production
  root_path: "."             # 项目根路径

# 服务器配置
server:
  host: "0.0.0.0"           # 监听地址
  port: 8000                 # 监听端口
  workers: 4                 # 工作进程数（Python/Node.js）

# 日志配置
log:
  level: "INFO"              # 日志等级：debug/info/warn/error
  format: "json"             # 日志格式：json/text
  file: "./logs/app.log"     # 日志文件路径（为空则输出到控制台）
  output: "both"             # 日志输出：file/console/both
  max_size: 100              # 单个日志文件最大MB
  max_backups: 7             # 最多保留旧文件数
  max_age: 30                # 最多保留天数
  compress: true             # 是否压缩
  time_format: "%Y-%m-%d %H:%M:%S"  # 时间格式
  encoding: "utf-8"          # 日志文件编码
```

### 5. 配置验证规则

**类型安全**：
- 使用类型系统进行验证（Pydantic/Viper/JSON Schema）
- 所有配置项必须有类型定义
- 复杂类型必须有验证器

**必填项验证**：
- 数据库连接配置
- Redis连接配置
- JWT密钥
- 服务端口

**范围验证**：
- 端口号：1-65535
- 日志等级：debug/info/warn/error
- 连接池大小：1-1000
- 日志文件大小：1-1000MB
- 日志备份数：1-100
- 日志保留天数：1-365

### 6. 配置文档要求

**README.md必须包含**：
- 配置项说明表格
- 环境变量映射说明
- 配置示例

**代码注释**：
- 每个配置项必须有注释
- 复杂配置项必须有示例值

## 工作流程

### Step 1: 分析项目需求

1. **确定项目类型**：
   - Python项目：使用pydantic-settings
   - Go项目：使用viper
   - Node.js项目：使用dotenv + convict

2. **确定配置需求**：
   - 基础配置（必须）
   - 数据库配置（如需要）
   - Redis配置（如需要）
   - JWT配置（如需要）
   - 日志配置（必须）

### Step 2: 生成配置结构

1. **创建配置文件**：
   - `.env`：环境变量文件
   - `config.yaml`：YAML配置文件
   - `config.json`：JSON配置文件

2. **创建示例文件**：
   - `.env.example`：环境变量模板
   - `config.example.yaml`：YAML配置模板
   - `config.example.json`：JSON配置模板

3. **定义配置项**：
   - 按基础配置项规范定义
   - 添加类型定义
   - 设置默认值

### Step 3: 实现配置加载

1. **配置加载逻辑**：
   - 实现多格式支持
   - 实现优先级处理
   - 实现环境变量映射

2. **配置验证**：
   - 添加类型验证
   - 添加必填项验证
   - 添加范围验证

3. **配置导出**：
   - 导出配置单例
   - 提供配置访问接口

### Step 4: 生成示例文件

1. **.env.example**：
   - 包含所有环境变量
   - 使用占位符（如`CHANGEME`）
   - 添加注释说明

2. **config.example.yaml**：
   - 包含所有配置项
   - 使用示例值
   - 添加注释说明

3. **config.example.json**：
   - 与YAML配置保持一致
   - 使用示例值

### Step 5: 验证配置

1. **测试配置加载**：
   - 测试默认值加载
   - 测试环境变量覆盖
   - 测试配置文件加载

2. **验证配置优先级**：
   - 测试环境变量优先级
   - 测试.env文件优先级
   - 测试配置文件优先级

3. **检查配置文档**：
   - 检查README.md配置说明
   - 检查代码注释

## 语言特定实现

### Python项目

**推荐库**：pydantic-settings

**配置结构**：
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 应用基础配置
    app_name: str = "My App"
    app_env: str = "development"
    root_path: str = "."
    
    # 服务器配置
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    log_output: str = "both"
    log_max_size: int = 100
    log_max_backups: int = 7
    log_max_age: int = 30
    log_compress: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

**配置加载**：
```python
settings = Settings()
```

### Go项目

**推荐库**：viper + godotenv

**配置结构**：
```go
type Config struct {
    App struct {
        Name     string `mapstructure:"name"`
        Env      string `mapstructure:"env"`
        RootPath string `mapstructure:"root_path"`
    } `mapstructure:"app"`
    
    Server struct {
        Host string `mapstructure:"host"`
        Port int    `mapstructure:"port"`
    } `mapstructure:"server"`
    
    Log struct {
        Level      string `mapstructure:"level"`
        File       string `mapstructure:"file"`
        Output     string `mapstructure:"output"`
        MaxSize    int    `mapstructure:"max_size"`
        MaxBackups int    `mapstructure:"max_backups"`
        MaxAge     int    `mapstructure:"max_age"`
        Compress   bool   `mapstructure:"compress"`
    } `mapstructure:"log"`
}
```

**配置加载**：
```go
func LoadConfig(path string) (*Config, error) {
    viper.SetConfigFile(path)
    if err := viper.ReadInConfig(); err != nil {
        return nil, err
    }
    
    var cfg Config
    if err := viper.Unmarshal(&cfg); err != nil {
        return nil, err
    }
    
    return &cfg, nil
}
```

### Node.js项目

**推荐库**：dotenv + convict

**配置结构**：
```javascript
const convict = require('convict');

const config = convict({
  app: {
    name: {
      doc: 'Application name',
      format: 'string',
      default: 'My App'
    },
    env: {
      doc: 'Application environment',
      format: ['development', 'staging', 'production'],
      default: 'development'
    }
  },
  server: {
    port: {
      doc: 'Server port',
      format: 'port',
      default: 8000,
      env: 'PORT'
    }
  },
  log: {
    level: {
      doc: 'Log level',
      format: ['debug', 'info', 'warn', 'error'],
      default: 'info'
    },
    file: {
      doc: 'Log file path',
      format: 'string',
      default: './logs/app.log'
    }
  }
});
```

**配置加载**：
```javascript
require('dotenv').config();
config.load();
```

## 验证清单

- [ ] 配置文件格式正确（.env, config.yaml, config.json）
- [ ] 示例文件完整（.env.example, config.example.yaml, config.example.json）
- [ ] 配置优先级正确（环境变量 > .env > 配置文件 > 默认值）
- [ ] 配置项命名规范（环境变量大写下划线+APP_前缀，配置文件小写下划线）
- [ ] 基础配置项完整（app, server, log）
- [ ] 配置验证通过（类型验证、必填项验证、范围验证）
- [ ] 配置文档完整（README.md、代码注释）
- [ ] .gitignore包含.env（不提交真实配置）

## 注意事项

1. **安全性**：
   - 真实配置文件（.env, config.yaml）必须在.gitignore中
   - 示例文件使用占位符（如`CHANGEME`）
   - 敏感信息（密码、密钥）必须有默认占位符

2. **可维护性**：
   - 配置项必须有注释
   - 复杂配置必须有示例
   - README必须有配置说明

3. **兼容性**：
   - 支持多格式配置文件
   - 支持环境变量覆盖
   - 支持默认值

4. **可测试性**：
   - 配置加载必须可测试
   - 配置验证必须可测试
   - 配置优先级必须可测试

## 配置管理最佳实践

### 1. 配置分离原则
- **开发环境**：使用.env文件，包含开发配置
- **测试环境**：使用环境变量，包含测试配置
- **生产环境**：使用环境变量，包含生产配置

### 2. 敏感信息管理
- 密码、密钥等敏感信息不得提交到git
- 使用环境变量或秘密管理工具（如Vault）
- 示例文件使用占位符（如`CHANGEME`）

### 3. 配置版本控制
- 配置文件（config.yaml, config.json）应提交到git
- .env文件不得提交到git
- 示例文件（.env.example）应提交到git

### 4. 配置热重载
- 开发环境支持配置热重载
- 生产环境配置变更需要重启服务
- 关键配置变更需要日志记录

### 5. 配置监控
- 记录配置加载过程
- 记录配置变更历史
- 监控配置异常

## 常见问题

### Q1: 为什么环境变量要优先于.env文件？
A: 符合12-factor原则，环境变量是不同环境之间配置差异的首选方式。.env文件主要用于本地开发覆盖。

### Q2: 如何处理不同环境的配置差异？
A: 使用环境变量覆盖配置文件中的值。例如，生产环境可以设置`APP_DATABASE_HOST=prod-db.example.com`来覆盖配置文件中的数据库主机。

### Q3: 配置文件格式选择哪个？
A: YAML更适合人类阅读，JSON更适合程序化生成。建议同时提供两种格式，让开发者选择。

### Q4: 如何验证配置的正确性？
A: 使用配置验证脚本（references/validate_config.py）验证配置文件格式和内容。同时，使用类型系统进行运行时验证。

## 工具脚本

### 配置验证脚本

使用`references/validate_config.py`验证配置文件：

```bash
# 验证目录中的示例文件
python references/validate_config.py .

# 验证单个配置文件
python references/validate_config.py config.yaml
```

脚本会检查：
- 配置文件格式（YAML/JSON）
- 必须的配置项
- 配置值范围
- 示例文件完整性

### 配置模板

`references/`目录包含配置模板：
- `python-fastapi-config.yaml`：Python FastAPI项目配置模板
- `go-gin-config.yaml`：Go Gin项目配置模板
- `nodejs-express-config.yaml`：Node.js Express项目配置模板
- `env.example`：环境变量模板