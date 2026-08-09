---
name: generate-alias
description: 生成一些常用命令的缩写alias
---

# 用户输入
用户想要生成alias的command名称

# 示例
以 rclone 为例你应该生成以下形式的alias
```bash
alias rls='rclone ls'
alias rlsl='rclone lsd'
alias rcopy='rclone copy -P'
alias rrsync='rclone sync -P'
alias rmount='rclone mount --vfs-cache-mode full'
alias rumount='fusermount -uz'
alias rconf='rclone config'
alias rlist='rclone listremotes'
```