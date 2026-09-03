#!/usr/bin/env python3
"""
配置文件验证脚本
用于验证配置文件是否符合config-management规范
"""

import yaml
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConfigValidator:
    """配置文件验证器"""
    
    # 必须包含的基础配置项
    REQUIRED_SECTIONS = ['app', 'server', 'log']
    
    # 必须包含的配置项
    REQUIRED_CONFIGS = {
        'app': ['name', 'env', 'root_path'],
        'server': ['host', 'port'],
        'log': ['level', 'file']
    }
    
    # 配置项验证规则
    VALIDATION_RULES = {
        'app.env': ['development', 'staging', 'production'],
        'log.level': ['debug', 'info', 'warn', 'error'],
        'log.output': ['file', 'console', 'both'],
        'server.port': (1, 65535),
        'log.max_size': (1, 1000),
        'log.max_backups': (1, 100),
        'log.max_age': (1, 365)
    }
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_yaml(self, file_path: str) -> bool:
        """验证YAML配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not isinstance(config, dict):
                self.errors.append(f"配置文件格式错误: {file_path}")
                return False
            
            return self.validate_config(config, file_path)
            
        except yaml.YAMLError as e:
            self.errors.append(f"YAML解析错误: {e}")
            return False
        except Exception as e:
            self.errors.append(f"读取文件错误: {e}")
            return False
    
    def validate_json(self, file_path: str) -> bool:
        """验证JSON配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if not isinstance(config, dict):
                self.errors.append(f"配置文件格式错误: {file_path}")
                return False
            
            return self.validate_config(config, file_path)
            
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON解析错误: {e}")
            return False
        except Exception as e:
            self.errors.append(f"读取文件错误: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any], file_path: str) -> bool:
        """验证配置内容"""
        valid = True
        
        # 检查必须的配置节
        for section in self.REQUIRED_SECTIONS:
            if section not in config:
                self.errors.append(f"缺少必须的配置节: {section}")
                valid = False
            else:
                # 检查必须的配置项
                if section in self.REQUIRED_CONFIGS:
                    for config_key in self.REQUIRED_CONFIGS[section]:
                        if config_key not in config[section]:
                            self.errors.append(f"配置节 {section} 缺少必须的配置项: {config_key}")
                            valid = False
        
        # 验证配置值
        for key, rule in self.VALIDATION_RULES.items():
            value = self.get_nested_value(config, key)
            if value is not None:
                if isinstance(rule, list):
                    # 大小写不敏感验证
                    if isinstance(value, str):
                        value_lower = value.lower()
                        rule_lower = [r.lower() for r in rule]
                        if value_lower not in rule_lower:
                            self.errors.append(f"配置项 {key} 的值 '{value}' 不在允许的范围内: {rule}")
                            valid = False
                    else:
                        if value not in rule:
                            self.errors.append(f"配置项 {key} 的值 '{value}' 不在允许的范围内: {rule}")
                            valid = False
                elif isinstance(rule, tuple):
                    min_val, max_val = rule
                    if not (min_val <= value <= max_val):
                        self.errors.append(f"配置项 {key} 的值 {value} 不在允许的范围内: [{min_val}, {max_val}]")
                        valid = False
        
        return valid
    
    def get_nested_value(self, config: Dict[str, Any], key: str) -> Any:
        """获取嵌套配置值"""
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value
    
    def validate_env_example(self, file_path: str) -> bool:
        """验证.env.example文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            env_vars = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key = line.split('=')[0]
                        env_vars.append(key)
            
            # 检查必须的环境变量
            required_env_vars = [
                'APP_NAME', 'APP_ENV', 'APP_ROOT_PATH',
                'APP_SERVER_HOST', 'APP_SERVER_PORT',
                'APP_LOG_LEVEL', 'APP_LOG_FILE'
            ]
            
            valid = True
            for env_var in required_env_vars:
                if env_var not in env_vars:
                    self.errors.append(f".env.example 缺少必须的环境变量: {env_var}")
                    valid = False
            
            return valid
            
        except Exception as e:
            self.errors.append(f"读取.env.example文件错误: {e}")
            return False
    
    def validate_example_files(self, directory: str) -> bool:
        """验证示例文件"""
        valid = True
        
        # 检查.env.example
        env_example = os.path.join(directory, '.env.example')
        if os.path.exists(env_example):
            if not self.validate_env_example(env_example):
                valid = False
        else:
            self.warnings.append(f"缺少.env.example文件")
        
        # 检查config.example.yaml
        yaml_example = os.path.join(directory, 'config.example.yaml')
        if os.path.exists(yaml_example):
            if not self.validate_yaml(yaml_example):
                valid = False
        else:
            self.warnings.append(f"缺少config.example.yaml文件")
        
        # 检查config.example.json
        json_example = os.path.join(directory, 'config.example.json')
        if os.path.exists(json_example):
            if not self.validate_json(json_example):
                valid = False
        else:
            self.warnings.append(f"缺少config.example.json文件")
        
        return valid
    
    def print_results(self):
        """打印验证结果"""
        if self.errors:
            print("❌ 验证失败:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("⚠️  警告:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ 验证通过")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python validate_config.py <目录或文件>")
        print("示例:")
        print("  python validate_config.py .")
        print("  python validate_config.py config.yaml")
        sys.exit(1)
    
    path = sys.argv[1]
    validator = ConfigValidator()
    
    if os.path.isfile(path):
        # 验证单个文件
        if path.endswith('.yaml') or path.endswith('.yml'):
            validator.validate_yaml(path)
        elif path.endswith('.json'):
            validator.validate_json(path)
        elif path.endswith('.env.example'):
            validator.validate_env_example(path)
        else:
            print(f"不支持的文件格式: {path}")
            sys.exit(1)
    elif os.path.isdir(path):
        # 验证目录中的示例文件
        validator.validate_example_files(path)
    else:
        print(f"路径不存在: {path}")
        sys.exit(1)
    
    validator.print_results()
    
    if validator.errors:
        sys.exit(1)


if __name__ == '__main__':
    main()