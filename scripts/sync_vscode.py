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
if system == 'Windows' or system == 'Linux':
    raise NotImplementedError
elif system == 'Darwin':
    VSCODE_SNIPPETS_DIR = Path('~/Library/Application Support/Code/User/snippets').expanduser()

BACKUP_DIR = FILE_DIR.parent / 'backup' / 'vscode'
os.makedirs(BACKUP_DIR, exist_ok=True)

language_name_map = {
    'go': 'go',
    'javascript': 'javascript',
    'python': 'python',
    'shell': 'shellscript',
    'typescript': 'typescript',
    'rust': 'rust',
}


def pop_list_null(lines: list, no_str: str = ''):
    while lines and lines[0] == no_str:
        lines.pop(0)
    while lines and lines[-1] == no_str:
        lines.pop()
    return lines


for o_name, t_name in language_name_map.items():
    o_file_name = f'{o_name}.code-snippets'
    o_file_path = FILE_DIR.parent / '.vscode' / f'{o_file_name}'
    t_file_name = f'{t_name}.json'
    t_file_path = VSCODE_SNIPPETS_DIR / t_file_name
    _logger.info(f'开始处理: {o_file_name}')
    # 备份
    shutil.copy2(t_file_path, BACKUP_DIR)
    _logger.info(f'{t_file_path} 备份到 {BACKUP_DIR / t_file_name} 完成')
    with open(o_file_path, encoding='utf-8') as f:
        content_list = pop_list_null(f.readlines(), '\n')
    with open(t_file_path, encoding='utf-8') as f:
        des_content_list = pop_list_null(f.readlines(), '\n')
        if des_content_list[-2] not in ['    // cus\n', '   // cus\n']:
            content_list[-2] = ''.join(content_list[-2][:-1]) + ',' + '\n'
        try:
            des_content_list[des_content_list.index('    // auto\n') + 1 : des_content_list.index('    // cus\n')] = content_list[1:-1]
        except ValueError:
            des_content_list[des_content_list.index('	// auto\n') + 1 : des_content_list.index('	// cus\n')] = content_list[1:-1]
        except Exception as e:
            raise e
    with open(t_file_path, 'w', encoding='utf-8') as f:
        f.write(''.join(des_content_list))
    _logger.info(f'处理: {o_file_name}，完成!')
