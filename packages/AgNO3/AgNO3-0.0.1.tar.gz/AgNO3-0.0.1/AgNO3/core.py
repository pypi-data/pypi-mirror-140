from math import *


print("Welcome to use Package AgNO3")

help_cont = {}
help_cont[0] = 'help : See this help page'
help_cont[1] = 'func1'
help_cont[2] = 'func2'
help_cont[3] = 'func3'
help_cont[4] = 'func4'
help_cont[5] = 'func5'


def help(page=1,lines = 5):
    maxPage = len(help_cont)//lines
    if (page - 1) * lines >= len(help_cont):
        aprint(f'Page Error, check the number : [{1},{maxPage}]')
        return
    print(f"{'=-'*14}= H E L P {'=-'*14}=\n")
    for i in range(lines):
        n = i+lines*(page-1)
        print(f"   {n} - {help_cont[n]}")
    print(f"\n{'=-'*14} page({page}/{maxPage}) {'-='*14}")
    if page < maxPage:print(f'\t\t\thelp({page+1}) for next page')


def func1():
    print('func1')
    
def func2():
    print('func2')
    
def func3():
    print('func3')
    
def func4():
    print('func4')
    
def func5():
    print('func5')
