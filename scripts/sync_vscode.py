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
    VSCODE_SNIPPETS_DIR = Path('~/Library/Application Support/Code/User/snippets').expanduser()

language_name_map = {
    'go': 'go',
    'javascript': 'javascript',
    'python': 'python',
    'shell': 'shellscript',
    'typescript': 'typescript',
}


def pop_list_null(lines: list, no_str: str = ''):
    while lines and lines[0] == no_str:
        lines.pop(0)
    while lines and lines[-1] == no_str:
        lines.pop()
    return lines


for file in FILE_DIR.parent.joinpath('.vscode').iterdir():
    if file.is_file() and file.name.endswith('.code-snippets'):
        _logger.info(f'开始处理: {file}')
        file_name = language_name_map[file.name.rsplit('.', 1)[0]]
        dest_file_name = f'{file_name}.json'
        dest_file_path = VSCODE_SNIPPETS_DIR / dest_file_name
        # 备份
        shutil.copy(dest_file_path, FILE_DIR.parent / 'backup/vscode')
        _logger.info(f'{dest_file_path} 备份到 {FILE_DIR.parent / "backup/vscode" / dest_file_name} 完成')
        with open(file, encoding='utf-8') as f:
            content_list = pop_list_null(f.readlines(), '\n')
        with open(dest_file_path, encoding='utf-8') as f:
            des_content_list = pop_list_null(f.readlines(), '\n')
            if des_content_list[-2] not in ['    // cus\n', '   // cus\n']:
                content_list[-2] = ''.join(content_list[-2][:-1]) + ',' + '\n'
            try:
                des_content_list[des_content_list.index('    // auto\n') + 1 : des_content_list.index('    // cus\n')] = content_list[1:-1]
            except ValueError:
                des_content_list[des_content_list.index('	// auto\n') + 1 : des_content_list.index('	// cus\n')] = content_list[1:-1]
            except Exception as e:
                raise e
        with open(dest_file_path, 'w', encoding='utf-8') as f:
            f.write(''.join(des_content_list))
        _logger.info(f'处理: {file}，完成!')
