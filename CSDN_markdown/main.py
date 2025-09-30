import io
import re
import os
import urllib.request
from typing import Tuple
from PIL import Image
from loguru import logger

input_file_dir: str = "./in"  # 需要转换的文件夹
output_file_dir: str = "./out"  # 转换后输出的文件夹
scale: float = 1.2  # 图片整体缩放比例
use_width_percent: bool = True  # 是否使用 width 百分比属性放缩
max_width: int = 960  # 标准图片宽度参考值

# 水印相关参数
watermark: str = "x-oss-process=image/watermark"  # 为图片添加图片或文字水印
type: str = "ZHJvaWRzYW5zZmFsbGJhY2s"  # 文字水印字体（Base64编码）
shadow: str = "50"  # 指定文字水印的阴影透明度
text: str = "Q1NETiBAemhlbGlrdQ=="  # 文字水印内容（Base64编码）
size: str = "20"  # 文字水印大小
color: str = "FFFFFF"  # 文字水印颜色
t: str = "70"  # 水印图片或水印文字的透明度
g: str = "se"  # 水印位置

if_watermark: bool = False  # 是否为图片添加水印


def generate_watermark() -> str:
    """
    根据上述参数生成水印
    :return: 返回生成的水印字符串
    """
    return f"?{watermark},type_{type},shadow_{shadow},text_{text},size_{size},color_{color},t_{t},g_{g}"


def get_size(img_path: str) -> Tuple[int, int]:
    """
    根据图片链接获取图片的大小
    :param img_path: 图片链接
    :return: 返回一个包含图片宽度和高度的元组
    """
    response = urllib.request.urlopen(img_path)
    temp_img = io.BytesIO(response.read())
    img = Image.open(temp_img)
    return img.size


def alter(s: re.Match) -> str:
    """
    处理未修改大小的图片
    :param s: 正则表达式匹配对象
    :return: 返回处理后的图片链接
    """
    logger.info(s)
    w, h = get_size(s.group(2))
    new_w, new_h = int(scale * w), int(scale * h)
    width = int(w * scale / max_width * 100)
    if use_width_percent:
        return '<img src="' + s.group(2) + (
            generate_watermark() if if_watermark else "") + f'#pic_center" width="{width}%">'
    else:
        return '<img src="' + s.group(2) + (
            generate_watermark() if if_watermark else "") + f'#pic_center" width="{new_w}" height="{new_h}">'


def alter_zoom(s: re.Match) -> str:
    """
    处理 typora 中用 zoom 属性修改过大小的图片
    :param s: 正则表达式匹配对象
    :return: 返回处理后的图片链接
    """
    logger.info(s)
    zoom_value = int(s.group(4)) / 100
    w, h = get_size(s.group(2))
    new_w, new_h = int(zoom_value * w), int(zoom_value * h)
    width = int(w * scale * zoom_value / max_width * 100)
    if use_width_percent:
        return s.group(1) + s.group(2) + (generate_watermark() if if_watermark else "") + "#pic_center" + s.group(
            3) + f'width="{width}%"' + s.group(5)
    else:
        return s.group(1) + s.group(2) + (generate_watermark() if if_watermark else "") + "#pic_center" + s.group(
            3) + f'width="{new_w}" height="{new_h}"' + s.group(5)


def process_file(input_file_path: str, output_file_path: str) -> None:
    """
    处理单个文件
    :param input_file_path: 输入文件路径
    :param output_file_path: 输出文件路径
    """
    logger.info(f"-------------------开始处理 {input_file_path}--------------------")
    with open(input_file_path, "r", encoding="utf-8") as fin, open(output_file_path, "w",
                                                                   encoding="utf-8") as fout:
        pattern = re.compile(r"(!\[image-\d+]\()(.+)(\))")  # 未修改大小的图片的匹配规则
        pattern_zoom = re.compile(r'(<img src=")(.*)(" .* )style="zoom:\s?(\d+)%;"(\s?/>)')  # 带有 zoom 属性的图片的匹配规则
        content = fin.read()  # 读取文件内容
        content1 = pattern.subn(alter, content)  # 第一次处理
        content2 = pattern_zoom.subn(alter_zoom, content1[0])  # 第二次处理
        fout.write(content2[0])  # 写入新文件
        logger.info(f"原始图片替换次数：{content1[1]}")
        logger.info(f"zoom 属性图片替换次数：{content2[1]}")
        logger.info(f"总共替换次数：{content1[1] + content2[1]}")


# 处理 in 文件夹下的所有 md 文件，输出到 out 文件夹下，保持文件名不变，若 out 文件夹中已存在同名文件则跳过
if __name__ == "__main__":
    # 检查输出文件夹是否存在，不存在则创建
    if not os.path.exists(output_file_dir):
        os.makedirs(output_file_dir)
    # 遍历输入文件夹下的所有文件
    for file_name in os.listdir(input_file_dir):
        # 如果文件是.md文件
        if file_name.endswith(".md"):
            # 构造输入输出文件路径
            input_file_path = os.path.join(input_file_dir, file_name)
            output_file_path = os.path.join(output_file_dir, file_name)
            # 如果输出文件已存在，则跳过
            if os.path.exists(output_file_path):
                logger.info(f"跳过 \"{file_name}\"，因为输出目录中已存在。")
                continue
            # 处理文件
            process_file(input_file_path, output_file_path)
