from subprocess import check_output, CalledProcessError, STDOUT
from threading import Lock, Thread

from logsmal import loglevel

try:
    # poetry add tqdm
    from tqdm import tqdm
except ImportError:
    ...


def os_exe_thread(
        label_command: str,
        command_list: list[str],
        call_log_info: loglevel = lambda _x, flag: ...,
        call_log_error: loglevel = lambda _x, flag: ...,
):
    """
    Выполнить команды системы в нескольких потоках.


    :param label_command: Общее название команд
    :param command_list: Список команд
    :param call_log_info: Функция для логов информации
    :param call_log_error: Функция для логов ошибок

    :Пример вызова:

    ..code-bloc:: python

        indir = os.path.dirname(__file__)
        command_list: list[str] = []
        command = "pull"

        for _path in listdir():
            command_list.append(f"cd {path.join(indir, _path)} && git {command}")

        os_exe_thread(
            "GIT PULL",
            command_list,
            call_log_info=logger.info,
            call_log_error=logger.error
        )
    """

    lock = Lock()

    def self_(_command: str):
        """

        :param _command:
        """

        try:
            res = check_output(_command, shell=True, stderr=STDOUT)
            with lock:
                call_log_info(f"{_command}:{res.decode('utf-8')}", flag=label_command)
        except CalledProcessError as e:
            with lock:
                call_log_error(f"{_command}:{e.output.decode('utf-8')}", flag=str(e.returncode))
        finally:
            with lock:
                pbar.set_description(f"{_command}")
                pbar.update()

    list_thread: list[Thread] = []
    with tqdm(total=len(command_list)) as pbar:
        for _command in command_list:
            th = Thread(
                target=self_, args=(_command,),
                name=f"th_{_command}", daemon=True,
            )
            list_thread.append(th)
            th.start()

        for th in list_thread:
            th.join()
