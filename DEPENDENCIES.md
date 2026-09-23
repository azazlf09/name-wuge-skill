# 网感名生成器 - 依赖说明

## 必需依赖

1. **opencc-python-reimplemented**
   - 用途：繁简体转换
   - 已在原 skill 中使用
   - 安装：`pip install opencc-python-reimplemented`

2. **pypinyin**
   - 用途：音韵判断（获取拼音、韵母、声母）
   - 新增依赖，用于音韵和谐度检测
   - 安装：`pip install pypinyin`

## 可选依赖

如果未安装 `pypinyin`，网感名生成器仍可运行，但会跳过音韵过滤功能。

## 安装命令

```bash
pip install opencc-python-reimplemented pypinyin
# 或使用 requirements.txt
pip install -r requirements.txt
```
