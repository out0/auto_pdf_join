# auto_pdf_join
Automatic folder watcher for pdf joining

install requirements

pip3 -r requirements.txt

then run:

python3 ./auto_join.py <base path (optional, if not it will use the current folder)>

it creates two folders: input, output

as pdfs are added to input, it creates and updates an output pdf file joining them.

This is useful for maintaining a docker for easly joining documents. You can simply map the two folders into a NFS or Samba and
to automate this tedious task