import logging
from pathlib import Path
import platform
import shutil


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)

system = platform.system()
FILE_DIR = Path(__file__).absolute().parent

VSCODE_SNIPPETS_DIR = Path()
if system == 'Windows' or system == 'Linux':
    raise NotImplementedError
elif system == 'Darwin':
    VSCODE_SNIPPETS_DIR = Path('/Users/stone/Documents/code/mine/template_snippet')

name_map = {
    'pandas': 'python',
    'fastapi': 'python',
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
    o_file_path = FILE_DIR.parent / f'.vscode/{o_file_name}'
    t_file_path = VSCODE_SNIPPETS_DIR / f'{cate}/{o_file_name}'
    # 备份
    if t_file_path.exists():
        shutil.copy(t_file_path, FILE_DIR.parent / 'backup/sps')
    # 覆盖
    if t_file_path.exists():
        t_file_path.replace(o_file_path)
    else:
        shutil.copy(o_file_path, VSCODE_SNIPPETS_DIR / f'{cate}')

    _logger.info(f'处理完成: {o_file_name}')
