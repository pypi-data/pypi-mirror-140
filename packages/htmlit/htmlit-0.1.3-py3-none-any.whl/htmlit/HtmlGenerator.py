import logging
import shutil
from collections import defaultdict
from typing import List

import markdown as md
import pandas as pd
import treefiles as tf
from jinja2 import Environment, PackageLoader, select_autoescape


class BaseBlock:
    def __init__(self, content, assets=None, **kw):
        self.content = content
        self.assets = tf.none(assets, [])
        self.kw = kw
        self._html = None
        self.html = self.content
        self.init()

    def init(self):
        pass

    @property
    def html(self) -> str:
        h = ""
        if "mt" in self.kw:
            h += f"""<div style='height: {self.kw["mt"]}px'></div>"""
        h += tf.none(self._html, "")
        if "mb" in self.kw:
            h += f"""<div style='height: {self.kw["mb"]}px'></div>"""
        return h

    @html.setter
    def html(self, value):
        raise NotImplementedError

    def copy_assets(self, out_dir):
        for x in self.assets:
            tf.copyfile(x, out_dir)
            self.html = self.html.replace(x, out_dir / tf.basename(x))


class ImgBlock(BaseBlock):
    def init(self):
        self.assets.append(self.content)

    @BaseBlock.html.setter
    def html(self, value: str):
        self._html = IMG.format(src=value)


class VideoBlock(BaseBlock):
    def init(self):
        self.assets.append(self.content)

    @BaseBlock.html.setter
    def html(self, value: str):
        self._html = VID.format(src=value)


class TexBlock(BaseBlock):
    @BaseBlock.html.setter
    def html(self, value: str):
        self._html = f"$${value}$$"


class MdBlock(BaseBlock):
    @BaseBlock.html.setter
    def html(self, value: str):
        self._html = md.markdown(value)


class DfBlock(BaseBlock):
    @BaseBlock.html.setter
    def html(self, value: pd.DataFrame):
        self._html = (
            value.to_html(classes=["table"], border=0, index=False)
            .replace(' style="text-align: right;"', "")
            .replace("<th>", "<th scope='col'>")
        )


class RowBlock(BaseBlock):
    @BaseBlock.html.setter
    def html(self, value: str):
        self._html = value


class HtmlGenerator:
    def __init__(self, new_env=True):
        self.python_dyn: List[BaseBlock] = []

        if new_env:
            self.env = Environment(
                loader=PackageLoader("htmlit.HtmlGenerator"),
                autoescape=select_autoescape(),
            )

    def get_include(self, out_dir):
        out_dir = tf.Tree(out_dir).dump()
        for x in self.python_dyn:
            x.copy_assets(out_dir)

        space = lambda x: f"<div style='height: {x}px'></div>"
        python_dyn = space(100).join([x.html for x in self.python_dyn])
        python_dyn = f"{space(50)}{python_dyn}{space(400)}"
        return python_dyn

    def render(self, out_dir: tf.T, save_zip: bool = False):
        out_dir = tf.Str(out_dir)
        python_dyn = self.get_include(out_dir)
        template = self.env.get_template("index.html")
        aa = template.render(
            enumerate=enumerate,
            python_dyn=python_dyn,
        )
        aa = aa.replace("\u2013", "-")

        fname = out_dir / "index.html"
        tf.dump_str(fname, aa)
        log.info(f"HTML report wrote to file://{fname}")

        if save_zip:
            shutil.make_archive(out_dir, "zip", out_dir)
            log.info(f"Wrote zip to file://{out_dir+'.zip'}")

    def markdown(self, s, **kw):
        self.python_dyn.append(MdBlock(s, **kw))

    def latex(self, s):
        self.python_dyn.append(TexBlock(s))

    def image(self, src: str):
        self.python_dyn.append(ImgBlock(src))

    def dataframe(self, df: pd.DataFrame):
        self.python_dyn.append(DfBlock(df))

    def video(self, src: str):
        self.python_dyn.append(VideoBlock(src))

    @property
    def row(self):
        class Row(HtmlGenerator):
            def __init__(s):
                super().__init__(new_env=False)
                s.col_keys = []

            def __enter__(s):
                return s

            def __call__(s, idx, key="col"):
                s.col_keys.append((idx, key))
                return s

            def __exit__(s, exc_type, exc_val, exc_tb):
                txt = "<div class='row'>\n"
                blocks = defaultdict(list)
                assets = []
                for ck, block in zip(s.col_keys, s.python_dyn):
                    blocks[ck[0]].append((block, ck[1]))
                    assets.extend(block.assets)
                for k, v in blocks.items():
                    txt += f"<div class='{v[0][1]}'>\n"
                    for bv, _ in v:
                        txt += bv.html + "\n"
                    txt += "</div>\n"
                txt += "</div>\n"
                self.python_dyn.append(RowBlock(txt, assets=assets))

        return Row()


IMG = """
<div>
    <a href="{src}">
        <img src="{src}" class="img-fluid">
    </a>
</div>
""".strip()
VID = """
<div>
    <video width="480" height="320" controls="controls">
        <source src="{src}" type="video/mp4">
    </video>
</div>
""".strip()

log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    gen = HtmlGenerator()
    gen.render(tf.f(__file__) / "test.html")
