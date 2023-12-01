import time
import os
import threading
from typing import List
import uuid
import PyPDF2
import signal
import sys


class AutoJoinPdf:
    list_files: List[str]
    run: bool
    watch_folder: str
    watch_folder_out: str
    new_files: bool
    new_output: str

    watch_folder_thr: threading.Thread

    def __init__(self, base_folder: str = None) -> None:
        self.list_files = []
        self.new_files = False
        self.run = True
        self.new_output = None
        self.watch_folder_thr = None
        self.watch_folder: str = None
        self.watch_folder_out: str = None
        self.set_path(base_folder)

    def set_path(self, path: str) -> None:
        if self.watch_folder_thr is not None:
            self.run = False
            self.watch_folder_thr.join()
            self.watch_folder_thr = None

        if path is None:
            self.watch_folder = None
            self.watch_folder_out = None
        else:
            self.watch_folder = f"{path}/input"
            self.watch_folder_out = f"{path}/output"
            self.watch_folder_thr = threading.Thread(
                target=self.__watch_folder_handler)
            self.run = True
            self.watch_folder_thr.start()

    def __get_new_name(self) -> str:
        return uuid.uuid4().hex

    def __find_state_changed(self, pdf_files: List[str]) -> (List[str], List[str]):

        removed = []
        added = []

        for f in self.list_files:
            if f not in pdf_files:
                removed.append(f)

        for f in pdf_files:
            if f not in self.list_files:
                added.append(f)

        return (added, removed)

    def __watch_folder_handler(self) -> None:
        while self.run:

            if self.__build_inout_folders():
                self.new_output = None
                continue

            existing_pdf_files = [os.path.join(self.watch_folder, f) for f in os.listdir(
                self.watch_folder) if f.endswith(".pdf")]
            self.new_files = False

            added, removed = self.__find_state_changed(existing_pdf_files)

            if len(removed) > 0:
                self.list_files = [
                    f for f in self.list_files if f not in removed]
                self.new_files = True

            if len(added) > 0:
                for f in added:
                    self.list_files.append(f)
                    self.new_files = True

            if self.new_files:
                self.__merge_pdfs(self.list_files)
                self.new_files = False

            time.sleep(1)

    def __clear_output(self):
        files = os.listdir(self.watch_folder_out)
        for f in files:
            os.remove(os.path.join(self.watch_folder_out, f))

    def __merge_pdfs(self, pdf_list):

        self.__clear_output()

        if self.new_output is None:
            self.new_output = os.path.join(
                self.watch_folder_out, f"{self.__get_new_name()}.pdf")

        merger = PyPDF2.PdfMerger()

        for pdf in pdf_list:
            with open(pdf, 'rb') as file:
                merger.append(file)

        with open(self.new_output, 'wb') as output_file:
            merger.write(output_file)

    def __build_inout_folders(self) -> bool:
        created = False
        if not os.path.exists(self.watch_folder):
            os.makedirs(self.watch_folder)
            created = True
        if not os.path.exists(self.watch_folder_out):
            os.makedirs(self.watch_folder_out)
            created = True
        return created

    def terminate(self) -> None:
        self.run = False

    def block_wait(self) -> None:
        while self.run:
            time.sleep(1)


join_pdf = AutoJoinPdf()


def signal_handler(sig, frame):
    join_pdf.terminate()
    print('\n\bTerminating...')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    path = "."

    if len(sys.argv) > 1:
        path = sys.argv[1]

    if (not os.path.exists(path)):
        print(f"invalid path {path}")
        exit(1)

    join_pdf.set_path(path)
    join_pdf.block_wait()
