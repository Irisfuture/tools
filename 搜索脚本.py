import os
import fnmatch
import re
from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, VERTICAL, HORIZONTAL, END
from docx import Document   # 用于处理 .docx 文件
import win32com.client as win32   # 用于处理 .doc 文件

def search_files(directory, pattern, search_text):
    results = []
    p = r'\.('+pattern+')$'
    pattern_re = re.compile(p)
    for root, dirs, files in os.walk(directory):
        # print('文件夹',files,pattern)
        matched_files = [f for f in files if pattern_re.search(f) and not f.startswith('~$')] # 不显示临时文件（通常以 ~$ 开头）
        for filename in matched_files:
            filepath = os.path.join(root, filename)
            try:
                if filename.endswith('.txt'):
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # print(results)
                elif filename.endswith('.py'):
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                elif filename.endswith('.doc'):
                    content = convert_doc_to_text(os.path.join(root, filename))
                elif filename.endswith('.docx'):
                    content = convert_docx_to_text(os.path.join(root, filename))
                
                matches = re.finditer(re.escape(search_text), content, re.IGNORECASE)
                for match in matches:
                    start = max(0, match.start() - 90)
                    end = min(len(content), match.end() + 90)
                    snippet = content[start:end]
                    results.append((filepath, snippet))
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    return results

def convert_doc_to_text(doc_path):
    word = win32.Dispatch('Word.Application')
    word.Visible = False
    doc = word.Documents.Open(doc_path)
    text = doc.Range().Text
    doc.Close()
    word.Quit()
    return text

def convert_docx_to_text(docx_path):
    doc = Document(docx_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def search_button_clicked():
    search_text = entry_search.get()
    results_text.delete('1.0', END)
    results_text.tag_configure("highlight", foreground="blue4", font=("TkDefaultFont", 12, "bold"))
    results = search_files(directory='./', pattern='py|doc|docx|txt', search_text=search_text)
    for i, (filepath, snippet) in enumerate(results, start=1):
        results_text.insert(END, f"{i}. File: {filepath}\n")
        last_end = 0
        for match in re.finditer(re.escape(search_text), snippet, re.IGNORECASE):
            results_text.insert(END, snippet[last_end:match.start()])
            start_pos = results_text.index("end-1c")
            results_text.insert(END, snippet[match.start():match.end()])
            end_pos = results_text.index("end-1c")
            results_text.tag_add("highlight", start_pos,end_pos)
            last_end = match.end()
        results_text.insert(END, snippet[last_end:])
        results_text.insert(END, "\n\n~~~~\n")

# GUI Setup
root = Tk()
root.title("File Search Utility")

Label(root, text="Enter search term:").pack()
entry_search = Entry(root, width=50)
entry_search.pack(pady=5)

Button(root, text="Search", command=search_button_clicked).pack()

results_text = Text(root, wrap='word')
results_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)

scrollbar_vertical = Scrollbar(root, orient=VERTICAL, command=results_text.yview)
scrollbar_vertical.pack(side='right', fill='y')

scrollbar_horizontal = Scrollbar(root, orient=HORIZONTAL, command=results_text.xview)
scrollbar_horizontal.pack(side='bottom', fill='x')

results_text.config(yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)

root.mainloop()