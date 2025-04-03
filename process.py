import os
import re
import uuid
import base64
import time
from bs4 import BeautifulSoup
from pathlib import Path

def save_base64_images(html_path, output_dir="images"):
    """
    处理HTML中的Base64图片（支持PNG/JPEG/SVG等格式）
    :param html_path: HTML文件路径
    :param output_dir: 图片保存目录（相对路径）
    :return: 处理后的HTML内容
    """
    # 创建图片保存目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # 匹配所有图片类型的Base64数据
    base64_pattern = re.compile(
        r'^data:(image/(?:png|jpeg|svg\+xml));base64,'
    )
    
    for img_tag in soup.find_all('img', src=base64_pattern):
        base64_str = img_tag['src']
        
        try:
            # 解析MIME类型
            mime_match = base64_pattern.search(base64_str)
            mime_type = mime_match.group(1)
            
            # 分割数据头和实际数据
            header, data = base64_str.split(',', 1)
            
            # 解码Base64数据
            decoded_data = base64.b64decode(data)
            
            # 确定文件扩展名和写入模式
            if "svg" in mime_type:
                file_ext = "svg"
                content = decoded_data.decode('utf-8')
                write_mode = 'w'
            else:
                file_ext = mime_type.split('/')[-1].replace('+xml', '')
                content = decoded_data
                write_mode = 'wb'
            
            # 生成唯一文件名（UUID+时间戳）
            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:8]
            file_name = f"{unique_id}_{timestamp}.{file_ext}"
            file_path = os.path.join(output_dir, file_name)
            
            # 确保文件名唯一
            while os.path.exists(file_path):
                unique_id = uuid.uuid4().hex[:8]
                file_name = f"{unique_id}_{timestamp}.{file_ext}"
                file_path = os.path.join(output_dir, file_name)
            
            # 保存文件
            with open(file_path, write_mode, encoding='utf-8' if write_mode == 'w' else None) as f:
                f.write(content)
            
            # 替换为相对路径
            img_tag['src'] = os.path.join(output_dir, file_name)
            
        except (ValueError, UnicodeDecodeError) as e:
            print(f"解码失败: {str(e)}")
            continue
        except Exception as e:
            print(f"文件操作异常: {str(e)}")
            continue

    return str(soup)

# 使用示例
if __name__ == "__main__":
    processed_html = save_base64_images("习题列表页.html")
    with open("习题列表页_new.html", "w", encoding='utf-8') as f:
        f.write(processed_html)
    print("图片已保存至images目录")