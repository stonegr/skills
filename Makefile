.PHONY: help s_vs s_sps
# ================================
# Config
# ================================
APP_NAME ?= skill_tools
ENV ?= dev
ARGS ?=

# 默认目标
.DEFAULT_GOAL := help

# ================================
# Help
# ================================
help: ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ================================
# Commands
# ================================

s_vs: ## 更新vscode的snippets
	uv run scripts/sync_vscode.py

s_sps: ## 更新vscode的sps
	uv run scripts/sync_sps.py