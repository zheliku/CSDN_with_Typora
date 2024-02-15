import io
import re
import urllib.request

from PIL import Image

file_dir = "./in"  # 需要转换的文件夹
scale = 1.2  # 图片整体缩放比例
use_width_percent = True  # 是否使用 width 百分比属性放缩
max_width = 960  # 标准图片宽度参考值

# 水印相关参数
watermark = "x-oss-process=image/watermark"  # 为图片添加图片或文字水印
type = "ZHJvaWRzYW5zZmFsbGJhY2s"  # 文字水印字体（Base64编码）
shadow = "50"  # 指定文字水印的阴影透明度
text = "Q1NETiBAemhlbGlrdQ=="  # 文字水印内容（Base64编码）
size = "20"  # 文字水印大小
color = "FFFFFF"  # 文字水印颜色
t = "70"  # 水印图片或水印文字的透明度
g = "se"  # 水印位置

if_watermark = False  # 是否为图片添加水印


def generate_watermark():  # 根据上述参数生成水印
    return f"?{watermark},type_{type},shadow_{shadow},text_{text},size_{size},color_{color},t_{t},g_{g}"


def get_size(img_path):  # 根据图片链接获取图片的大小
    response = urllib.request.urlopen(img_path)
    temp_img = io.BytesIO(response.read())
    img = Image.open(temp_img)
    # print(img.size)
    return img.size


def alter(s):  # 处理未修改大小的图片
    w, h = get_size(s.group(2))
    new_w, new_h = int(scale * w), int(scale * h)
    width = int(w * scale / max_width * 100)
    if use_width_percent:
        return '<img src="' + s.group(2) + (
            generate_watermark() if if_watermark else "") + f'#pic_center" width="{width}%">'
    else:
        return '<img src="' + s.group(2) + (
            generate_watermark() if if_watermark else "") + f'#pic_center" width="{new_w}" height="{new_h}">'


def alter_zoom(s):  # 处理 typora 中用 zoom 属性修改过大小的图片
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


file_name = "Unity 编辑器开发之编辑器拓展4 —— EditorGUIUtility.md"
with open("./in/" + file_name, "r", encoding="utf-8") as fin, open("./out/" + file_name, "w",
                                                                   encoding="utf-8") as fout:
    pattern = re.compile(r"(!\[image-\d+]\()(.+)(\))")  # 未修改大小的图片的匹配规则
    pattern_zoom = re.compile(r'(<img src=")(.*)(" .* )style="zoom:\s?(\d+)%;"(\s?/>)')  # 带有 zoom 属性的图片的匹配规则
    content = fin.read()  # 读取文件内容
    content1 = pattern.subn(alter, content)  # 第一次处理
    content2 = pattern_zoom.subn(alter_zoom, content1[0])  # 第二次处理
    fout.write(content2[0])  # 写入新文件
    print("原始图片替换次数：", content1[1])
    print("zoom 属性图片替换次数：", content2[1])
    print("总共替换次数：", content1[1] + content2[1])

