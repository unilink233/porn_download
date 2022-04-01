一个协助下载91porn视频的工具 :)

**傻瓜版教程**

1. 确保你安装了python以及chrome
2. 运行install.bat安装对应的依赖
3. 运行run.bat并粘贴网址.

**详细版教程**

除了调用脚本后手动输入url外, `main.py` 还可以直接接收url进行下载, 例如

```bash
python main.py https://91porn.com/view_video.php?viewkey=123456789
```

`download_91porn.py` 以及 `download_91porny.py` 也可以用类似的方式调用.

下载91时, 会调用selenium来获得uid以便获得下载地址, 程序会自动下载Chrome Webdriver, 但如果Selenium启动Chrome失败, 可以手动下载你目前Chrome版本的Webdriver放入 `chrome_drivers` 文件夹.

[chrome_drivers 下载地址](https://chromedriver.chromium.org/downloads)

91porny为91porn的镜像站, cdn的下载速度更快并且没有cloudflare, 这意味着不需要使用selenium来获得title以及uid, 此外部分视频91porny可以下载更加高清的版本, 你可以更改 `constants.py` 内的 `use_91porny_if_possible` 为 `True` 来使用91porny替代91porn.

