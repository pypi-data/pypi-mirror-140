import os
print("请稍后，正在检查模块.....")
os.system("pip install requests")
os.system("pip install lxml")
os.system("pip install wget")
import wget
import zipfile
import requests
import tkinter
import tkinter.filedialog
from lxml import etree

import time
import re

def coffee_dou_requests_1(m,u,i,p,j):
    start = time.time()
    a = float(0)
    for mima in range(5):
        if m == 'qazplm75124':
            break
        else:
            print("密码错误")
            exit()
    for c in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
        url = u
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
        }
        b = '.jpg'

        response = requests.get(url=url, headers=headers)
        page_text = response.text
        tree = etree.HTML(page_text)
        li_list = tree.xpath(i)
        if not os.path.exists(f'./{p}'):
            os.mkdir(f'./{p}')
        for li in li_list:
            a = a+1
            u = li.xpath(f'{j}')[0]
            img_name = (f'{a}+{b}')
            # img_name = img_name.encode('iso-8859-1').decode('gbk')
            img_data = requests.get(url=u, headers=headers).content
            img_path = f'{p}/' + img_name
            with open(img_path, 'wb') as fp:
                fp.write(img_data)
            print(img_name, u, '爬取完毕！！')
            end = time.time()
            print('总耗时:', end - start)
    print("爬取结束！！！")
    print("感谢您使用该模块，作者为高中生，制作不易，不喜勿喷，使用模块等于接受条例，详细介绍请打开模块根目录查看条例")
    sd = input("如果您所爬取的网站的图片质量不咋滴，可以使用超分辨率模式.如要使用，请输入yes，否则请输入任意键退出")
    if sd == 'yes':
        _4k()
    else:
        exit()
    return a

def coffee_dou_requests_2(m,u,i,p,j,l):
    start = time.time()
    a = float(0)
    for mima in range(5):
        if m == 'qazplm75124':
            break
        else:
            print("密码错误")
            exit('')
    for c in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
        url = u
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
        }
        b = '.jpg'
        response = requests.get(url=url, headers=headers)
        page_text = response.text
        tree = etree.HTML(page_text)
        li_list = tree.xpath(i)
        if not os.path.exists(f'./{p}'):
            os.mkdir(f'./{p}')
        for li in li_list:
            a = a+1
            u = l+li.xpath(f'{j}')[0]
            img_name = (f'{a}+{b}')
            # img_name = img_name.encode('iso-8859-1').decode('gbk')
            img_data = requests.get(url=u, headers=headers).content
            img_path = f'{p}/' + img_name
            with open(img_path, 'wb') as fp:
                fp.write(img_data)
            print(img_name, u, '爬取完毕！！')
            end = time.time()
            print('总耗时:', end - start)

    print("爬取结束！！！")
    sd = input("如果您所爬取的网站的图片质量不咋滴，可以使用超分辨率模式.如要使用，请输入yes，否则请输入任意键退出")
    if sd == 'yes':
        _4k()
    else:
        exit()
    print("感谢您使用该模块，作者为高中生，制作不易，不喜勿喷，使用模块等于接受条例，详细介绍请打开模块根目录查看条例")
    return a


def coffee_dou_example_bizhi(m):
    start = time.time()
    #a = float(0)
    for mima in range(5):
        if m == 'qazplm75124':
            break
        else:
            print("密码错误")
            exit('')
    # a=input("请输入2~10：")
    d=input("您确定要对此页面进行爬虫吗，如果您之前运行了该模块，先前保存的图片会被覆盖掉。如果会覆盖原图，请更改位置重新运行，更改好请输入yes,否则请输入no以退出程序")
    if d=='no':
        exit()
    else:
        for a in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']:
            url = 'https://wallhaven.cc/toplist?' + 'page=' + a
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'
            }
            response = requests.get(url=url, headers=headers)
            page_text = response.text
            tree = etree.HTML(page_text)
            as_href = tree.xpath('//*[@id="thumbs"]/section[1]/ul/li//a/@href')
            if not os.path.exists('./壁纸'):
                os.mkdir('./壁纸')
            for a_href in as_href:
                rsp = requests.get(url=a_href, headers=headers)
                html2 = etree.HTML(rsp.text)
                img_src = html2.xpath("//img[@id='wallpaper']/@src")[0]
                img_name = re.findall('.*-(.*)', img_src)[0]
                content2 = requests.get(url=img_src, headers=headers).content
                with open(file='./壁纸/{}'.format(img_name), mode='wb') as f:
                    f.write(content2)
                print(img_name, '爬取完毕')
            print("第", a, "页爬取完毕")
        print("全部爬取完毕！！")
        end = time.time()
        print('总耗时:', end - start)
        print("感谢您使用该模块，作者为高中生，制作不易，不喜勿喷，使用模块等于接受条例，详细介绍请打开模块根目录查看条例")
    return a
def coffee_dou_example_haokantupian(m):
    start = time.time()
    # a = float(0)
    for mima in range(5):
        if m == 'qazplm75124':
            break
        else:
            print("密码错误")
            exit('')
    # a=input("请输入2~10：")
    d = input("您确定要对此页面进行爬虫吗，如果您之前运行了该模块，先前保存的图片会被覆盖掉。如果会覆盖原图，请更改位置重新运行，更改好请输入yes,否则请输入no以退出程序")
    if d == 'no':
        exit()
    else:
        for a in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
                  '19',
                  '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33']:
            url = 'https://pic.netbian.com/4kmeinv/index_' + a + '.html'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
            }
            response = requests.get(url=url, headers=headers)
            page_text = response.text
            tree = etree.HTML(page_text)
            li_list = tree.xpath('//div[@class="slist"]/ul/li')
            if not os.path.exists('./好看图片'):
                os.mkdir('./好看图片')
            for li in li_list:
                img_src = 'https://pic.netbian.com/' + li.xpath('./a/img/@src')[0]
                img_name = li.xpath('./a/img/@alt')[0] + '.jpg'
                img_name = img_name.encode('iso-8859-1').decode('gbk')
                print(img_name, img_src)
                img_data = requests.get(url=img_src, headers=headers).content
                img_path = '好看图片/' + img_name
                with open(img_path, 'wb') as fp:
                    fp.write(img_data)
                print(img_name, '爬取完毕!!!!')
                a=input('该网站所下载的图片图片质量不咋地，是否运行超分辨率项目,请输入yes运行，或按任意键退出程序')

                if a =='yes':
                    f=input("如果您未下载相关模块，请输入1，如已下载，请输入2")
                    if f=='1':
                        xiazai()
                        w = "C:/Real-ESRGAN/realesrgan-ncnn-vulkan.exe"
                        start = time.time()
                        txt = img_name
                        bb=''
                        # 第二个参数为 1，返回两个参数列表
                        x = txt.split(".")[0:-1]
                        for i in range(len(x) - 1):
                            bb = bb + x[i] + "."
                        h = bb + x[len(x) - 1] + "_4k.png"
                        z = w + " -i " + txt + " -o " + h + " -n realesrgan-x4plus"
                        print("开始处理")
                        print("源文件:", txt)
                        os.system(z)
                        end = time.time()
                        hh = "%.2f" % (end - start)
                        print("----------")
                        print("处理完成")
                        print("")
                        print("输出位置:", h)
                        print("本次耗时:", hh, "s")
                        print("")
                    elif f=='2':
                        w=weizhi(a)
                        start = time.time()
                        txt= img_name
                        bb=''
                        # 第二个参数为 1，返回两个参数列表
                        x = txt.split(".")[0:-1]
                        for i in range(len(x) - 1):
                            bb = bb + x[i] + "."
                        h = bb + x[len(x) - 1] + "_4k.png"
                        z = w+" -i " + txt + " -o " + h + " -n realesrgan-x4plus"
                        print("开始处理")
                        print("源文件:", txt)
                        os.system(z)
                        end = time.time()
                        hh = "%.2f" % (end - start)
                        print("----------")
                        print("处理完成")
                        print("")
                        print("输出位置:", h)
                        print("本次耗时:", hh, "s")
                        print("")
                    else:
                        return f

                else:
                    exit()
        print("感谢您使用该模块，作者为高中生，制作不易，不喜勿喷，使用模块等于接受条例，详细介绍请打开模块根目录查看条例")
def weizhi (a):
    a=input("请输入您的项目地址")
    return a
def _4k():
    txt = tkinter.filedialog.askopenfilename()
    start = time.time()
    bb = ""
    # 第二个参数为 1，返回两个参数列表
    x = txt.split(".")[0:-1]
    for i in range(len(x) - 1):
        bb = bb + x[i] + "."
    h = bb + x[len(x) - 1] + "_4k.png"
    z = "C:/Users/16662/Downloads/Compressed/realesrgan-ncnn-vulkan-20211212-windows/realesrgan-ncnn-vulkan.exe -i " + txt + " -o " + h + " -n realesrgan-x4plus"
    print("开始处理")
    print("源文件:", txt)
    os.system(z)
    end = time.time()
    hh = "%.2f" % (end - start)
    print("----------")
    print("处理完成")
    print("")
    print("输出位置:", h)
    print("本次耗时:", hh, "s")
    print("")
    input("按Enter退出")
    # print(x)
def xiazai ():
    if not os.path.exists('c:/Real-ESRGAN'):
        os.mkdir('c:/Real-ESRGAN')
    print("请稍后，正在下载所需项目.......")
    url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.3.0/realesrgan-ncnn-vulkan-20211212-windows.zip'
    wget.download(url, 'c:/Real-ESRGAN')

    print('下载完成')

    zip_file = zipfile.ZipFile("C:/Real-ESRGAN/realesrgan-ncnn-vulkan-20211212-windows.zip")
    zip_list = zip_file.namelist()  # 得到压缩包里所有文件
    folder_abs = 'C:/Real-ESRGAN/'
    for f in zip_list:
        zip_file.extract(f, folder_abs)  # 循环解压文件到指定目录

    zip_file.close()  # 关闭文件，必须有，释放内存



#u为url
#i为宏观位置
#p为文件名称
#j为具体位置


#使用本程序代表接受以下条款：
#声明：
#本模块完全由作者开发，无借鉴任何帖子
#模块解释所有权归作者所有
#若使用者使用本模块有关违法的行为，并造成严重后果的，作者均不承担相应的法律责任
#感谢您下载此模块，希望能带来美好的体验
#如有打赏，请联系作者
#如有需求，请联系作者
#如有bug或无法使用，请联系作者
#作者邮箱：1666285441@qq.com
#无作者允许，禁止转发或盗用此代码
#如有违反以上原则，作者将交到公安机关，并依法处理
#作者为高中生，制作不易，不喜勿喷
#由于学业繁忙，周一~周五不提供更新服务
#要问作者为什么模块叫咖啡豆请求，因为咖啡豆为作者外号，且作者朋友为此编了个故事集，有兴趣请联系： 3024928063qq.com（jonexi）


#提供以下测试代码使用：
'''
from coffee_dou_requests import coffee_dou_requests
#import asyncio
#u=input("请输入url或url格式:")
#i=input("请输入宏观位置(类型为xpath)：")
#p=input("请输入文件名称：")
#j=input("请输入爬取内容具体位置(类型为xpath)：")
m='qazplm75124'



u = 'https://pic.netbian.com/4kdongman/index_'+'2'+'.html'
i = '//*[@id="main"]/div[3]/ul/li'
p = "图片"
j = './a/img/@src'
o='https://pic.netbian.com'
u=coffee_dou_requests.coffee_dou_requests_2(m,u,i,p,j,o)
print(u)


#密码为：qazplm75124

'''