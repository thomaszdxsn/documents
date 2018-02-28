# Git Branching - Branches in a Nutshell

几乎每个版本控制工具都支持某种形式的分支管理。

为什么很多人说Git的branch是杀手级特性？因为它的速度快！

### Branches in a Nutshell

想要理解Git怎么进行分支的，首先你需要明白Git怎么存储数据的。

之前说到过，Git并不把所有文件的改动都存储起来，而是把它们作为一系列快照来存储。

在你进行一次commit之后，Git会存储这个commit对象，它包含你staged内容快照的指针。

其实是一个链表，除了初始的commit，其它commit都有父节点，有时会有多个父节点。

假设你的目录中有三个文件，你把它们都stage并commit：

```shell
$ git add README test.rb LICENSE
$ git commit -m 'The initial commit of my project'
```

在你进行commit之后，Git会检查每个子目录的checksum(在这个例子中只有根目录)并且把这些树对象存储到Git仓库中。Git然后会创建一个commit对象用来存储元数据和指向根目录的指针。让你可以在需要的时候重新创建这个快照。

你的Git仓库包含5个对象：三个文件的blob内容，一个列出目录内容的树用来指定每个blob对应的文件名，以及一个代表指向root tree和所有commit元数据的指针的commit。

如果你做了一些改动然后再次提交，下一个commit会包含一个紧随其后的指针(它指向的tree的父节点是root tree)。

而**分支**可以说就是一个这样的指针，不过更加轻量级并且可移动。Git中默认的分支名为`master`.

### Creating a New Branch

在你创建分支的时候发生了什么？它会为你创建一个新的指针，让你可以随时移动：

`$ git branch testing`

这个命令会创建一个指针指向你当前commit的位置。

Git怎么知道你在哪个分支上面呢？它有一个特殊指针叫做`HEAD`。这个指针代表你当前处于的本地分支。现在你仍然出于`master`上面，因为上面的命令只是创建了一个分支，并没有转换到这个分支上面。

你可以使用`git log --decorate`命令来查看你当前分支的指针和指向：

```shell
$ git log --oneline --decorate
f30ab (HEAD -> master, testing) add feature #32 - ability to add new formats to the central interface
34ac2 Fixed bug #1328 - stack overflow under certain conditions
98ca9 The initial commit of my project
```

### Switching Branches

想要切换到一个现存的分支上，可以使用`git checkout`命令：

`$ git checkout testing`

这个命令会把HEAD指向testing分支。

分支到底有什么用呢？

让我们在这个分支上面再进行一个commit：

```shell
$ vim test.rb
$ git commit -a -m "made a change"
```

这就有意思了，现在你的testing分支和master不一样了。

让我们在master也做一次commit：

```shell
$ git checkout master
$ vim test.rb
$ git commit -a -m "made other changes"
```

你可以使用`git log`命令来看commit历史：

```shell
$ git log --oneline --decorate --graph --all
* c2b9e (HEAD, master) made other changes   # master的commit
| * 87ab2 (testing) made a change   # testing的commit
|/
* f30ab add feature #32 - ability to add new formats to the
* 34ac2 fixed bug #1328 - stack overflow under certain conditions
* 98ca9 initial commit of my project
```

## 3.2 Git Branching - Basic Branching and Merging

### Basic Branching

使用`git checkout -b`可以方便的创建一个分支并切换到这个分支上面：

```shell
$ git checkout -b iss53
Switched to a new branch "iss53"
```

它等同于：

```shell
$ git branch iss53
$ git checkout iss53
```

你需要提交一些commit：

```shell
$ vim index.html
$ git commit -a -m 'added a newer footer [issue 53]'
```

提交完之后，你可以切换回`master`分支了:

```shell
$ git checkout master
Switching to branch 'master'
```

然后你需要创建一个hotfix：

```shell
$ git checkout -b hotfix
Switched to a new branch 'hotfix'
$ vim index.html
$ git commit -a -m "fixed the broken email address"
[hotfix 1fb7853] fixed the broken email address
 1 file changed, 2 insertions(+)
```

然后你应该运行测试，看hotfix是否正常，然后将`hotfix`合并到`master`中：

```shell
$ git checkout master
$ git merge hotfix
Updating f42c576..3a0874c
Fast-forward
 index.html | 2 ++
 1 file changed, 2 insertions(+)
```

你会注意到merge中出现"fast-forward"的字样.因为hotfix分支的commit在master的commit前面，Git只需把指针往前挪就行了。因为在合并的时候没有分歧，所以它叫做"fast-forward".

因为你不再需要`hotfix`分支了，只需要删除它就好了：

```shell
$ git branch -d hotfix
Deleted branch hotfix (3a0874c).
```

现在回到`iss53`：

```shell
$ git checkout iss53
Switched to branch "iss53"
$ vim index.html
$ git commit -a -m 'finished the new footer [issue 53]'
[iss53 ad82d7a] finished the new footer [issue 53]
1 file changed, 1 insertion(+)
```

### Basic Merging

假设你觉得iss53可以合并到`master`分支了：

```shell
$ git checkout master
Switching to branch 'master'
$ git merge iss53
Merge made by the 'recursive' strategy.
index.html |    1 +
1 file changed, 1 insertion(+)
```

这种合并策略，会有Git来决定两个分支的一个共同祖先，然后创建一个新的合并commit；

现在`iss53`分支也可以删除了：

`$ git branch -d iss53`

### Basic Merge Conflicts

有时，合并过程可能不是那么顺序。比如你在hotfix修改的文件和master有冲突：

```shell
$ git merge iss53
Auto-merging index.html
CONFLICT (content): Merge conflict in index.html
Automatic merge failed; fix conflicts and then commit the result.
```

Git不会再自动创建一个新的合并commit，它需要暂停下来等待你解决冲突。如果你想知道合并冲突时哪些文件没有被合并，你可以执行`git status`:

```shell
$ git status
On branch master
You have unmerged paths.
  (fix conflicts and run "git commit")

Unmerged paths:
  (use "git add <file>..." to mark resolution)

    both modified:      index.html

no changes added to commit (use "git add" and/or "git commit -a")
```

出现合并冲突的时候。Git会为这些文件增加一些标记，你需要手动打开它们并解决冲突：

```txt
<<<<<<< HEAD:index.html
<div id="footer">contact : email.support@github.com</div>
=======
<div id="footer">
 please contact us at support@github.com
</div>
>>>>>>> iss53:index.html
```

这意味着HEAD(指master，也就是你想要合并进入的分支)是上方的块(`======`之上)， 而`iss53`的改动在=====下面。怎么解决冲突完全取决于你。

在你解决冲突之后，再执行`git add`把文件标记为已解决。

如果你想要使用一些图形工具来解决合并冲突，你可以使用`git mergetool`:

```shell
$ git mergetool

This message is displayed because 'merge.tool' is not configured.
See 'git mergetool --tool-help' or 'git help config' for more details.
'git mergetool' will now attempt to use one of the following tools:
opendiff kdiff3 tkdiff xxdiff meld tortoisemerge gvimdiff diffuse diffmerge ecmerge p4merge araxis bc3 codecompare vimdiff emerge
Merging:
index.html

Normal merge conflict for 'index.html':
  {local}: modified file
  {remote}: modified file
Hit return to start merge resolution tool (opendiff):
```

合并成功后，再次运行`git status`:

```shell
$ git status
On branch master
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes to be committed:

    modified:   index.html
```

最后，你需要使用`git commit`来结束这次合并。

```shell
Merge branch 'iss53'

Conflicts:
    index.html
#
# It looks like you may be committing a merge.
# If this is not correct, please remove the file
#	.git/MERGE_HEAD
# and try again.


# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
# On branch master
# All conflicts fixed but you are still merging.
#
# Changes to be committed:
#	modified:   index.html
#
```

## 3.3 Git Branching - Branch Management

你已经知道如何创建，合并以及删除分支。现在让我们看一些分支管理的工具。

直接执行`git branch`，会看到当前所有的分支：

```shell
$ git branch
  iss53
* master
  testing
```

`*`号代表你当前激活的分支。想要看到每个分支的最后一个commit，可以使用`-v`选项：

```shell
$ git branch -v
  iss53   93b412c fix javascript issue
* master  7a98805 Merge branch 'iss53'
  testing 782fd34 add scott to the author list in the readmes
```

而`--merged`和`--no-merged`选项可以筛选一个分支是否被合并：

```shell
$ git branch --merged
  iss53
* master

$ git branch --no-merged
  testing
```

如果你想删除一个未合并的分支，Git会警告你。如果你确定要删除，那么需要使用`-D`选项：

```shell
$ git branch -d testing
error: The branch 'testing' is not fully merged.
If you are sure you want to delete it, run 'git branch -D testing'.
```

> 注意
>
>> `--merged`和`--no-merged`是有参照物的，是查询任何是否和本分支进行合并的其它分支。如果你在一个分支想查询其它分支的合并情况，可以在之后传入分支名。
>>
>> ```shell
>> $ git checkout testing
>> $ git branch --no-merged master
>>   topicA
>>   featureB
>> ```

## 3.4 Git Branching - Branching Workflows

### Long-Running Branches

Git使用简单的three-way合并.

### Topic Branches

## 3.5 Git Branching - Remote Branches

远程分支的格式为`<remote>/<branch>`，比如你本地有一个分支叫做`iss53`，远程分支就是`origin/iss53`.








