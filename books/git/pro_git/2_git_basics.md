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

然后Git会为你打开编辑器，让你输入提交message.

如果打开的是vim:

```txt
# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
# On branch master
# Your branch is up-to-date with 'origin/master'.
#
# Changes to be committed:
#	new file:   README
#	modified:   CONTRIBUTING.md
#
~
~
~
".git/COMMIT_EDITMSG" 9L, 283C
```

你可以看到默认的commit message会包含`git status`命令的输出（不过被注释了)，你可以加入一些提示你本次提交干了些什么的信息。

另外你可以使用`-m`来快速提交message:

```shell
$ git commit -m "Story 182: Fix benchmarks for speed"
[master 463dc4f] Story 182: Fix benchmarks for speed
 2 files changed, 2 insertions(+)
 create mode 100644 README
```

你会看到这次commit输出了一些关于它自身的信息：你提交的分支(`master`)，commit的SHA-1 checksum(`463dc4f`)，以及有多少文件被修改，插入/移除了多少行代码。

### Skipping the Staging Area

有时使用staging area麻烦了点。如果你想要跳过staging area，Git提供了一个快捷方式。可以在`git commit`加入`-a`选项让Git自动stage，让你可以跳过`git add`的步骤：

```shell
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

    modified:   CONTRIBUTING.md
no changes added to commit (use "git add" and/or "git commit -a")
$ git commit -a -m "add new beckmarks"
[master 83e38c7] added new benchmarks
 1 file changed, 5 insertions(+), 0 deletions(-)
```

### Removing Files

想要从Git中移除文件，你需要将它从你的tracked文件中移除(或者准确来说是想要把它从你staging area中移除)然后并提交。`git rm`命令就是做这事的，并且它会把文件从你的工作目录中移除。

如果你仅仅把一个文件移除。它会在`git status`输出中显示"Changes not staged for commit"

```shell
$ rm PROJECTS.md
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

        deleted:    PROJECTS.md

no changes added to commit (use "git add" and/or "git commit -a")
```

然后，你使用`git rm`，可以看到文件的stage也被移除了：

```shell
$ git rm PROJECTS.md
rm 'PROJECTS.md'
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    deleted:    PROJECTS.md
```

如果你已经修改了文件并把它加入到了staging area，你必须使用`-f`选项。

另一种情况是，你想要把文件保持在working tree，但是从staging area中移除。换句话说，你想要把文件留在硬盘中，只是不想让Git继续追踪它了。比如有时你忘记把某些文件加入到`.gitignore`，如一个很大的log文件。可以使用`--cached`选项：

`$ git rm --cached README`

你可以将文件，目录，或者glob模式串传入到`git rm`命令：

`$ git rm log/\*.log`

注意`*`前面的反斜杠`\`。

### Moving Files

Git不会显式地追踪文件的移动。如果你将Git中的一个文件重命名，Git的元数据并不会告诉它你将文件重命名了。不够Git很聪明，它会在之后发现文件的移动。

`git mv`命令可以用来为Git的文件重命名：

`$ git mv file_from file_to`

使用一个示例来展示这个命令，你可以看到操作之后的状态变化，Git将它看作是一个renamed文件：

```shell
$ git mv README.mv README
$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    renamed:    README.md -> README
```

不过，它其实和下列一串命令相等：

```shell
$ mv README.md README
$ git rm README.md
$ git add README
```

Git会隐式的算出文件的重命名。所以`git mv`其实是三个命令的一个合成体。另外，你可以使用其它任何方式来将文件重命名，然后在提交之前手动进行`add/rm`.

## 2.3 Git Basics - Viewing the Commit History

### Viewing the Commit History

在你进行几次commit之后，你可以回头看看做了些什么。最基础的一个子命令是`git log`.

我们用一个简单的项目`simplegit`来作实验:

`$ git clone https://github.com/schacon/simplegit-progit`

当你在这个项目中执行`git log`时，你可能会获得如下输出：

```shell
$ git log
commit ca82a6dff817ec66f44342007202690a93763949
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Mon Mar 17 21:52:11 2008 -0700

    changed the version number

commit 085bb3bcb608e1e8451d4b2432f8ecbe6306e7e7
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Sat Mar 15 16:40:33 2008 -0700

    removed unnecessary test

commit a11bef06a3f659402fe7563abf99ad00de2209e6
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Sat Mar 15 10:31:28 2008 -0700

    first commit
```

还有一个强大的选项`-p`或者`--patch`，它可以展示每次提交之间的区别。你可以限制显示的log数量，比如使用`-2`来显示最近的两条：

```shell
$ git log -p -2
commit ca82a6dff817ec66f44342007202690a93763949
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Mon Mar 17 21:52:11 2008 -0700

    changed the version number

diff --git a/Rakefile b/Rakefile
index a874b73..8f94139 100644
--- a/Rakefile
+++ b/Rakefile
@@ -5,7 +5,7 @@ require 'rake/gempackagetask'
 spec = Gem::Specification.new do |s|
     s.platform  =   Gem::Platform::RUBY
     s.name      =   "simplegit"
-    s.version   =   "0.1.0"
+    s.version   =   "0.1.1"
     s.author    =   "Scott Chacon"
     s.email     =   "schacon@gee-mail.com"
     s.summary   =   "A simple gem for using Git in Ruby code."

commit 085bb3bcb608e1e8451d4b2432f8ecbe6306e7e7
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Sat Mar 15 16:40:33 2008 -0700

    removed unnecessary test

diff --git a/lib/simplegit.rb b/lib/simplegit.rb
index a0a60ae..47c6340 100644
--- a/lib/simplegit.rb
+++ b/lib/simplegit.rb
@@ -18,8 +18,3 @@ class SimpleGit
     end

 end
-
-if $0 == __FILE__
-  git = SimpleGit.new
-  puts git.show
-end
```

另外，如果你看每个commit的缩略统计信息，可以使用`--stat`选项：

```shell
$ git log --stat
commit ca82a6dff817ec66f44342007202690a93763949
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Mon Mar 17 21:52:11 2008 -0700

    changed the version number

 Rakefile | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

commit 085bb3bcb608e1e8451d4b2432f8ecbe6306e7e7
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Sat Mar 15 16:40:33 2008 -0700

    removed unnecessary test

 lib/simplegit.rb | 5 -----
 1 file changed, 5 deletions(-)

commit a11bef06a3f659402fe7563abf99ad00de2209e6
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Sat Mar 15 10:31:28 2008 -0700

    first commit

 README           |  6 ++++++
 Rakefile         | 23 +++++++++++++++++++++++
 lib/simplegit.rb | 25 +++++++++++++++++++++++++
 3 files changed, 54 insertions(+)
```

另外还有一个有用的选项是`--pretty`.可以传入`oneline`, `short`，`full`和`fuller`.

```shell
$ git log --pretty=oneline
ca82a6dff817ec66f44342007202690a93763949 changed the version number
085bb3bcb608e1e8451d4b2432f8ecbe6306e7e7 removed unnecessary test
a11bef06a3f659402fe7563abf99ad00de2209e6 first commit
```

最有意思的一个pretty选项是`format`，你可以通过它来修改输出的格式：

```shell
$ git log --pretty=format:"%h - %an, %ar : %s"
ca82a6d - Scott Chacon, 6 years ago : changed the version number
085bb3b - Scott Chacon, 6 years ago : removed unnecessary test
a11bef0 - Scott Chacon, 6 years ago : first commit
```

`oneline`和`format`都可以应用一个选项`--graph`。这个选项可以向你展示一个ASCII graph，代表分支和合并的历史：

```shell
$ git log --pretty=format:"%h %s" --graph
* 2d3acf9 ignore errors from SIGCHLD on trap
*  5e3ee11 Merge branch 'master' of git://github.com/dustin/grit
|\
| * 420eac9 Added a method for getting the current branch.
* | 30e367c timeout code and tests
* | 5a09431 add timeout protection to grit
* | e1193f8 support for heads with slashes in them
|/
* d6016bc require time for xmlschema
*  11d191e Merge branch 'defunkt' into local
```

### Limiting Log Output

使用`--since`和`--until`可以根据时间来限制输出：

`$ git log --since=2.weeks`

## 2.4 Git Basics - Undoing Things

### Undoing Things

在任何时候，你都可能想用撤销一些操作。有若干工具可以进行这种操作，不过小心，不能撤销撤销操作。

第一个unto操作是，修改你的commit(并且替换message)，可以使用`--amend`选项：

`$ git commit --amend`

作为一个例子，如果你commit之后发现你忘记把修改的文件stage并加入到这个commit：

```shell
$ git commit -m "initial commit"
$ git add forgotten_file
$ git commit --amend
```

第二个commit江湖替换之前的一个。

### Unstaging a Staged File

举例来说，你修改了两个文件，像把它们做两次单独的commit，但是不小心输入了`git add *`，怎么将它们中的一个解除stage呢？`git status`提醒了你：

```shell
$ git add *
$ git status
On branch master
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    renamed:    README.md -> README
    modified:   CONTRIBUTING.md
```

你可以看到`git reset HEAD <file>...`可以解除stage：

```shell
$ git reset HEAD CONTRIBUTING.md
Unstaged changes after reset:
M	CONTRIBUTING.md
$ git status
On branch master
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    renamed:    README.md -> README

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

    modified:   CONTRIBUTING.md
```

### Unmodifying a Modified File

如果你发现你不想保持对`CONTRUBUTING.md`文件呢？怎么把它解除修改？将它转换到上一次提交的状态？`git status`同样告诉了你应该怎么做：

```shell
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

    modified:   CONTRIBUTING.md
```

可以使用`git checkout -- <file>...`

```shell
$ git checkout -- CONTRIBUTING.md
$ git status
On branch master
Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

    renamed:    README.md -> README
```

## Git Basics - Working with Remotes

### Working with Remotes

### Showing Your Remotes

想要看你配置了那个remote server，你可以执行`git remote`命令.它会返回remote的简写名称。如果你的仓库来自克隆，你应该至少会看到`origin`:

```shell
$ git clone https://github.com/schacon/ticgit
Cloning into 'ticgit'...
remote: Reusing existing pack: 1857, done.
remote: Total 1857 (delta 0), reused 0 (delta 0)
Receiving objects: 100% (1857/1857), 374.35 KiB | 268.00 KiB/s, done.
Resolving deltas: 100% (772/772), done.
Checking connectivity... done.
$ cd ticgit
$ git remote
origin
```

你可以指定`-v`选项来看Git remote的详细信息，包括URL和用于读或者写：

```shell
$ git remote -v
origin	https://github.com/schacon/ticgit (fetch)
origin	https://github.com/schacon/ticgit (push)
```

如果你有多个remote，它们也会全部列出来：

```shell
$ cd grit
$ git remote -v
bakkdoor  https://github.com/bakkdoor/grit (fetch)
bakkdoor  https://github.com/bakkdoor/grit (push)
cho45     https://github.com/cho45/grit (fetch)
cho45     https://github.com/cho45/grit (push)
defunkt   https://github.com/defunkt/grit (fetch)
defunkt   https://github.com/defunkt/grit (push)
koke      git://github.com/koke/grit.git (fetch)
koke      git://github.com/koke/grit.git (push)
origin    git@github.com:mojombo/grit.git (fetch)
origin    git@github.com:mojombo/grit.git (push)
```

### Adding Remote Repositories

在执行`git clone`的时候，会自动为你添加一个remote - `origin`。想要自定义创建一个remote，可以执行`git remote add <shortname> <url>`:

```shell
$ git remote
origin
$ git remote add pb https://github.com/paulboone/ticgit
$ git remote -v
origin	https://github.com/schacon/ticgit (fetch)
origin	https://github.com/schacon/ticgit (push)
pb	https://github.com/paulboone/ticgit (fetch)
pb	https://github.com/paulboone/ticgit (push)
```

你可以执行`git fetch pb`:

```shell
$ git fetch pb
remote: Counting objects: 43, done.
remote: Compressing objects: 100% (36/36), done.
remote: Total 43 (delta 10), reused 31 (delta 5)
Unpacking objects: 100% (43/43), done.
From https://github.com/paulboone/ticgit
 * [new branch]      master     -> pb/master
 * [new branch]      ticgit     -> pb/ticgit
```

### Fetching and Pulling from Your Remotes

想要从一个remote项目中获取数据：

`$ git fetch <remote>`

请注意，`git fetch`只会把数据下载到你的本地仓库 - 它不会自动合并。

你可以使用`git pull`命令来自动fetch，然后把远程分支合并到当前的分支。

### Pushing to Your Remotes

如果你想要把你本地的项目仓库推送给一个upstream。可以使用一个简单的命令:`push <remote> <branch>`:

`$ git push origin master`

### Inspecting a Remote




