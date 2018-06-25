import datetime, os, re, sys, fnmatch, calendar

TODO_PATH = "todo"
COMPLETED_PATH = "completed"
DELIMITER = '_'
DATE_REGEX = '\d{6}'
FUP_KEY = '_FUP_'
FUP_PATTERN = re.compile('' + FUP_KEY + '(' + DATE_REGEX + ')')
if os.name == 'nt':
    CREATE_PROMPT = "Todo description: (Enter Ctrl+z when done)"
    UPDATE_PROMPT = "Update: (Enter Ctrl+z when done)"
elif os.name == 'posix':
    CREATE_PROMPT = "Todo description: (Enter Ctrl+c? when done)"
    UPDATE_PROMPT = "Update: (Enter Ctrl+c? when done)"


def display_calendar():
    calendar.setfirstweekday(calendar.SUNDAY)
    calendar.prcal(datetime.datetime.today().year)#,2,1,1,3)

def all_todos():
    todos = []
    for (dirpath, dirnames, filenames) in os.walk(TODO_PATH):
        todos.extend(filenames)
        break
    return todos

def fup_todos():
    files = []
    todos = []
    for (dirpath, dirnames, filenames) in os.walk(TODO_PATH):
        files.extend(filenames)
        break
    for filename in files:
        s = FUP_PATTERN.search(filename)
        if (s and s.group(1) <= datetime.datetime.now().strftime("%y%m%d")) or not s:
            todos.append(filename)
    return todos
    
def search_todos():
    files = []
    todos = []
    srch_phrase = raw_input("\nsearch for: ").upper()
    for (dirpath, dirnames, filenames) in os.walk(TODO_PATH):
        files.extend(filenames)
        break
    for filename in files:
        if srch_phrase in filename.upper():
            todos.append(filename)
        else:
            with open(os.path.join(TODO_PATH, filename), "r") as f:
                searchlines = f.readlines()
                for line in searchlines:
                    if srch_phrase in line.upper():
                        todos.append(filename)
                        break
    print("\n\nFound %d todos --- " % len(todos))
    return todos    

def create_todo():
    title = raw_input("todo: ")
    if title != '':
        # handle \ / : * ?
        title = re.sub('[\\/\:\*\?]', '-', title)
        # create todo file
        create_time = datetime.datetime.now().strftime("%y%m%d%H%M%S_")
        fup_time = datetime.datetime.now().strftime("%y%m%d")
        write_todo(create_time+title+FUP_KEY+fup_time, CREATE_PROMPT)

def update_todo(todo_name):
    write_todo(todo_name, UPDATE_PROMPT)
    
def write_todo(todo_name, prompt): 
    target = open(os.path.join(TODO_PATH, todo_name), "a")
    print(prompt)
    buffer = sys.stdin.read()
    if buffer != '':
        target.write(re.sub("\r?\n", "\r\n", buffer))
        target.write("                              " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S\n") )
        target.close()
        set_fup(todo_name)
    else:
        target.close()

def display_todos(todos):
    if len(todos) == 0:
        print ("\nNo FUP to work... Congratulations!")
        return
    print('\n')
    idx = 1
    for todo in todos:
        print("%d  %s  %s\tFUP: %s" % (idx, todo.split(DELIMITER)[0], todo.split(DELIMITER)[1], FUP_PATTERN.search(todo).group(1)))
        idx += 1
        
def clean_screen():
    if os.name == 'nt':
        os.system('cls')  # on windows
    if os.name == 'posix':
        os.system('clear')  # on linux / os x
    
def display_last_updates(todo_name):
    clean_screen()
    print('===== %s =====' % todo_name)
    with open(os.path.join(TODO_PATH, todo_name), "r") as target:
        for line in target:
            print(line)

def set_fup(todo_name):
    fup = raw_input("\nFUP on (yymmdd) or tom/da/nw/close/cal(endar): ")
    if fup == 'close': # close
        with open(os.path.join(TODO_PATH, todo_name), 'a') as target:
            target.write("== Todo is closed ==\n")
            target.write("                              " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S\n") )
        os.renames(os.path.join(TODO_PATH, todo_name), os.path.join(COMPLETED_PATH, todo_name))
    elif fup == '': # later
        fup = datetime.datetime.now().strftime("%y%m%d")
        fup_todo_file(todo_name, fup)
    elif fup == 'tom': # tomorrow
        fup = ( datetime.date.today() + datetime.timedelta(days=1) ).strftime("%y%m%d")
        fup_todo_file(todo_name, fup)
    elif fup == 'da': # the day after
        fup = ( datetime.date.today() + datetime.timedelta(days=2) ).strftime("%y%m%d")
        fup_todo_file(todo_name, fup)
    elif fup == 'nw': # next week
        fup = ( datetime.date.today() + datetime.timedelta(days=7) ).strftime("%y%m%d")
        fup_todo_file(todo_name, fup)
    elif fup == 'cal': # show calendar
        display_calendar()
        set_fup(todo_name)
    elif (not re.match(DATE_REGEX, fup)) or fup < datetime.datetime.now().strftime("%y%m%d"):
        print('\nInvalid FUP date')
        set_fup(todo_name)
    else:
        fup_todo_file(todo_name, fup)
        
def fup_todo_file(todo_name, fup):
    if FUP_PATTERN.search(todo_name):
        new_name = FUP_PATTERN.sub(FUP_KEY + fup, todo_name)
    else:
        new_name = todo_name + FUP_KEY + fup
    os.renames(os.path.join(TODO_PATH, todo_name), os.path.join(TODO_PATH, new_name))
    
# main process
clean_screen()
todos = fup_todos()
while True:
    display_todos(todos)
    task = raw_input("\n\nselect todo # or new/fup/all/s(earch) todos\ncal(endar)/cls/exit: ")
    if task == 'new':
        create_todo()
        todos = fup_todos()
    elif task == 'all':
        todos = all_todos()
    elif task == 'fup':
        todos = fup_todos()
    elif task == 's':
        todos = search_todos()            
    elif task == 'exit' or task == 'quit' or task == 'bye':
        break
    elif task == 'cls':
        clean_screen()
    elif task == 'cal': # show calendar
        display_calendar()
        raw_input("Press Enter to continue...")
    elif task.isdigit() and int(task) <= len(todos):
        todo = todos[int(task) - 1]
        print(todo)
        display_last_updates(todo)
        update_todo(todo)
        todos = fup_todos()
        
