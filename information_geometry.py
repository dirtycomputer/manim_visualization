"""信息几何 (Information Geometry) 3D 可视化讲解视频（带中文旁白）

用 Manim (ThreeDScene) + Manim Voiceover (gTTS) 渲染的中文讲解视频，共 6 个场景：

1. TitleScene          —— 片头：旋转的三维高斯钟形曲面
2. ManifoldScene       —— 概率分布族铺成一张会变形的三维曲面
3. EuclideanFailsScene —— 两座高斯"山峰"：分得开 vs 融为一体
4. FisherMetricScene   —— Fisher 度量、单位信息圆与伪球面（曲率 -1）
5. GeodesicScene       —— 信息成本地形上的测地线 vs 欧氏直线
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
C_DBLUE = "#1565C0"
C_DPINK = "#AD1457"


def gaussian(x, mu, sigma):
    return np.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (np.sqrt(2 * np.pi) * sigma)


def biv_gaussian(x, y, cx, sigma):
    r2 = (x - cx) ** 2 + y ** 2
    return np.exp(-r2 / (2 * sigma ** 2)) / (2 * np.pi * sigma ** 2)


def make_heading(zh, en):
    zh_t = Text(zh, font=CJK, font_size=38, weight=BOLD, color=C_YELLOW)
    en_t = Text(en, font_size=22, color=C_GREY, slant=ITALIC)
    g = VGroup(zh_t, en_t).arrange(DOWN, buff=0.12)
    g.to_edge(UP, buff=0.3)
    return g


class IG3DScene(VoiceoverScene, ThreeDScene):
    """带中文 gTTS 旁白的 3D 基类。"""

    def setup_voice(self):
        self.set_speech_service(GTTSService(lang="zh-CN"))

    def fix(self, *mobs):
        """把屏幕文字/公式固定在相机坐标系，但先不显示（留给动画）。"""
        self.add_fixed_in_frame_mobjects(*mobs)
        self.remove(*mobs)


class TitleScene(IG3DScene):
    def construct(self):
        self.setup_voice()
        self.set_camera_orientation(phi=62 * DEGREES, theta=-45 * DEGREES,
                                    zoom=0.95)

        # 三维高斯钟形曲面
        bell = Surface(
            lambda u, v: np.array([u, v, 2.4 * np.exp(-(u * u + v * v) / 2.4)]),
            u_range=[-3.2, 3.2], v_range=[-3.2, 3.2],
            resolution=(30, 30),
            checkerboard_colors=[C_DBLUE, BLUE_E],
            fill_opacity=0.75, stroke_color=C_BLUE, stroke_width=0.5,
        ).shift(IN * 1.0)

        title = Text("信息几何", font=CJK, font_size=80, weight=BOLD)
        title.set_color_by_gradient(C_BLUE, C_PINK)
        en = Text("Information Geometry", font_size=34, color=WHITE)
        sub = Text("—— 当概率分布遇见黎曼几何 ——", font=CJK,
                   font_size=26, color=C_GREY)
        head = VGroup(title, en, sub).arrange(DOWN, buff=0.3).to_edge(UP, buff=0.6)
        self.fix(head)

        self.begin_ambient_camera_rotation(rate=0.12)
        with self.voiceover(
            text="这期视频，我们聊一个优雅的数学话题：信息几何——"
                 "用几何的眼光来看概率分布。"
        ):
            self.play(Create(bell), run_time=3)
            self.play(Write(title), run_time=1.5)
            self.play(FadeIn(en, shift=UP * 0.3), FadeIn(sub, shift=UP * 0.3),
                      run_time=1.2)

        q = Text("两个概率分布之间，距离是多少？", font=CJK,
                 font_size=34, color=C_YELLOW)
        q.to_edge(DOWN, buff=0.7)
        self.fix(q)
        with self.voiceover(
            text="一切都从一个看似简单的问题开始：两个概率分布之间，"
                 "距离到底是多少？"
        ):
            self.play(Write(q), run_time=1.5)

        self.wait(0.5)
        self.stop_ambient_camera_rotation()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)


class ManifoldScene(IG3DScene):
    def construct(self):
        self.setup_voice()
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES,
                                    zoom=0.85)

        head = make_heading("一、概率分布族是一个流形",
                            "A family of distributions is a manifold")
        formula = MathTex(
            r"p(x\mid\mu,\sigma)=\frac{1}{\sqrt{2\pi}\,\sigma}",
            r"\exp\!\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)",
            font_size=30,
        ).next_to(head, DOWN, buff=0.25)
        self.fix(head, formula)

        axes = ThreeDAxes(
            x_range=[-4, 4, 2], y_range=[-3, 3, 1], z_range=[0, 0.9, 0.3],
            x_length=8.5, y_length=6, z_length=2.8,
            axis_config={"font_size": 20},
        ).shift(IN * 0.8)
        xlab = axes.get_x_axis_label(MathTex("x", font_size=34))
        ylab = axes.get_y_axis_label(MathTex(r"\mu", font_size=34))
        zlab = axes.get_z_axis_label(MathTex(r"p(x)", font_size=30))

        with self.voiceover(
            text="先从最熟悉的高斯分布说起。它由两个参数完全决定："
                 "均值和标准差。"
        ):
            self.play(FadeIn(head, shift=DOWN * 0.2))
            self.play(Write(formula), run_time=1.5)
            self.play(Create(axes), FadeIn(xlab), FadeIn(ylab), FadeIn(zlab),
                      run_time=1.5)

        mu_tr = ValueTracker(-2.0)
        sig_tr = ValueTracker(1.0)

        def fam_curve():
            m, s = mu_tr.get_value(), sig_tr.get_value()
            return ParametricFunction(
                lambda t: axes.c2p(t, m, gaussian(t, m, s)),
                t_range=[-4, 4], color=C_YELLOW, stroke_width=5,
            )

        curve = always_redraw(fam_curve)
        with self.voiceover(
            text="固定一组参数，就得到一条密度曲线。参数空间中的每一个点，"
                 "都对应一个这样的完整分布。改变均值，曲线就沿着参数轴滑动。"
        ):
            curve0 = fam_curve()
            self.play(Create(curve0), run_time=1)
            self.remove(curve0)
            self.add(curve)
            self.play(mu_tr.animate.set_value(2.0), run_time=4,
                      rate_func=there_and_back)

        def fam_surface(s):
            return Surface(
                lambda u, v: axes.c2p(u, v, gaussian(u, v, s)),
                u_range=[-4, 4], v_range=[-2.6, 2.6],
                resolution=(32, 18),
                checkerboard_colors=[C_DBLUE, BLUE_E],
                fill_opacity=0.6, stroke_color=C_BLUE, stroke_width=0.4,
            )

        surf_static = fam_surface(1.0)
        with self.voiceover(
            text="把所有均值对应的曲线一字排开，它们就铺成了一张"
                 "三维空间里的曲面。"
        ):
            self.remove(curve)
            self.play(Create(surf_static), run_time=3)

        self.begin_ambient_camera_rotation(rate=0.08)
        dyn_surf = always_redraw(lambda: fam_surface(sig_tr.get_value()))
        with self.voiceover(
            text="再让标准差也动起来：整张曲面跟着变尖、变平。"
                 "均值和标准差，就是这张曲面的两个坐标。"
        ):
            self.remove(surf_static)
            self.add(dyn_surf)
            self.play(sig_tr.animate.set_value(0.55), run_time=2.5)
            self.play(sig_tr.animate.set_value(1.6), run_time=2.5)
            self.play(sig_tr.animate.set_value(1.0), run_time=2)

        self.remove(dyn_surf)
        surf_final = fam_surface(1.0)
        self.add(surf_final)

        note2 = Text("整个分布族 = 一张二维曲面（统计流形）",
                     font=CJK, font_size=26, color=C_GREEN)
        note2.to_edge(DOWN, buff=0.4)
        self.fix(note2)
        with self.voiceover(
            text="把所有可能的参数收集起来，整个高斯分布族就构成了"
                 "一张二维曲面。数学家给它起了个名字，叫统计流形。"
        ):
            self.play(FadeIn(note2, shift=UP * 0.2))

        self.wait(0.5)
        self.stop_ambient_camera_rotation()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)


class EuclideanFailsScene(IG3DScene):
    def construct(self):
        self.setup_voice()
        self.set_camera_orientation(phi=60 * DEGREES, theta=-70 * DEGREES,
                                    zoom=0.9)

        head = make_heading("二、参数的欧氏距离会骗人",
                            "Euclidean distance in parameter space misleads")
        self.fix(head)

        axes = ThreeDAxes(
            x_range=[-3, 4, 1], y_range=[-3, 3, 1], z_range=[0, 1.1, 0.5],
            x_length=8, y_length=6.5, z_length=3.2,
            axis_config={"font_size": 20},
        ).shift(IN * 1.0)

        sig_tr = ValueTracker(0.4)

        def bump(cx, colors, line_color):
            def make(s):
                return Surface(
                    lambda u, v: axes.c2p(u, v, biv_gaussian(u, v, cx, s)),
                    u_range=[-2.8, 3.8], v_range=[-2.8, 2.8],
                    resolution=(26, 26),
                    checkerboard_colors=colors,
                    fill_opacity=0.55, stroke_color=line_color,
                    stroke_width=0.4,
                )
            return make

        make_blue = bump(0.0, [C_DBLUE, BLUE_E], C_BLUE)
        make_pink = bump(1.0, [C_DPINK, MAROON_E], C_PINK)

        bumpL = make_blue(0.4)
        bumpR = make_pink(0.4)

        sig_label = MathTex(r"\sigma = 0.4,\quad \Delta\mu = 1",
                            font_size=34, color=C_YELLOW).to_edge(DOWN, buff=0.4)
        self.fix(sig_label)

        with self.voiceover(
            text="这次把高斯分布画成三维的山峰。蓝色和粉色两个分布，"
                 "标准差都是零点四，均值只相差一。两座山峰泾渭分明，"
                 "一眼就能区分。"
        ):
            self.play(FadeIn(head, shift=DOWN * 0.2))
            self.play(Create(axes), run_time=1.2)
            self.play(Create(bumpL), run_time=1.8)
            self.play(Create(bumpR), run_time=1.8)
            self.play(Write(sig_label))

        self.begin_ambient_camera_rotation(rate=0.06)

        dynL = always_redraw(lambda: make_blue(sig_tr.get_value()))
        dynR = always_redraw(lambda: make_pink(sig_tr.get_value()))
        sig_label2 = MathTex(r"\sigma = 1.2,\quad \Delta\mu = 1",
                             font_size=34, color=C_YELLOW).to_edge(DOWN, buff=0.4)
        self.fix(sig_label2)

        with self.voiceover(
            text="现在保持均值之差不变，把标准差增大到一点二。注意看："
                 "两座山慢慢摊平，融成了一片，再也分不开了。"
                 "可它们在参数空间里的欧氏距离，自始至终没有变。"
        ):
            self.remove(bumpL, bumpR)
            self.add(dynL, dynR)
            self.play(sig_tr.animate.set_value(1.2), run_time=5,
                      rate_func=smooth)
            self.play(FadeOut(sig_label), FadeIn(sig_label2))

        self.remove(dynL, dynR)
        bumpL2, bumpR2 = make_blue(1.2), make_pink(1.2)
        self.add(bumpL2, bumpR2)

        kl = MathTex(
            r"D_{\mathrm{KL}}=\frac{\Delta\mu^2}{2\sigma^2}:\qquad",
            r"\sigma=0.4 \;\Rightarrow\; 3.13", r"\qquad",
            r"\sigma=1.2 \;\Rightarrow\; 0.35",
            font_size=32,
        ).to_edge(DOWN, buff=1.0)
        kl[1].set_color(C_GREEN)
        kl[3].set_color(RED)
        self.fix(kl)
        with self.voiceover(
            text="用 KL 散度来量化可区分性：标准差零点四时约为三点一三，"
                 "摊平之后只剩零点三五，差了将近十倍——"
                 "而参数距离完全相同。"
        ):
            self.play(Write(kl), run_time=2)

        concl = Text("分布之间的“真实距离”依赖于所在位置 —— 我们需要一个度量",
                     font=CJK, font_size=27, color=C_YELLOW)
        concl.to_edge(DOWN, buff=0.4)
        self.fix(concl)
        with self.voiceover(
            text="同样的参数距离，真实的差异却天差地别。这说明分布之间的"
                 "距离依赖于所在的位置——我们需要一把随位置变化的尺子，"
                 "也就是一个度量。"
        ):
            self.play(FadeOut(kl), FadeOut(sig_label2), FadeIn(concl))

        self.wait(0.5)
        self.stop_ambient_camera_rotation()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)


class FisherMetricScene(IG3DScene):
    def construct(self):
        self.setup_voice()
        self.set_camera_orientation(phi=55 * DEGREES, theta=-90 * DEGREES,
                                    zoom=0.95)

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
        self.fix(head, expand, note1)

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
        self.fix(fisher, fname)
        with self.voiceover(
            text="这个二次型的系数矩阵，就是大名鼎鼎的 Fisher 信息矩阵。"
                 "它给统计流形装上了一个黎曼度量。"
        ):
            self.play(Write(fisher), run_time=2)
            self.play(FadeIn(fname))

        gauss_metric = MathTex(
            r"ds^2 \;=\; \frac{d\mu^2 + 2\,d\sigma^2}{\sigma^2}",
            font_size=42, color=C_YELLOW,
        ).shift(DOWN * 0.4)
        gauss_note = Text("高斯族 (μ, σ) 的 Fisher 度量", font=CJK,
                          font_size=24, color=C_GREY)
        gauss_note.next_to(gauss_metric, UP, buff=0.2)
        hyper = Text("分母里的 σ² —— 这是双曲几何！", font=CJK,
                     font_size=27, color=C_GREEN)
        hyper.next_to(gauss_metric, DOWN, buff=0.35)
        self.fix(gauss_metric, gauss_note, hyper)

        with self.voiceover(
            text="对高斯分布族具体算出来，距离的平方等于：均值的微分平方，"
                 "加上两倍标准差微分的平方，再除以标准差的平方。"
        ):
            self.play(FadeOut(fisher), FadeOut(fname), FadeOut(note1))
            self.play(FadeIn(gauss_note), Write(gauss_metric), run_time=1.8)

        with self.voiceover(
            text="注意分母里的西格玛平方——这恰好是双曲几何。"
        ):
            self.play(Write(hyper), run_time=1.5)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        # 第二部分：平面上的“单位信息圆”（俯视微倾视角）
        head2 = make_heading("同样的信息距离，不一样的参数步长",
                             "Unit Fisher balls in the (μ, σ) half-plane")
        self.fix(head2)

        plane = Axes(
            x_range=[-4, 4, 1], y_range=[0, 3.2, 1],
            x_length=10, y_length=5.6,
            axis_config={"font_size": 22}, tips=False,
        ).shift(DOWN * 0.6)
        mu_lab = MathTex(r"\mu", font_size=30).next_to(plane.x_axis, RIGHT,
                                                       buff=0.15)
        sg_lab = MathTex(r"\sigma", font_size=30).next_to(plane.y_axis, UP,
                                                          buff=0.15)

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
            text="双曲是什么感觉？我们在参数半平面的不同位置，"
                 "画出信息距离相等的小圆。"
        ):
            self.play(Create(plane), FadeIn(mu_lab), FadeIn(sg_lab),
                      FadeIn(head2, shift=DOWN * 0.2))

        note2 = Text("σ 越大，同样的信息距离覆盖的参数范围越大",
                     font=CJK, font_size=26, color=C_YELLOW)
        note2.to_edge(DOWN, buff=0.35)
        self.fix(note2)
        with self.voiceover(
            text="注意看：西格玛越大，圆就越大。也就是说，分布越模糊，"
                 "参数挪动同样一段，分布本身几乎看不出变化——"
                 "尺子在高处变长了。"
        ):
            self.play(LaggedStart(*[Create(b) for b in balls],
                                  lag_ratio=0.25), run_time=3)
            self.play(Write(note2), run_time=1.3)

        # 第三部分：伪球面（曲率 -1 的曲面）
        pseudo = Surface(
            lambda u, v: np.array([
                1.7 / np.cosh(u) * np.cos(v),
                1.7 / np.cosh(u) * np.sin(v),
                1.7 * (u - np.tanh(u)) - 1.5,
            ]),
            u_range=[0.03, 3.0], v_range=[0, TAU],
            resolution=(24, 40),
            checkerboard_colors=[C_DBLUE, BLUE_E],
            fill_opacity=0.8, stroke_color=C_BLUE, stroke_width=0.4,
        )
        pname = Text("伪球面：高斯曲率 K ≡ −1", font=CJK, font_size=28,
                     color=C_GREEN).to_edge(DOWN, buff=0.4)
        self.fix(pname)

        with self.voiceover(
            text="这种处处负曲率的几何，可以局部卷成三维空间里一个"
                 "喇叭形的曲面——伪球面，它的高斯曲率处处等于负一。"
                 "高斯分布族的内在几何，就长这个样子。"
        ):
            self.play(FadeOut(plane), FadeOut(balls), FadeOut(mu_lab),
                      FadeOut(sg_lab), FadeOut(note2), FadeOut(head2))
            self.set_camera_orientation(phi=68 * DEGREES, theta=-90 * DEGREES,
                                        zoom=0.95)
            self.begin_ambient_camera_rotation(rate=0.25)
            self.play(Create(pseudo), FadeIn(pname), run_time=3.5)

        self.wait(1)
        self.stop_ambient_camera_rotation()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)


class GeodesicScene(IG3DScene):
    COST_K = 0.55

    def construct(self):
        self.setup_voice()
        self.set_camera_orientation(phi=62 * DEGREES, theta=-95 * DEGREES,
                                    zoom=0.9)

        head = make_heading("四、测地线：分布之间的最短路径",
                            "Geodesics: shortest paths between distributions")
        self.fix(head)

        axes = ThreeDAxes(
            x_range=[-3, 3, 1], y_range=[0, 2.4, 1], z_range=[0, 2.4, 1],
            x_length=9, y_length=5.5, z_length=3.4,
            axis_config={"font_size": 20},
        ).shift(IN * 1.2)
        xlab = axes.get_x_axis_label(MathTex(r"\mu", font_size=34))
        ylab = axes.get_y_axis_label(MathTex(r"\sigma", font_size=34))

        def cost(s):
            return self.COST_K / s

        terrain = Surface(
            lambda u, v: axes.c2p(u, v, cost(v)),
            u_range=[-3, 3], v_range=[0.28, 2.3],
            resolution=(28, 22),
            checkerboard_colors=[GREY_D, GREY_E],
            fill_opacity=0.45, stroke_color=C_GREY, stroke_width=0.4,
        )
        terr_note = Text("高度 = 移动单位参数的信息成本（∝ 1/σ）",
                         font=CJK, font_size=24, color=C_GREY)
        terr_note.to_edge(DOWN, buff=0.35)
        self.fix(terr_note)

        with self.voiceover(
            text="有了度量，就可以问一个几何学最经典的问题：两个分布之间的"
                 "最短路径——测地线——长什么样？这次我们把尺子的长度画成"
                 "三维地形：高度代表移动单位参数所要付出的信息成本。"
                 "标准差越小的地方成本越高，像一面陡峭的山壁。"
        ):
            self.play(FadeIn(head, shift=DOWN * 0.2))
            self.play(Create(axes), FadeIn(xlab), FadeIn(ylab), run_time=1.5)
            self.play(Create(terrain), FadeIn(terr_note), run_time=3)

        # 两个端点分布
        muA, sA = -2.0, 0.6
        muB, sB = 2.0, 0.6

        def lift(m, s):
            return axes.c2p(m, s, cost(s) + 0.03)

        dotA = Dot3D(lift(muA, sA), color=C_BLUE, radius=0.09)
        dotB = Dot3D(lift(muB, sB), color=C_PINK, radius=0.09)
        labAB = MathTex(r"\mathcal{N}(-2,\,0.6^2)\ \longleftrightarrow\ "
                        r"\mathcal{N}(2,\,0.6^2)",
                        font_size=30, color=WHITE).to_corner(UL, buff=0.4).shift(DOWN * 1.2)
        self.fix(labAB)
        with self.voiceover(
            text="比如这两个高斯分布：均值一个在负二，一个在正二，"
                 "标准差都是零点六——它们都站在山壁的半山腰上。"
        ):
            self.play(FadeIn(dotA, scale=0.5), FadeIn(dotB, scale=0.5),
                      Write(labAB))

        # 欧氏直线：沿山腰高处横切
        straight = DashedVMobject(ParametricFunction(
            lambda t: lift(muA + (muB - muA) * t, sA),
            t_range=[0, 1], stroke_width=4,
        ), num_dashes=40).set_color(RED)
        lab_s = Text("欧氏直线：贴着高成本山脊走", font=CJK, font_size=23,
                     color=RED).to_corner(UR, buff=0.4).shift(DOWN * 1.2)
        self.fix(lab_s)
        with self.voiceover(
            text="欧氏直觉告诉我们走直线——但那意味着一路贴着"
                 "高成本的山脊行走。"
        ):
            self.play(Create(straight), FadeIn(lab_s))

        # Fisher 测地线：在 u = μ/√2 坐标下是半圆
        uA, uB = muA / np.sqrt(2), muB / np.sqrt(2)
        c = (uB ** 2 + sB ** 2 - uA ** 2 - sA ** 2) / (2 * (uB - uA))
        r = np.sqrt((uA - c) ** 2 + sA ** 2)
        thA = np.arctan2(sA, uA - c)
        thB = np.arctan2(sB, uB - c)

        def geo_point(t):
            th = thA + (thB - thA) * t
            u = c + r * np.cos(th)
            s = r * np.sin(th)
            return u * np.sqrt(2), s

        geodesic = ParametricFunction(
            lambda t: lift(*geo_point(t)),
            t_range=[0, 1], color=C_YELLOW, stroke_width=5,
        )
        lab_g = Text("Fisher 测地线：下到低成本的谷地", font=CJK,
                     font_size=23, color=C_YELLOW)
        lab_g.next_to(lab_s, DOWN, buff=0.15)
        self.fix(lab_g)
        with self.voiceover(
            text="而 Fisher 度量下真正的最短路径，会先下到山谷——"
                 "也就是标准差更大的区域——再爬回来。"
        ):
            self.play(Create(geodesic), FadeIn(lab_g), run_time=2.5)

        # 右下角固定小图：沿测地线插值出的分布
        inset = Axes(
            x_range=[-4.5, 4.5, 2], y_range=[0, 0.75, 0.25],
            x_length=3.9, y_length=2.2,
            axis_config={"font_size": 16}, tips=False,
        ).to_corner(DR, buff=0.35)
        inset_bg = SurroundingRectangle(inset, color=GREY_D, fill_color=BLACK,
                                        fill_opacity=0.75, buff=0.18)
        inset_title = Text("路径上的分布", font=CJK, font_size=20,
                           color=C_GREY).next_to(inset, UP, buff=0.12)

        t_tr = ValueTracker(0.0)

        def inset_graph():
            m, s = geo_point(t_tr.get_value())
            return inset.plot(lambda x: gaussian(x, m, s),
                              x_range=[-4.5, 4.5], color=C_YELLOW,
                              stroke_width=4)

        inset_curve = inset_graph()
        sigma_read = DecimalNumber(sA, num_decimal_places=2, font_size=28,
                                   color=WHITE)
        sigma_lab = MathTex(r"\sigma =", font_size=28, color=WHITE)
        sigma_grp = VGroup(sigma_lab, sigma_read).arrange(RIGHT, buff=0.12)
        sigma_grp.next_to(inset_bg, LEFT, buff=0.25)

        moving = always_redraw(lambda: Dot3D(
            lift(*geo_point(t_tr.get_value())), color=WHITE, radius=0.1,
        ))

        self.add_fixed_in_frame_mobjects(inset_bg, inset, inset_title,
                                         inset_curve, sigma_grp)
        inset_curve.add_updater(lambda m: m.become(inset_graph()))
        sigma_read.add_updater(
            lambda d: d.set_value(geo_point(t_tr.get_value())[1]))

        with self.voiceover(
            text="沿着测地线走一遍，右下角实时显示路径上的分布："
                 "它先变得模糊，标准差在中点达到最大，然后再重新变得清晰。"
        ):
            self.add(moving)
            self.play(t_tr.animate.set_value(1.0), run_time=6,
                      rate_func=double_smooth)

        note2 = Text("绕道高 σ 的谷地更“便宜”—— 因为那里的尺子更长",
                     font=CJK, font_size=26, color=C_GREEN)
        note2.to_edge(DOWN, buff=0.35)
        self.fix(note2)
        with self.voiceover(
            text="为什么要绕道？因为高西格玛区域的尺子更长，在那里移动"
                 "更便宜。欧氏直线翻越的是成本的山脊，测地线选择了"
                 "成本的山谷。这就是双曲几何的智慧。"
        ):
            self.play(t_tr.animate.set_value(0.0), run_time=4,
                      rate_func=smooth)
            self.play(FadeOut(terr_note), FadeIn(note2))

        self.wait(0.5)
        inset_curve.clear_updaters()
        sigma_read.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)


class SummaryScene(IG3DScene):
    def construct(self):
        self.setup_voice()
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES,
                                    zoom=0.95)

        # 背景：缓慢旋转的半透明钟形曲面
        bell = Surface(
            lambda u, v: np.array([u, v, 2.0 * np.exp(-(u * u + v * v) / 2.4)]),
            u_range=[-3, 3], v_range=[-3, 3],
            resolution=(24, 24),
            checkerboard_colors=[C_DBLUE, BLUE_E],
            fill_opacity=0.25, stroke_color=C_BLUE, stroke_width=0.3,
        ).shift(IN * 1.2)
        self.add(bell)
        self.begin_ambient_camera_rotation(rate=0.08)

        head = make_heading("五、信息几何有什么用？",
                            "Why information geometry matters")
        ng = MathTex(
            r"\theta_{t+1} \;=\; \theta_t \;-\; \eta\,",
            r"G(\theta_t)^{-1}",
            r"\nabla_\theta L",
            font_size=40,
        ).shift(UP * 1.3)
        ng[1].set_color(C_YELLOW)
        ng_name = Text("自然梯度下降：在分布空间中沿最陡方向走",
                       font=CJK, font_size=26, color=C_GREY)
        ng_name.next_to(ng, DOWN, buff=0.25)
        self.fix(head, ng, ng_name)

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
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.32).shift(DOWN * 1.0)
        self.fix(apps)
        with self.voiceover(
            text="此外，参数估计的克拉美罗下界、变分推断和 EM 算法的几何解释、"
                 "强化学习中的 KL 信赖域方法，背后都有信息几何的影子。"
        ):
            self.play(LaggedStart(*[FadeIn(a, shift=RIGHT * 0.3)
                                    for a in apps],
                                  lag_ratio=0.35), run_time=3)

        self.play(FadeOut(head), FadeOut(ng), FadeOut(ng_name), FadeOut(apps),
                  run_time=0.8)

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
                                    stroke_color=color,
                                    fill_color=BLACK, fill_opacity=0.6)
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
        self.fix(recap_title, boxes, arrows)

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
        self.fix(final)
        with self.voiceover(
            text="几何，是理解概率的另一双眼睛。感谢观看，我们下期再见。"
        ):
            self.play(Write(final), run_time=2)

        self.wait(0.5)
        self.stop_ambient_camera_rotation()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.2)
