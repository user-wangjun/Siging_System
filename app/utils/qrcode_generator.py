"""
二维码生成工具
生成签到二维码图片（PNG 格式，Base64 编码）
"""

import io
import base64
import qrcode
from qrcode.image.pil import PilImage


def generate_checkin_qrcode(checkin_code: str, activity_title: str = None, size: int = 10) -> str:
    """生成签到二维码，返回 Base64 编码的 PNG 图片

    Args:
        checkin_code: 签到码
        activity_title: 活动标题（显示在二维码下方）
        size: 二维码模块大小

    Returns:
        Base64 编码的图片字符串，可直接用于 <img src="data:image/png;base64,...">
    """
    # 构建二维码内容（包含签到码和提示信息）
    content = f"CHECKIN:{checkin_code}"

    # 创建二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 高容错率
        box_size=size,
        border=2,
    )
    qr.add_data(content)
    qr.make(fit=True)

    # 生成图片
    img = qr.make_image(fill_color="black", back_color="white")

    # 如果有活动标题，在底部添加文字
    if activity_title:
        from PIL import Image, ImageDraw, ImageFont
        # 创建带文字的新图片
        width, height = img.size
        text_height = 40
        new_img = Image.new('RGB', (width, height + text_height), 'white')
        new_img.paste(img, (0, 0))

        draw = ImageDraw.Draw(new_img)
        # 尝试使用系统字体，失败则用默认字体
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except Exception:
            font = ImageFont.load_default()

        # 居中绘制文字
        text = activity_title[:20] + "..." if len(activity_title) > 20 else activity_title
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, height + 10), text, fill="black", font=font)
        img = new_img

    # 转为 Base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return f"data:image/png;base64,{img_base64}"


def generate_checkin_qrcode_url(checkin_code: str) -> str:
    """生成二维码内容（纯文本签到码，供扫码设备解析）"""
    return f"CHECKIN:{checkin_code}"
