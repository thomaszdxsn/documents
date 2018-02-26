# Git Basics

## 2.1 Git Basics - Getting a Git Repository

在本章你会学到Git的基本用法，在学完之后，你应该知道怎么初始化一个Git仓库，怎么开始/停止追踪一个文件，以及stage和commit的改动。

### Getting a Git Repository

一般你有两种途径获得一个Git仓库：

1. 你可以将一个目前还没有被版本控制的本地目录转换为一个Git仓库
2. 你可以从其它地方拷贝一份Git仓库

### Initializing a Repository in an Existing Directory

```shell
$ cd myproject
$ git init
```

如果这个目录已经有文件了，你希望最终所有的c文件并提交：

```shell
$ git add *.c
$ git add LICENSE
$ git commit -m "initial project version"
```

### Cloning an Existing Repository

语法: `git clone <url>`

## 2.2 Git Basics - Recording Changes to the Repository

### Recording Changes to the Repository

项目目录中的文件按git是否追踪来划分可以分为tracked，untracked.tracked文件是最后一次快照的文件；它可以是unmodified,modified或者staged状态。简而言之，tracked文件就是Git所知道的文件。

untracked文件是另一种东西了 - 工作目录中任何既不存在于最后一次快照也不存在于staging area的文件都是untracked文件。

### Checking the Status of Your Files

可以使用`git status`命令来查看当前文件的状态。

让我们加入一个README文件，然后再看一下状态：

```shell
$ echo "My Project" > README
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Untracked files:
  (use "git add <file>..." to include in what will be committed)

    README
    
nothing added to commit but untracked files present (use "git add" to track)
```

### Tracking New Files

想要开始追踪一个文件，你需要使用`git add`命令。

`$ git add README`

你可以再次执行`git status`命令：

```shell
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    new file:   README
```

### Staging Modified Files

让我们修改一个已经追踪的文件，把之前的文件名修改为`CONTRIBUTING.md`，然后再次运行`git status`:

```shell
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    new file:   README

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

    modified:   CONTRIBUTING.md
```

这个`CONTRIBUTING.md`文件出现在"Changes not staged for commit"下方 -- 说明这个文件被发现已经改动过了，但是还没有进入staged状态。想要staged它，你需要使用`git add`，`git add`是一个多用途命令 - 你可以用它来追踪文件，stage文件，以及一些类似解决合并冲突的事情。

```shell
$ git add CONTRIBUTING.md
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    new file:   README
    modified:   CONTRIBUTING.md
```

所有文件都出于staged状态，为你的下一次提交作准备。假设你在提交前还想对这个文件作一些小改动：

```shell
$ vim CONTRIBUTING.md
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    new file:   README
    modified:   CONTRIBUTING.md

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

    modified:   CONTRIBUTING.md
```

你会发现：CONTRUBUTING同时出现在staged和unstaged状态！stage状态的CONTRIBUTING实际上记的是你上一次执行`git add`时的内容。你需要再次执行一次`git add`.

```shell
$ git add CONTRIBUTING.md
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    new file:   README
    modified:   CONTRIBUTING.md
```

### Short Status

`git status`的输出看起来有些复杂。Git同样有一种间断的status表述方法，你可以使用`git status -s`或者`git status --short`来输出:

```shell
$ git status -s
  M README
MM Rakefile
A  lib/git.rb
M  lib/simplegit.rb
?? LICENSE.txt
```

新文件以`??`开头，加入到staging area的新文件以`A`开头，已修改文件以`M`开头。

### Ignoring Files

有些文件你并不想被Git最终，但是这让你很难使用通配符取add文件。Git提供了一种机制，可以将不想追踪的文件加入到`.gitignore`文件中：

```shell
$ cat .gitignore
*.[oa]
*~
```

`.gitignore`中模式的匹配规则为：

- 空白行和以`#`开始的行会被忽略
- 使用标准的glob模式匹配，并且会对整个目录结构进行递归匹配
- 你可以对一个规则以`/`开头，可以避免递归匹配
- 你可以对一个规则以`/`结尾，代表它是一个目录
- 你可以使用一个`!`来否定一个规则(代表例外情况)

下面是一个`.gitignore`文件的示例：

```txt
# 忽略所有 .a 文件
*.a

# 虽然你上边忽略了所有`.a`文件，这里仍然会追踪`lib.a`
lib.a

# 只忽略当前文件夹的TODO文件，不会忽略子文件夹的TODO文件
/TODO

# 忽略`build/`目录下的所有文件
build/

# 忽略`doc/notes.txt`文件，但不忽略`doc/server/arch.txt`文件
doc/*.txt

# 忽略`doc/`目录以及它的子目录下的所有pdf文件
doc/**/*.pdf
```

### Viewing Your Staged and Unstaged Changes

如果`git status`输出的结果对你来说还是太模糊的话 -- 比如你需要知道到底变了什么，你可以使用`git diff`命令。

让我们回到你将`README`文件修改为`CONTRIBUTING.md`但还没有staging的时候。运行`git status`你会看到：

```shell
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    modified:   README

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

    modified:   CONTRIBUTING.md
```

想要看哪些还没有staged的变动，可以输入`git diff`命令:

```shell
$ git diff
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 8ebb991..643e24f 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -65,7 +65,8 @@ branch directly, things can get messy.
 Please include a nice description of your changes when you submit your PR;
 if we have to read the whole diff to figure out why you're contributing
 in the first place, you're less likely to get feedback and have your change
-merged in.
+merged in. Also, split your changes into comprehensive chunks if your patch is
+longer than a dozen lines.

 If you are starting to work on a particular area, feel free to submit a PR
 that highlights your work in progress (and note in the PR title that it's
```

如果你想知道下一次commit之后的staged，可以输入`git diff --staged`:

```shell
$ git diff --staged
diff --git a/README b/README
new file mode 100644
index 0000000..03902a1
--- /dev/null
+++ b/README
@@ -0,0 +1 @@
+My Project
```

请注意，**`git diff`不会显示所有文件的改动，它只会显示还没有staged的改动**。

另一个例子：

```shell
$ git add CONTRIBUTING.md
$ echo '# test line' >> CONTRIBUTING.md
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    modified:   CONTRIBUTING.md

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

    modified:   CONTRIBUTING.md
```

你可以使用`git diff`看到仍然是unstaged的内容：

```shell
$ git diff
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 643e24f..87f08c8 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -119,3 +119,4 @@ at the
 ## Starter Projects

 See our [projects list](https://github.com/libgit2/libgit2/blob/development/PROJECTS.md).
+# test line
```

使用`git diff --cached`(`--cached`和`--staged`是同义词)可以看到哪些内容已经staged：

```shell
$ git diff --cached
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 8ebb991..643e24f 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -65,7 +65,8 @@ branch directly, things can get messy.
 Please include a nice description of your changes when you submit your PR;
 if we have to read the whole diff to figure out why you're contributing
 in the first place, you're less likely to get feedback and have your change
-merged in.
+merged in. Also, split your changes into comprehensive chunks if your patch is
+longer than a dozen lines.

 If you are starting to work on a particular area, feel free to submit a PR
 that highlights your work in progress (and note in the PR title that it's
```

### Committing Your Changes

现在按照你的想法建立起来staging area，你可以提交你的改动。

最简单的提交方式就是:

`$ git commit`

