# 信息几何可视化讲解视频 (Information Geometry with Manim)

用 [Manim Community](https://www.manim.community/) 制作的中文讲解视频，
约 4 分半，介绍信息几何的核心思想。

## 视频结构

| 场景 | 内容 |
| --- | --- |
| `TitleScene` | 片头：两个概率分布之间，距离是多少？ |
| `ManifoldScene` | 高斯分布族 (μ, σ) 是一个二维统计流形：参数点 ⟷ 分布的实时联动 |
| `EuclideanFailsScene` | 相同的 Δμ=1，可区分性却天差地别 —— 欧氏距离失效，引入 KL 散度 |
| `FisherMetricScene` | KL 的二阶展开给出 Fisher 信息矩阵；高斯族的度量 ds² = (dμ²+2dσ²)/σ² 正是双曲半平面；不同 σ 处的"单位信息圆" |
| `GeodesicScene` | Fisher 测地线 vs 欧氏直线：最短路径会先"变模糊"再"变清晰"，沿途分布实时演示 |
| `SummaryScene` | 自然梯度、Cramér–Rao 下界、TRPO/PPO 等应用 + 三步回顾 |

## 环境依赖

```bash
# 系统依赖（Debian/Ubuntu）
sudo apt install libpango1.0-dev libcairo2-dev pkg-config ffmpeg \
    texlive texlive-latex-extra texlive-science dvisvgm fonts-noto-cjk

# Python 依赖
pip install -r requirements.txt
```

中文文本使用 `Noto Sans CJK SC` 字体，请确保已安装（`fonts-noto-cjk`）。

## 渲染

```bash
./render.sh        # 720p30（默认）
./render.sh -ql    # 480p15 快速预览
./render.sh -qh    # 1080p60 高清
```

脚本会渲染全部 6 个场景并用 ffmpeg 拼接为 `information_geometry_full.mp4`。

也可以单独渲染某个场景：

```bash
manim -qm information_geometry.py GeodesicScene
```

## 数学背景速记

- 统计流形：参数化分布族 {p_θ}，每个点是一个分布。
- Fisher 信息矩阵：G_ij(θ) = E[∂_i log p · ∂_j log p]，
  是 KL 散度的二阶泰勒展开系数，定义了流形上的黎曼度量。
- 高斯族 (μ, σ) 的 Fisher 度量为 ds² = (dμ² + 2dσ²)/σ²，
  与庞加莱半平面（双曲几何）等距（μ 方向差一个 √2 缩放）。
- 测地线：代换 u = μ/√2 后是圆心在 σ=0 轴上的半圆，
  说明两个分布之间的最短路径会经过更高 σ（更"模糊"）的区域。
