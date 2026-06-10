"""信息几何 (Information Geometry) 可视化讲解视频（带中文旁白）

用 Manim + Manim Voiceover (gTTS) 渲染的中文讲解视频，共 6 个场景：

1. TitleScene          —— 片头
2. ManifoldScene       —— 概率分布族是一个流形
3. EuclideanFailsScene —— 欧氏距离会骗人 / KL 散度
4. FisherMetricScene   —— Fisher 信息 = 流形上的黎曼度量
5. GeodesicScene       —— 测地线：分布之间的最短路径
6. SummaryScene        —— 自然梯度与总结

渲染（需要联网，gTTS 在线合成语音）：
    manim -qm information_geometry.py TitleScene ManifoldScene \
        EuclideanFailsScene FisherMetricScene GeodesicScene SummaryScene
然后用 ffmpeg 把各段拼接成完整视频（见 render.sh）。
"""

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
import numpy as np

CJK = "Noto Sans CJK SC"

C_BLUE = "#4FC3F7"
C_PINK = "#FF6B9D"
C_YELLOW = "#FFD166"
C_GREEN = "#7AE582"
C_GREY = "#9E9E9E"


def gaussian(x, mu, sigma):
    return np.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (np.sqrt(2 * np.pi) * sigma)


def make_heading(zh, en):
    zh_t = Text(zh, font=CJK, font_size=38, weight=BOLD, color=C_YELLOW)
    en_t = Text(en, font_size=22, color=C_GREY, slant=ITALIC)
    g = VGroup(zh_t, en_t).arrange(DOWN, buff=0.12)
    g.to_edge(UP, buff=0.3)
    return g


class IGScene(VoiceoverScene):
    """带中文 gTTS 旁白的基类。"""

    def setup_voice(self):
        self.set_speech_service(GTTSService(lang="zh-CN"))


class TitleScene(IGScene):
    def construct(self):
        self.setup_voice()

        # 背景：几条高斯曲线
        axes = Axes(
            x_range=[-6, 6], y_range=[0, 1.0],
            x_length=13, y_length=4.5,
            axis_config={"stroke_opacity": 0}, tips=False,
        ).shift(DOWN * 1.2)
        params = [(-2.5, 0.7, C_BLUE), (-0.8, 1.2, C_PINK),
                  (1.0, 0.5, C_GREEN), (2.8, 1.0, C_YELLOW)]
        curves = VGroup(*[
            axes.plot(lambda x, m=m, s=s: gaussian(x, m, s),
                      x_range=[-6, 6], color=c, stroke_opacity=0.45)
            for m, s, c in params
        ])

        title = Text("信息几何", font=CJK, font_size=80, weight=BOLD)
        title.set_color_by_gradient(C_BLUE, C_PINK)
        en = Text("Information Geometry", font_size=34, color=WHITE)
        sub = Text("—— 当概率分布遇见黎曼几何 ——", font=CJK,
                   font_size=26, color=C_GREY)
        head = VGroup(title, en, sub).arrange(DOWN, buff=0.35).shift(UP * 1.2)

        with self.voiceover(
            text="这期视频，我们聊一个优雅的数学话题：信息几何——"
                 "用几何的眼光来看概率分布。"
        ):
            self.play(LaggedStart(*[Create(c) for c in curves],
                                  lag_ratio=0.2), run_time=2.5)
            self.play(Write(title), run_time=1.5)
            self.play(FadeIn(en, shift=UP * 0.3), FadeIn(sub, shift=UP * 0.3),
                      run_time=1.2)

        q = Text("两个概率分布之间，距离是多少？", font=CJK,
                 font_size=34, color=C_YELLOW)
        q.shift(DOWN * 2.8)
        with self.voiceover(
            text="一切都从一个看似简单的问题开始：两个概率分布之间，"
                 "距离到底是多少？"
        ):
            self.play(Write(q), run_time=1.5)

        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)


class ManifoldScene(IGScene):
    def construct(self):
        self.setup_voice()

        head = make_heading("一、概率分布族是一个流形",
                            "A family of distributions is a manifold")
        formula = MathTex(
            r"p(x\mid\mu,\sigma)=\frac{1}{\sqrt{2\pi}\,\sigma}",
            r"\exp\!\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)",
            font_size=34,
        ).next_to(head, DOWN, buff=0.3)

        with self.voiceover(
            text="先从最熟悉的高斯分布说起。它由两个参数完全决定："
                 "均值和标准差。"
        ):
            self.play(FadeIn(head, shift=DOWN * 0.2))
            self.play(Write(formula), run_time=1.5)

        # 左：参数空间 (μ, σ)
        param_axes = Axes(
            x_range=[-3, 3, 1], y_range=[0, 3, 1],
            x_length=5, y_length=3.6,
            axis_config={"font_size": 22}, tips=False,
        ).to_edge(LEFT, buff=0.7).shift(DOWN * 1.2)
        param_labels = VGroup(
            MathTex(r"\mu", font_size=30).next_to(param_axes.x_axis, RIGHT, buff=0.15),
            MathTex(r"\sigma", font_size=30).next_to(param_axes.y_axis, UP, buff=0.15),
        )
        param_title = Text("参数空间", font=CJK, font_size=24, color=C_BLUE)
        param_title.next_to(param_axes, UP, buff=0.15).shift(LEFT * 1.6)

        # 右：分布空间
        dist_axes = Axes(
            x_range=[-6, 6, 2], y_range=[0, 0.9, 0.3],
            x_length=5.6, y_length=3.6,
            axis_config={"font_size": 22}, tips=False,
        ).to_edge(RIGHT, buff=0.7).shift(DOWN * 1.2)
        dist_labels = VGroup(
            MathTex(r"x", font_size=30).next_to(dist_axes.x_axis, RIGHT, buff=0.15),
            MathTex(r"p(x)", font_size=30).next_to(dist_axes.y_axis, UP, buff=0.15),
        )
        dist_title = Text("概率分布", font=CJK, font_size=24, color=C_PINK)
        dist_title.next_to(dist_axes, UP, buff=0.15).shift(RIGHT * 1.6)

        with self.voiceover(
            text="左边是参数空间，横轴是均值，纵轴是标准差；"
                 "右边画出对应的概率密度曲线。"
        ):
            self.play(
                Create(param_axes), Create(dist_axes),
                FadeIn(param_labels), FadeIn(dist_labels),
                FadeIn(param_title), FadeIn(dist_title),
                run_time=1.5,
            )

        mu = ValueTracker(0.0)
        sigma = ValueTracker(1.0)

        dot = always_redraw(lambda: Dot(
            param_axes.c2p(mu.get_value(), sigma.get_value()),
            color=C_YELLOW, radius=0.09,
        ))
        curve = always_redraw(lambda: dist_axes.plot(
            lambda x: gaussian(x, mu.get_value(), sigma.get_value()),
            x_range=[-6, 6], color=C_YELLOW, stroke_width=4,
        ))
        arrow = always_redraw(lambda: Arrow(
            param_axes.c2p(mu.get_value(), sigma.get_value()),
            dist_axes.c2p(-5.5, 0.75),
            color=C_GREY, stroke_width=2, buff=0.2,
            max_tip_length_to_length_ratio=0.04,
        ))

        note = Text("参数空间中的一个点  ⟷  一个完整的概率分布",
                    font=CJK, font_size=26, color=WHITE)
        note.to_edge(DOWN, buff=0.35)

        with self.voiceover(
            text="关键的观察是：参数空间中的每一个点，"
                 "都对应一个完整的概率分布。"
        ):
            self.play(FadeIn(dot), Create(curve), GrowArrow(arrow))
            self.play(Write(note), run_time=1.2)

        with self.voiceover(
            text="当我们在参数空间里移动这个点，右边的分布也跟着"
                 "平移、变胖、变瘦。"
        ):
            for m, s, rt in [(2.0, 1.0, 2.0), (2.0, 2.2, 2.0),
                             (-1.8, 0.5, 2.5), (0.0, 1.0, 2.0)]:
                self.play(mu.animate.set_value(m), sigma.animate.set_value(s),
                          run_time=rt, rate_func=smooth)

        note2 = Text("整个分布族 = 一张二维曲面（统计流形）",
                     font=CJK, font_size=26, color=C_GREEN)
        note2.to_edge(DOWN, buff=0.35)
        grid_dots = VGroup(*[
            Dot(param_axes.c2p(mm, ss), radius=0.03, color=C_BLUE,
                fill_opacity=0.6)
            for mm in np.linspace(-2.6, 2.6, 12)
            for ss in np.linspace(0.3, 2.7, 8)
        ])

        with self.voiceover(
            text="把所有可能的参数收集起来，整个高斯分布族就构成了"
                 "一张二维曲面。数学家给它起了个名字，叫统计流形。"
        ):
            self.play(FadeOut(note), FadeIn(note2))
            self.play(LaggedStart(*[FadeIn(d) for d in grid_dots],
                                  lag_ratio=0.01), run_time=2)

        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)


class EuclideanFailsScene(IGScene):
    def construct(self):
        self.setup_voice()

        head = make_heading("二、参数的欧氏距离会骗人",
                            "Euclidean distance in parameter space misleads")
        with self.voiceover(
            text="有了流形，很自然会想用参数的欧氏距离来度量两个分布的远近。"
                 "但这个直觉会骗人。"
        ):
            self.play(FadeIn(head, shift=DOWN * 0.2))

        # 两组对比：Δμ = 1 相同，σ 不同
        axes_kw = dict(
            x_range=[-5, 6, 2], y_range=[0, 1.05, 0.5],
            x_length=5.4, y_length=2.9,
            axis_config={"font_size": 20}, tips=False,
        )
        axL = Axes(**axes_kw).shift(LEFT * 3.3 + DOWN * 0.15)
        axR = Axes(**axes_kw).shift(RIGHT * 3.3 + DOWN * 0.15)

        s1, s2 = 0.4, 2.0
        cL1 = axL.plot(lambda x: gaussian(x, 0, s1), x_range=[-5, 6],
                       color=C_BLUE, stroke_width=4)
        cL2 = axL.plot(lambda x: gaussian(x, 1, s1), x_range=[-5, 6],
                       color=C_PINK, stroke_width=4)
        cR1 = axR.plot(lambda x: gaussian(x, 0, s2), x_range=[-5, 6],
                       color=C_BLUE, stroke_width=4)
        cR2 = axR.plot(lambda x: gaussian(x, 1, s2), x_range=[-5, 6],
                       color=C_PINK, stroke_width=4)

        labL = MathTex(r"\sigma=0.4", font_size=30, color=C_GREY)
        labL.next_to(axL, UP, buff=0.15)
        labR = MathTex(r"\sigma=2", font_size=30, color=C_GREY)
        labR.next_to(axR, UP, buff=0.15)

        with self.voiceover(
            text="看这两组高斯分布：左边标准差是零点四，右边是二，"
                 "两边蓝色和粉色曲线的均值都只相差一。"
        ):
            self.play(Create(axL), Create(axR), FadeIn(labL), FadeIn(labR))
            self.play(Create(cL1), Create(cR1), run_time=1.2)
            self.play(Create(cL2), Create(cR2), run_time=1.2)

        note = Text("两边都是 Δμ = 1：参数距离完全相同",
                    font=CJK, font_size=27, color=C_YELLOW)
        note.to_edge(DOWN, buff=0.4)
        with self.voiceover(
            text="也就是说，这两对分布在参数空间里的欧氏距离完全相同。"
        ):
            self.play(Write(note), run_time=1.2)

        verdictL = Text("一眼就能区分", font=CJK, font_size=26, color=C_GREEN)
        verdictL.next_to(axL, DOWN, buff=0.12)
        verdictR = Text("几乎无法区分", font=CJK, font_size=26, color=RED)
        verdictR.next_to(axR, DOWN, buff=0.12)
        with self.voiceover(
            text="但左边两条曲线几乎不重叠，一眼就能区分；"
                 "右边却几乎完全叠在一起，根本分不开。"
        ):
            self.play(FadeIn(verdictL, shift=UP * 0.2),
                      FadeIn(verdictR, shift=UP * 0.2))

        # 引入 KL 散度
        kl_label = Text("KL 散度（可区分性）：", font=CJK, font_size=24,
                        color=C_GREY)
        kl_formula = MathTex(
            r"D_{\mathrm{KL}}(p\,\|\,q)=\int p(x)\,\log\frac{p(x)}{q(x)}\,dx",
            font_size=32,
        )
        kl = VGroup(kl_label, kl_formula).arrange(RIGHT, buff=0.25)
        kl.to_edge(DOWN, buff=0.3)
        with self.voiceover(
            text="统计学里用 KL 散度来量化两个分布的可区分性：它衡量的是，"
                 "数据能多容易地暴露出这两个分布的不同。"
        ):
            self.play(FadeOut(note))
            self.play(Write(kl), run_time=1.6)

        # 同方差高斯：D_KL = Δμ² / 2σ²
        klL = MathTex(r"D_{\mathrm{KL}}\approx 3.13", font_size=32,
                      color=C_GREEN).next_to(verdictL, DOWN, buff=0.12)
        klR = MathTex(r"D_{\mathrm{KL}}=0.125", font_size=32,
                      color=RED).next_to(verdictR, DOWN, buff=0.12)
        with self.voiceover(
            text="算一下：左边这对的 KL 散度约为三点一三，"
                 "右边只有零点一二五，相差二十五倍。"
        ):
            self.play(FadeIn(klL), FadeIn(klR))

        concl = Text("分布之间的“真实距离”依赖于所在位置 —— 我们需要一个度量",
                     font=CJK, font_size=27, color=C_YELLOW)
        concl.to_edge(DOWN, buff=0.35)
        with self.voiceover(
            text="同样的参数距离，真实的差异却天差地别。这说明分布之间的"
                 "距离依赖于所在的位置——我们需要一把随位置变化的尺子，"
                 "也就是一个度量。"
        ):
            self.play(FadeOut(kl), FadeIn(concl))

        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)


class FisherMetricScene(IGScene):
    def construct(self):
        self.setup_voice()

        head = make_heading("三、Fisher 信息：流形上的黎曼度量",
                            "Fisher information as a Riemannian metric")
        expand = MathTex(
            r"D_{\mathrm{KL}}\big(p_\theta \,\|\, p_{\theta+d\theta}\big)",
            r"\;\approx\;",
            r"\tfrac{1}{2}\, d\theta^{\top} G(\theta)\, d\theta",
            font_size=38,
        ).shift(UP * 1.4)
        expand[2].set_color(C_YELLOW)
        note1 = Text("KL 散度在局部是一个二次型 —— 这就是“距离的平方”",
                     font=CJK, font_size=25, color=C_GREY)
        note1.next_to(expand, DOWN, buff=0.3)

        with self.voiceover(
            text="这把尺子其实就藏在 KL 散度里。把它在一点附近做泰勒展开，"
                 "一阶项正好消失，剩下的主导项是一个二次型——"
                 "这正是距离的平方该有的样子。"
        ):
            self.play(FadeIn(head, shift=DOWN * 0.2))
            self.play(Write(expand), run_time=2)
            self.play(FadeIn(note1))

        fisher = MathTex(
            r"G_{ij}(\theta) \;=\; \mathbb{E}_{x\sim p_\theta}\!\left[",
            r"\frac{\partial \log p_\theta(x)}{\partial \theta_i}\,",
            r"\frac{\partial \log p_\theta(x)}{\partial \theta_j}",
            r"\right]",
            font_size=36,
        ).shift(DOWN * 0.6)
        fname = Text("Fisher 信息矩阵", font=CJK, font_size=26, color=C_BLUE)
        fname.next_to(fisher, DOWN, buff=0.25)
        with self.voiceover(
            text="这个二次型的系数矩阵，就是大名鼎鼎的 Fisher 信息矩阵。"
                 "它给统计流形装上了一个黎曼度量。"
        ):
            self.play(Write(fisher), run_time=2)
            self.play(FadeIn(fname))

        gauss_metric = MathTex(
            r"ds^2 \;=\; \frac{d\mu^2 + 2\,d\sigma^2}{\sigma^2}",
            font_size=42, color=C_YELLOW,
        ).shift(UP * 0.9 + RIGHT * 3.2)
        gauss_note = Text("高斯族 (μ, σ) 的 Fisher 度量", font=CJK,
                          font_size=24, color=C_GREY)
        gauss_note.next_to(gauss_metric, UP, buff=0.2)
        hyper = Text("分母里的 σ² —— 这正是双曲几何（庞加莱半平面）！",
                     font=CJK, font_size=27, color=C_GREEN)
        hyper.next_to(gauss_metric, DOWN, buff=0.35)

        with self.voiceover(
            text="对高斯分布族具体算出来，距离的平方等于：均值的微分平方，"
                 "加上两倍标准差微分的平方，再除以标准差的平方。"
        ):
            self.play(FadeOut(note1), FadeOut(fisher), FadeOut(fname),
                      expand.animate.scale(0.8).to_edge(LEFT, buff=0.6)
                                              .shift(UP * 0.6))
            self.play(FadeIn(gauss_note), Write(gauss_metric), run_time=1.8)

        with self.voiceover(
            text="注意分母里的西格玛平方——这恰好是双曲几何，"
                 "也就是著名的庞加莱半平面。"
        ):
            self.play(Write(hyper), run_time=1.5)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # 可视化：不同 σ 处的“单位信息圆”
        head2 = make_heading("同样的信息距离，不一样的参数步长",
                             "Unit Fisher balls in the (μ, σ) half-plane")
        plane = Axes(
            x_range=[-4, 4, 1], y_range=[0, 3.2, 1],
            x_length=10, y_length=4.6,
            axis_config={"font_size": 22}, tips=False,
        ).shift(DOWN * 0.8)
        plabels = VGroup(
            MathTex(r"\mu", font_size=30).next_to(plane.x_axis, RIGHT, buff=0.15),
            MathTex(r"\sigma", font_size=30).next_to(plane.y_axis, UP, buff=0.15),
        )

        # Fisher 距离为 ε 的“圆”：dμ = εσ cosθ, dσ = (εσ/√2) sinθ
        eps = 0.55
        balls = VGroup()
        centers = [(-3, 0.5), (-1.5, 1.0), (0, 1.5), (1.5, 2.0), (3, 2.5)]
        for m0, s0 in centers:
            ball = plane.plot_parametric_curve(
                lambda t, m0=m0, s0=s0: np.array([
                    m0 + eps * s0 * np.cos(t),
                    s0 + eps * s0 / np.sqrt(2) * np.sin(t),
                    0,
                ]),
                t_range=[0, TAU], color=C_BLUE, stroke_width=3,
            )
            center_dot = Dot(plane.c2p(m0, s0), radius=0.05, color=C_YELLOW)
            balls.add(VGroup(ball, center_dot))

        with self.voiceover(
            text="双曲是什么感觉？我们在不同位置画出信息距离相等的小圆。"
        ):
            self.play(FadeIn(head2, shift=DOWN * 0.2))
            self.play(Create(plane), FadeIn(plabels))

        note2 = Text("σ 越大，同样的信息距离覆盖的参数范围越大",
                     font=CJK, font_size=27, color=C_YELLOW)
        note2.to_edge(DOWN, buff=0.35)
        note3 = Text("（分布越“模糊”，参数变一点也看不出来）",
                     font=CJK, font_size=24, color=C_GREY)
        note3.next_to(note2, UP, buff=0.18)

        with self.voiceover(
            text="注意看：西格玛越大，圆就越大。也就是说，分布越模糊，"
                 "参数挪动同样一段，分布本身几乎看不出变化——"
                 "尺子在高处变长了。"
        ):
            self.play(LaggedStart(*[Create(b) for b in balls],
                                  lag_ratio=0.25), run_time=3)
            self.play(Write(note2), run_time=1.3)
            self.play(FadeIn(note3))

        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)


class GeodesicScene(IGScene):
    def construct(self):
        self.setup_voice()

        head = make_heading("四、测地线：分布之间的最短路径",
                            "Geodesics: shortest paths between distributions")
        plane = Axes(
            x_range=[-3, 3, 1], y_range=[0, 2.2, 1],
            x_length=8.2, y_length=4.2,
            axis_config={"font_size": 22}, tips=False,
        ).to_edge(LEFT, buff=0.6).shift(DOWN * 0.9)
        plabels = VGroup(
            MathTex(r"\mu", font_size=30).next_to(plane.x_axis, RIGHT, buff=0.15),
            MathTex(r"\sigma", font_size=30).next_to(plane.y_axis, UP, buff=0.15),
        )
        with self.voiceover(
            text="有了度量，就可以问一个几何学最经典的问题："
                 "两个分布之间的最短路径——测地线——长什么样？"
        ):
            self.play(FadeIn(head, shift=DOWN * 0.2))
            self.play(Create(plane), FadeIn(plabels))

        # 两个端点分布
        muA, sA = -2.0, 0.6
        muB, sB = 2.0, 0.6
        dotA = Dot(plane.c2p(muA, sA), color=C_BLUE, radius=0.09)
        dotB = Dot(plane.c2p(muB, sB), color=C_PINK, radius=0.09)
        labA = MathTex(r"\mathcal{N}(-2,\,0.6^2)", font_size=26,
                       color=C_BLUE).next_to(dotA, DOWN, buff=0.18)
        labB = MathTex(r"\mathcal{N}(2,\,0.6^2)", font_size=26,
                       color=C_PINK).next_to(dotB, DOWN, buff=0.18)
        with self.voiceover(
            text="比如这两个高斯分布：均值一个在负二，一个在正二，"
                 "标准差都是零点六。"
        ):
            self.play(FadeIn(dotA, scale=0.5), FadeIn(dotB, scale=0.5),
                      Write(labA), Write(labB))

        # 欧氏直线（虚线）
        straight = DashedLine(plane.c2p(muA, sA), plane.c2p(muB, sB),
                              color=RED, stroke_width=3)
        lab_s = Text("欧氏直线", font=CJK, font_size=22, color=RED)
        lab_s.next_to(straight, DOWN, buff=0.12)
        with self.voiceover(text="欧氏直觉告诉我们：走直线。"):
            self.play(Create(straight), FadeIn(lab_s))

        # Fisher 测地线：在 u = μ/√2 坐标下是以 σ=0 轴为圆心的半圆
        uA, uB = muA / np.sqrt(2), muB / np.sqrt(2)
        c = (uB ** 2 + sB ** 2 - uA ** 2 - sA ** 2) / (2 * (uB - uA))
        r = np.sqrt((uA - c) ** 2 + sA ** 2)
        thA = np.arctan2(sA, uA - c)
        thB = np.arctan2(sB, uB - c)

        def geo_point(t):
            th = thA + (thB - thA) * t
            u = c + r * np.cos(th)
            s = r * np.sin(th)
            return np.array([u * np.sqrt(2), s, 0])

        geodesic = plane.plot_parametric_curve(
            geo_point, t_range=[0, 1], color=C_YELLOW, stroke_width=5,
        )
        lab_g = Text("Fisher 测地线", font=CJK, font_size=22, color=C_YELLOW)
        lab_g.next_to(plane.c2p(0, r), UP, buff=0.12)
        with self.voiceover(
            text="但在 Fisher 度量下，真正的最短路径是这条向上拱起的弧线。"
        ):
            self.play(Create(geodesic), FadeIn(lab_g), run_time=2)

        note = Text("最短路径会先“变模糊”再“变清晰”", font=CJK,
                    font_size=27, color=C_YELLOW).to_edge(DOWN, buff=0.35)

        # 右侧小图：沿测地线插值出的分布
        inset = Axes(
            x_range=[-4.5, 4.5, 2], y_range=[0, 0.75, 0.25],
            x_length=4.3, y_length=2.8,
            axis_config={"font_size": 18}, tips=False,
        ).to_edge(RIGHT, buff=0.45).shift(UP * 0.4)
        inset_title = Text("路径上的分布", font=CJK, font_size=22,
                           color=C_GREY).next_to(inset, UP, buff=0.18)

        t_tr = ValueTracker(0.0)
        moving = always_redraw(lambda: Dot(
            plane.c2p(*geo_point(t_tr.get_value())[:2]),
            color=WHITE, radius=0.10,
        ))
        moving_curve = always_redraw(lambda: inset.plot(
            lambda x: gaussian(x, *geo_point(t_tr.get_value())[:2]),
            x_range=[-4.5, 4.5], color=C_YELLOW, stroke_width=4,
        ))
        sigma_read = always_redraw(lambda: MathTex(
            rf"\sigma = {geo_point(t_tr.get_value())[1]:.2f}",
            font_size=28, color=WHITE,
        ).next_to(inset, DOWN, buff=0.22))

        with self.voiceover(
            text="沿着测地线走一遍，右边实时显示路径上的分布："
                 "它先变得模糊，标准差在中点达到最大，然后再重新变得清晰。"
        ):
            self.play(Write(note), Create(inset), FadeIn(inset_title))
            self.play(FadeIn(moving), Create(moving_curve),
                      FadeIn(sigma_read))
            self.play(t_tr.animate.set_value(1.0), run_time=5,
                      rate_func=double_smooth)

        note2 = Text("绕道高 σ 区域更“便宜”—— 因为那里的尺子更长",
                     font=CJK, font_size=27, color=C_GREEN)
        note2.to_edge(DOWN, buff=0.35)
        with self.voiceover(
            text="为什么要绕道？因为高西格玛区域的尺子更长，"
                 "在那里移动更便宜。这就是双曲几何的智慧。"
        ):
            self.play(t_tr.animate.set_value(0.0), run_time=3.5,
                      rate_func=smooth)
            self.play(FadeOut(note), FadeIn(note2))

        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)


class SummaryScene(IGScene):
    def construct(self):
        self.setup_voice()

        head = make_heading("五、信息几何有什么用？",
                            "Why information geometry matters")
        ng = MathTex(
            r"\theta_{t+1} \;=\; \theta_t \;-\; \eta\,",
            r"G(\theta_t)^{-1}",
            r"\nabla_\theta L",
            font_size=40,
        ).shift(UP * 1.5)
        ng[1].set_color(C_YELLOW)
        ng_name = Text("自然梯度下降：在分布空间中沿最陡方向走",
                       font=CJK, font_size=26, color=C_GREY)
        ng_name.next_to(ng, DOWN, buff=0.25)

        with self.voiceover(
            text="信息几何不只是优雅，它非常实用。把梯度下降里的梯度，"
                 "用 Fisher 矩阵的逆修正一下，就得到自然梯度——"
                 "它在分布空间中沿真正最陡的方向前进，"
                 "而且不依赖于参数化的方式。"
        ):
            self.play(FadeIn(head, shift=DOWN * 0.2))
            self.play(Write(ng), run_time=1.8)
            self.play(FadeIn(ng_name))

        apps = VGroup(
            Text("• 自然梯度 / K-FAC：更稳更快的神经网络优化", font=CJK,
                 font_size=26),
            Text("• Cramér–Rao 下界：参数估计的精度极限", font=CJK,
                 font_size=26),
            Text("• 变分推断、EM 算法的几何解释", font=CJK, font_size=26),
            Text("• 强化学习：TRPO / PPO 的 KL 信赖域", font=CJK,
                 font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.32).shift(DOWN * 0.9)
        with self.voiceover(
            text="此外，参数估计的克拉美罗下界、变分推断和 EM 算法的几何解释、"
                 "强化学习中的 KL 信赖域方法，背后都有信息几何的影子。"
        ):
            self.play(LaggedStart(*[FadeIn(a, shift=RIGHT * 0.3)
                                    for a in apps],
                                  lag_ratio=0.35), run_time=3)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # 三步总结
        recap_title = Text("回顾", font=CJK, font_size=40, weight=BOLD,
                           color=C_YELLOW).to_edge(UP, buff=0.5)

        def box(zh, tex, color):
            t = Text(zh, font=CJK, font_size=24, color=color)
            f = MathTex(tex, font_size=26)
            inner = VGroup(t, f).arrange(DOWN, buff=0.2)
            rect = RoundedRectangle(corner_radius=0.15,
                                    width=inner.width + 0.6,
                                    height=inner.height + 0.5,
                                    stroke_color=color)
            return VGroup(rect, inner.move_to(rect))

        b1 = box("分布族 = 流形", r"\{p_\theta\}", C_BLUE)
        b2 = box("Fisher 信息 = 度量", r"ds^2 = d\theta^\top G\, d\theta",
                 C_YELLOW)
        b3 = box("KL ≈ 距离²/2", r"D_{\mathrm{KL}}\approx \tfrac12\,ds^2",
                 C_PINK)
        boxes = VGroup(b1, b2, b3).arrange(RIGHT, buff=0.9).shift(UP * 0.4)
        arrows = VGroup(
            Arrow(b1.get_right(), b2.get_left(), buff=0.1, color=C_GREY),
            Arrow(b2.get_right(), b3.get_left(), buff=0.1, color=C_GREY),
        )

        with self.voiceover(
            text="回顾一下今天的三步：概率分布族是一个流形；"
                 "Fisher 信息给它装上了度量；而 KL 散度在局部，"
                 "就是距离平方的一半。"
        ):
            self.play(FadeIn(recap_title))
            self.play(FadeIn(b1, shift=UP * 0.3))
            self.play(GrowArrow(arrows[0]), FadeIn(b2, shift=UP * 0.3))
            self.play(GrowArrow(arrows[1]), FadeIn(b3, shift=UP * 0.3))

        final = Text("几何，是理解概率的另一双眼睛。", font=CJK,
                     font_size=32)
        final.set_color_by_gradient(C_BLUE, C_PINK)
        final.shift(DOWN * 1.8)
        with self.voiceover(
            text="几何，是理解概率的另一双眼睛。感谢观看，我们下期再见。"
        ):
            self.play(Write(final), run_time=2)

        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.2)
