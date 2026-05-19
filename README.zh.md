# ChimeraX Clip-Export 插件

将 ChimeraX 全局近/远裁剪面的设置导出为可复用的命令字符串。用法类似内置的 `view matrix` 命令——输出到 Log 窗口，之后粘贴回 Command 窗口即可恢复相同的裁剪配置。

## 安装

从 [Releases](https://github.com/kangkang042/chimerax-clip-export/releases) 下载最新的 `.whl` 文件，在 ChimeraX 中运行：

```
toolshed install /path/to/chimerax_clip_export-0.1.1-py3-none-any.whl
```

或从源码构建：

```bash
python build_wheel_manual.py
```

再用 `toolshed install` 安装 `dist/` 目录中生成的 wheel。

> **注意**：ChimeraX 1.11 内置的 setuptools 80.9.0 存在 bug，用 `package_dir` 构建 wheel 时不会包含 `.py` 源文件。因此本项目使用 `build_wheel_manual.py` 手动构建 wheel。

## 使用

1. 在 ChimeraX 中打开一个结构。
2. 通过 Side View 面板调整近/远裁剪面。
3. 在 Command 窗口输入 `clipstate`。
4. Log 窗口输出类似：

```
clip off ; clip near 0.5 far 100
```

5. 之后复制这段命令粘贴到 Command 窗口即可恢复完全相同的裁剪设置。

## 为什么是 `clip off ; clip near ... far ...`？

ChimeraX 内置的 `clip near X far Y` 命令在裁剪面已存在时是**相对移动**（从当前位置偏移 X），而非绝对定位。加上 `clip off` 前缀确保先清空裁剪面，后面的 near/far 值始终表示从旋转中心起算的绝对距离，无论当前裁剪状态如何都能精确还原。

## 环境要求

- ChimeraX 1.x（已在 1.11 上测试）
- Python 3.9+

## 许可

本项目仅供学习和个人使用。
