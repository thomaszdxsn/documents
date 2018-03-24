## 安装Vundle

1. 通过git安装`Vundle`

    `git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim`

2. 配置插件:

    将下面的配置函数放在`~/.vimrc`中.

    ```vim
    set nocompatible              " be iMproved, required
        filetype off                  " required

    " set the runtime path to include Vundle and initialize
    set rtp+=~/.vim/bundle/Vundle.vim
    call vundle#begin()
    " alternatively, pass a path where Vundle should install plugins
    "call vundle#begin('~/some/path/here')

    " let Vundle manage Vundle, required
    Plugin 'VundleVim/Vundle.vim'

    " The following are examples of different formats supported.
    " Keep Plugin commands between vundle#begin/end.
    " plugin on GitHub repo
    Plugin 'tpope/vim-fugitive'
    " plugin from http://vim-scripts.org/vim/scripts.html
    " Plugin 'L9'
    " Git plugin not hosted on GitHub
    Plugin 'git://git.wincent.com/command-t.git'
    " git repos on your local machine (i.e. when working on your own plugin)
    Plugin 'file:///home/gmarik/path/to/plugin'
    " The sparkup vim script is in a subdirectory of this repo called vim.
    " Pass the path to set the runtimepath properly.
    Plugin 'rstacruz/sparkup', {'rtp': 'vim/'}
    " Install L9 and avoid a Naming conflict if you've already installed a
    " different version somewhere else.
    " Plugin 'ascenator/L9', {'name': 'newL9'}

    " Dash Plugin
    Plugin 'rizzatti/dash.vim'

    " All of your Plugins must be added before the following line
    call vundle#end()            " required
    filetype plugin indent on    " required
    " To ignore plugin indent changes, instead use:
    "filetype plugin on
    "
    " Brief help
    " :PluginList       - lists configured plugins
    " :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
    " :PluginSearch foo - searches for foo; append `!` to refresh local cache
    " :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
    "
    " see :h vundle for more details or wiki for FAQ
    " Put your non-Plugin stuff after this line
    ```

3. 然后，你需要下载这些插件

    输入vim，进入vim应用，然后使用下面这条vim命令就可以安装插件了

    `:PluginInstall`

## Usage

### :Dash[!]

在指定的docset或所有的docset中搜索一个术语。

```
# Usage
:Dash[!] [TERM] [KEYWORD]

# Examples

# 会根据当前所编辑的文件类型，搜索光标所在位置的单词
:Dash

# 会根据当前所编辑的文件类型，搜索单词"printf"
:Dash printf

# 在'javascript' docset中搜索单词 'setTimeout'
:Dash setTimeout javascript

# 会在所有文档中搜索光标下的单词
:Dash!

# 会在所有文档中搜索'func'
:Dash! func
```

### :DashKeywords[!]

这个命令可以用来展示当前缓存的关键字，或者设置关键字.

```
# Examples

# 展示当前使用的keywords的缓冲list
:DashKeywords

# 设置当前buffer查询优先市有关的docsets，根据给定的顺序
:DashKeywords! backbone underscore javascript
```

