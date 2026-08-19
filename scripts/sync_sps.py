import logging
import os
from pathlib import Path
import platform
import shutil


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)

system = platform.system()
FILE_DIR = Path(__file__).absolute().parent

VSCODE_SNIPPETS_DIR = Path()
if system == 'Windows':
    raise NotImplementedError
elif system == 'Linux':
    VSCODE_SNIPPETS_DIR = Path('/home/mine/template_snippet')
elif system == 'Darwin':
    VSCODE_SNIPPETS_DIR = Path('/Users/stone/Documents/code/mine/template_snippet')

BACKUP_DIR = FILE_DIR.parent / 'backup' / 'sps'
os.makedirs(BACKUP_DIR, exist_ok=True)

name_map = {
    'pandas': 'python',
    'fastapi': 'python',
    'sqlalchemy': 'python',
    'sqlmodel': 'python',
    'marshmallow': 'python',
    'gorm': 'go',
}


def pop_list_null(lines: list, no_str: str = ''):
    while lines and lines[0] == no_str:
        lines.pop(0)
    while lines and lines[-1] == no_str:
        lines.pop()
    return lines


for name, cate in name_map.items():
    o_file_name = f'{name}.code-snippets'
    _logger.info(f'开始处理: {o_file_name}')
    o_file_path = FILE_DIR.parent / '.vscode' / f'{o_file_name}'
    t_file_path = VSCODE_SNIPPETS_DIR / f'{cate}/{o_file_name}'
    if t_file_path.exists():
        shutil.copy2(t_file_path, BACKUP_DIR)
        _logger.info(f'{o_file_name} 备份到 {BACKUP_DIR / o_file_name} 完成')
    # 拷贝
    if t_file_path.exists():
        t_file_path.write_text(o_file_path.read_text())
    else:
        shutil.copy2(o_file_path, VSCODE_SNIPPETS_DIR / f'{cate}')

    _logger.info(f'处理完成: {o_file_name}')
