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

如果你想要查看一个特定remote的更多信息，你可以使用`git remote show <remote>`命令。

```shell
$ git remote show origin
* remote origin
  Fetch URL: https://github.com/schacon/ticgit
  Push  URL: https://github.com/schacon/ticgit
  HEAD branch: master
  Remote branches:
    master                               tracked
    dev-branch                           tracked
  Local branch configured for 'git pull':
    master merges with remote master
  Local ref configured for 'git push':
    master pushes to master (up to date)
```

### Renaming and Removing Remotes

你可以执行`git remote rename`命令来修改一个remote的短名称。例如，你可以把pb改为paul：

```shell
$ git remote rename pb paul
$ git remote
origin
paul
```

如果你出于某些原因想要移除一个remote，可以使用`git remote rm/remove`命令：

```shell
$ git remote remove paul
$ git remote
origin
```

## Git Basics - Tagging

### Tagging

很多数版本控制工具一样，你可以使用tag标记一些commit。

#### Listing Your Tags

想要直接列出Git仓库的tag清单。只需要输入`git tag`就可以了：

```shell
$ git tag
v0.1
v0.3
```

这个commit顺序是以字母表为顺序的；不过顺序其实并不重要。

你也可以根据一个特定的规则模式来搜索tag。如果一个Git仓库，包含超过500个tag，如果你只对1.8.5系列感兴趣：

```shell
$ git tag -l "v1.8.5*"
v1.8.5
v1.8.5-rc0
v1.8.5-rc1
v1.8.5-rc2
v1.8.5-rc3
v1.8.5.1
v1.8.5.2
v1.8.5.3
v1.8.5.4
v1.8.5.5
```

使用通配符列tag清单需要使用`-l`或者`--list`选项。

### Creating Tags

Git支持两种类型的tag：轻量级(lightweight)和标记型(annotated)。

轻量级标签很像不作改动的分支 -- 它只是一个特定commit的指针。

标记型标签，将会把所有的对象都存储到Git数据库中。它们已经被checksum了；包含tagger名称，email和日期；以及一个tagging message；可以使用GNU Privacy Guard来进行签名和验证。一般推荐使用标记型标签，不过如果你只想要一个临时标签，那么轻量级标签更适合。

### Annotated Tags

在Git中创建一个标记型标签很简单。最简单的方式是执行`git tag`命令的时候加入`-a`选项：

```shell
$ git tag -a v1.4 -m "my version 1.4"
$ git tag
v0.1
v1.3
v1.4
```

`-m`选项可以指定tagging message，它会存储到这个tag中。

你可以使用`git show`命令来展示一个tag相关的信息:

```shell
$ git show v1.4
tag v1.4
Tagger: Ben Straub <ben@straub.cc>
Date:   Sat May 3 20:19:12 2014 -0700

my version 1.4

commit ca82a6dff817ec66f44342007202690a93763949
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Mon Mar 17 21:52:11 2008 -0700

    changed the version number
```

### Lightweight Tags

想要创建一个轻量级标签，只需要传入标签名称就行了，不要传入`-a`, `-s`或`-m`任一的一个选项：

```shell
$ git tag v1.4-1w
$ git tag
v0.1
v1.3
v1.4
v1.4-lw
v1.5
```

这次，再使用`git show`命令不会展示额外的tag信息。

```shell
$ git show v1.4-lw
commit ca82a6dff817ec66f44342007202690a93763949
Author: Scott Chacon <schacon@gee-mail.com>
Date:   Mon Mar 17 21:52:11 2008 -0700

    changed the version number
```

### Tagger Later

假设你的commit历史如下：

```shell
$ git log --pretty=oneline
15027957951b64cf874c3557a0f3547bd83b3ff6 Merge branch 'experiment'
a6b4c97498bd301d84096da251c98a07c7723e65 beginning write support
0d52aaab4479697da7686c15f77a3d64d9165190 one more thing
6d52a271eda8725415634dd79daabbc4d9b6008e Merge branch 'experiment'
0b7434d86859cc7b8c3d5e1dddfed66ff742fcbc added a commit function
4682c3261057305bdd616e23b64b0857d832627b added a todo file
166ae0c4d3f420721acbb115cc33848dfcc2121a started write support
9fceb02d0ae598e95dc970b74767f19372d61af8 updated rakefile
964f16d36dfccde844893cac5b347e7b3d44abbc commit the todo
8a5cbc430f1a9c3d00faaeffd07798508422908a updated readme
```

现在，假设你忘记项目中的v1.2标签需要标记"updated rakefile"commit。你可以时候加入这个标签，只要把这个commit的checksum(或者一部分)加入到命令末尾即可：

`$ git tag -a v1.2 9fceb02`

现在可以看到你新加入的标签了：

```shell
$ git tag
v0.1
v1.2
v1.3
v1.4
v1.4-lw
v1.5

$ git show v1.2
tag v1.2
Tagger: Scott Chacon <schacon@gee-mail.com>
Date:   Mon Feb 9 15:32:16 2009 -0800

version 1.2
commit 9fceb02d0ae598e95dc970b74767f19372d61af8
Author: Magnus Chacon <mchacon@gee-mail.com>
Date:   Sun Apr 27 20:43:35 2008 -0700

    updated rakefile
...
```

### Sharing Tags

默认情况下，`git push`命令不会把tag移交给远程服务器。你需要显式指定把tag推送到服务器，就像分享远程分支一样：`git push origin <tagname>`

```shell
$ git push origin v1.5
Counting objects: 14, done.
Delta compression using up to 8 threads.
Compressing objects: 100% (12/12), done.
Writing objects: 100% (14/14), 2.05 KiB | 0 bytes/s, done.
Total 14 (delta 3), reused 0 (delta 0)
To git@github.com:schacon/simplegit.git
 * [new tag]         v1.5 -> v1.5
```

如果你想要一次性推送所有的tag，可以使用`--tags`选项：

```shell
$ git push origin --tags
$ git push origin --tags
Counting objects: 1, done.
Writing objects: 100% (1/1), 160 bytes | 0 bytes/s, done.
Total 1 (delta 0), reused 0 (delta 0)
To git@github.com:schacon/simplegit.git
 * [new tag]         v1.4 -> v1.4
 * [new tag]         v1.4-lw -> v1.4-lw
```

### Checking out Tags

如果你想要检查一个tag的文件，你可以使用`git checkout`，它会让你的仓库出于"detached HAED"状态：

```shell
$ git checkout 2.0.0
Note: checking out '2.0.0'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by performing another checkout.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -b with the checkout command again. Example:

  git checkout -b <new-branch>

HEAD is now at 99ada87... Merge pull request #89 from schacon/appendix-final

$ git checkout 2.0-beta-0.1
Previous HEAD position was 99ada87... Merge pull request #89 from schacon/appendix-final
HEAD is now at df3f601... add atlas.json and cover image
```

在"detached HEAD"状态中。如果你修改了一些文件并commit，这个标签仍然会存在，不过这个commit不会属于任何分支，也不可获取，除非指定这个commit hash。

## 2.7 Git Basics - Git Aliases

### Git Aliases

在我们结束这个章节之前，再介绍一个方便的工具: `aliases`.

如果你只输入了命令的一部分，Git不会为你自动补全。如果你不想完整的输入整个命令，你可以使用`git config`来设置alias：

```shell
$ git config --global alias.co checkout
$ git config --global alias.br branch
$ git config --global alias.ci commit
$ git config --global alias.st status
```

显而易见，可以看到上面例子把一些命令进行了简化。

这个技术也可以为你创建复合命令：

`$ git conifg --global alias.unstage 'reset HEAD --'`

然后下面两个命令就相等了：

```shell
$ git unstage fileA
$ git reset HEAD -- fileA
```

比如可以加入一个`last`命令，让你简单的看最后一个commit：

`$ git config --global alias.last 'log -1 HEAD'`

使用它：

```shell
$ git last
commit 66938dae3329c7aebe598c2246a8e6af90d04646
Author: Josh Goebel <dreamer3@example.com>
Date:   Tue Aug 26 19:48:51 2008 +0800

    test for current head

    Signed-off-by: Scott Chacon <schacon@example.com>
```

## 2.8 Git Basics - Summary

### Summary

在这个章节我们教你克隆一个仓库，创建改动，staging以及提交这些commits，以及可以查看所有commit的历史。

下一个章节，我们会开始讲Git的杀手级特性：分支模型(Branch Model).