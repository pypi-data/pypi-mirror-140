from tqdm import trange
from time import sleep
from random import randint
LOGO_CHAR = '''
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
　■■■■■■　　　　■■■　　　　　　■　　　　■■■■　　　
　■　　　　　　　　■　　■■　　　　■■　　　　■　　　■　　
　■　　　　　　　■■　　　■　　　■■■　　　　■　　　■■　
　■　　　　　　　■■　　　　　　　　■■　　　　■　　　　■　
　■　　　　　　　■　■■■　　　　　■■　　　　■　　　　■　
　■■■■■　　　■■　　■■　　　　■■　　　　■　　　　■　
　■　　　　　　　■■　　　■　　　　■■　　　　■　　　　■　
　■　　　　　　　■　　　　■　　　　■■　　　　■　　　　■　
　■　　　　　　　■■　　　■　　　　■■　　　　■　　　■■　
　■　　　　　　　　■　　■■　　　　■■　　　　■　　　■　　
　■　　　　　　　　　■■■　　　　　■■　　　　■■■■　　　
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
'''
print(LOGO_CHAR)
print("Welcome to F61D")

help_cont = {}
help_cont[0] = 'help     : See this help page'
help_cont[1] = 'fuckStar : One Button to fuck Satellite'
help_cont[2] = 'lifeGame : Play the Life Game'
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


def fuckStar():
    print('欢迎使用一键日卫星功能')
    print('请输入要日的卫星编号(可在官网查询):',end='')
    num = input()
    while num == '':
        num = input('请重新输入：')
    for i in trange(randint(1000,2000)):
        for _ in range(66666):
            a = 1
            b = 1
            a,b = b,1
    for i in range(3):
        print('.',end='')
        sleep(0.4)
    print('\n日卫星失败，请重新尝试')
    
def lifeGame():
    import lifeGame
    
def func3():
    print('func3')
    
def func4():
    print('func4')
    
def func5():
    print('func5')

def main():
    lifeGame()

if __name__ == '__main__':
    main()
