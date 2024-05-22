import os


def create_dir(dir_path):
    """创建目录"""
    if not os.path.isdir(dir_path):
        dir_path = os.path.dirname(dir_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def load_file(file_path):
    """读取文件并返回其内容

    Args:
    - file_path (str): 文件路径

    Returns:
    - str: 包含文件的字符串
    """
    with open(file_path, "r", encoding="utf-8") as f:
        str = f.read()
    return str


def save_file(file_path, text):
    """保存文件"""
    create_dir(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)