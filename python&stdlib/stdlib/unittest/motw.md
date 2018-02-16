# uniitest -- Automated Testing Framework

*用途:自动化测试框架*

Python的`uniitest`是基于Kent Beck & Erich Gamma设计的XUnit框架来实现的。在很多编程语言中都有关相关实现比如C，Perl，Java和Smalltalk。`uniittest`实现了fixture，test suite，test runner。

## Basic Test Structure

`unittest`定义的测试包含两个部分：用来管理测试依赖的代码(叫做`fixture`)，以及测试代码本身。每个测试都是通过继承`TestCase`来创建的，可以继承它并重写一些方法。

### unitest_simple.py

```python
# unittest_simple.py

import unittest


class SimplisticTest(unittest.TestCase):

    def test(self):
        a = 'a'
        b = 'a'
        self.assertEqual(a, b)
```

## Running Tests

可以通过命令行接口来自动运行testcase。

```shell
$ python3 -m unittest unittest_simple.py

.
----------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

输出中包含了test总耗时，并且包含了状态指标来代表每个test("."代表这个test通过)。如果想要更详细的输出，建议使用`-v`选项。

```shell
$ python3 -m unittest -v unittest_simple.py

test (unittest_simple.SimplisticTest) ... ok

----------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

## Test Outcomes

Test拥有三种可能的结果:

结果 | 描述
-- | --
ok | 这个测试通过.
FAIL | 这个测试没有通过，将会抛出一个`AssertionError`.
ERROR | 这个测试发生了错误，即抛出了不是`AssertionError`的异常.

### unittest_outcomes.py

```python
# unittest_outcomes.py

import unittest


class OutcomesTest(unittest.TestCase):

    def testPass(self):
        return

    def testFail(self):
        self.assertTrue(False)

    def testError(self):
        raise RuntimeError('Test error!')
```

在一个测试fail或者生成一个error的时候，输出中将会包含traceback.

```shell
$ python3 -m unittest unittest_outcomes.py

EF.
================================================================
ERROR: testError (unittest_outcomes.OutcomesTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_outcomes.py", line 18, in testError
    raise RuntimeError('Test error!')
RuntimeError: Test error!

================================================================
FAIL: testFail (unittest_outcomes.OutcomesTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_outcomes.py", line 15, in testFail
    self.assertFalse(True)
AssertionError: True is not false

----------------------------------------------------------------
Ran 3 tests in 0.001s

FAILED (failures=1, errors=1)
```

### unittest_failwithmessage.py

在之前的例子中，`testFail()`将会fail，再failure code的旁边还会显示traceback。用户也可以自定义一些错误消息.

```python
# unittest_failwithmessage.py

import unittest


class FailureMessageTest(unittest.TestCase):

    def testFail(self):
        self.assertFalse(True, 'failure message goes here')
```

输出:

```shell
$ python3 -m unittest -v unittest_failwithmessage.py

testFail (unittest_failwithmessage.FailureMessageTest) ... FAIL

================================================================
FAIL: testFail (unittest_failwithmessage.FailureMessageTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_failwithmessage.py", line 12, in testFail
    self.assertFalse(True, 'failure message goes here')
AssertionError: True is not false : failure message goes here

----------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

## Asserting Truth

### unittest_truth.py

多数测试都是某些条件下的正向断言。有两种不同的方式可以进行truth测试。

```python
# unittest_truth.py

import unittest


class TruthTest(unittest.TestCase):
    
    def testAssertTrue(self):
        self.assertTrue(True)

    def testAssertFalse(self):
        self.assertFalse(False)
```

输出:

```shell
$ python3 -m unittest -v unittest_truth.py

testAssertFalse (unittest_truth.TruthTest) ... ok
testAssertTrue (unittest_truth.TruthTest) ... ok

----------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

## Testing Equality

### unittest_equality.py

在一些特殊的情况下，可以使用`unittest`的方法来判断两个值的相等性。

```python
# unittest_equality.py

import unittest


class EqualityTest(unittest.TestCase):
    
    def testExpectEqual(self):
        self.assertEqual(1, 3 - 2)

    def testExpectEqualFails(self):
        self.assertEqual(2, 3 -2 )

    def testExpectNotEqual(self):
        self.assertNotEqual(2, 3 - 2)

    def testExpectNotEqualFails(self):
        self.assertNotEqual(1, 3 - 2)
```

输出:

```shell
$ python3 -m unittest -v unittest_equality.py

testExpectEqual (unittest_equality.EqualityTest) ... ok
testExpectEqualFails (unittest_equality.EqualityTest) ... FAIL
testExpectNotEqual (unittest_equality.EqualityTest) ... ok
testExpectNotEqualFails (unittest_equality.EqualityTest) ...
FAIL

================================================================
FAIL: testExpectEqualFails (unittest_equality.EqualityTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_equality.py", line 15, in
testExpectEqualFails
    self.assertEqual(2, 3 - 2)
AssertionError: 2 != 1

================================================================
FAIL: testExpectNotEqualFails (unittest_equality.EqualityTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_equality.py", line 21, in
testExpectNotEqualFails
    self.assertNotEqual(1, 3 - 2)
AssertionError: 1 == 1

----------------------------------------------------------------
Ran 4 tests in 0.001s

FAILED (failures=2)
```

## Almost Equal?

### unittest_almostequal.py

除了严格的相等性断言，可以使用`assertAlmostEqual()`和`assertNotAlmostEqual()`来进行一些约等于断言。

```python
# unittest_almostequal.py

import unittest


class AlmostEqualTest(unittest.TestCase):

    def testEqual(self):
        self.assertEqual(1.1, 3.3 - 2.2)

    def testAlmostEqual(self):
        self.assertAlmostEqual(1.1, 3.3 - 2.2, places=1)

    def testNotAlmostEqual(self):
        self.assertNotAlmostEqual(1.1, 3.3 - 2.0, places=1)
```

输出:

```shell
$ python3 -m unittest unittest_almostequal.py

.F.
================================================================
FAIL: testEqual (unittest_almostequal.AlmostEqualTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_almostequal.py", line 12, in testEqual
    self.assertEqual(1.1, 3.3 - 2.2)
AssertionError: 1.1 != 1.0999999999999996

----------------------------------------------------------------
Ran 3 tests in 0.001s

FAILED (failures=1)
```

## Containers

### unittest_equality_container.py

除了一般的`assertEqual()`和`assertNotEqual()`，有一些特殊的方法可以比较比如`list`, `dict`, `set`这些容器对象.

```python
# unittest_equality_container.py

import textwrap
import unittest


class ContainerEqualityTest(unittest.TestCase):

    def testCount(self):
        self.assertCountEqual(
            [1, 2, 3, 2],
            [1, 3, 2, 3]
        )

    def testDict(self):
        self.assertDictEqual(
            {'a': 1, 'b': 2},
            {'a': 1, 'b': 2}
        )

    def testList(self):
        self.assertListEqual(
            [1, 2, 3],
            [1, 2, 3]
        )

    def testMultiLineString(self):
        self.assertMultiLineEqual(
            testwarp.dedent("""
            This string
            has more than one
            line.
            """),
            testwarp.dedent("""
            This string has
            more than two
            lines.
            """)
        )

    def testSequence(self):
        self.assertSequenceEqual(
            [1, 2, 3],
            [1, 3, 2]
        )

    def testSet(self):
        self.assertSetEqual(
            set([1, 2, 3])
            set([1, 3, 2, 4])
        )

    def testTuple(self):
        self.assertTupleEqual(
            (1, 'a'),
            (1, 'b')
        )
```

输出：

```shell
$ python3 -m unittest unittest_equality_container.py

FFFFFFF
================================================================
FAIL: testCount
(unittest_equality_container.ContainerEqualityTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_equality_container.py", line 15, in
testCount
    [1, 3, 2, 3],
AssertionError: Element counts were not equal:
First has 2, Second has 1:  2
First has 1, Second has 2:  3

================================================================
FAIL: testDict
(unittest_equality_container.ContainerEqualityTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_equality_container.py", line 21, in
testDict
    {'a': 1, 'b': 3},
AssertionError: {'b': 2, 'a': 1} != {'b': 3, 'a': 1}
- {'a': 1, 'b': 2}
?               ^

+ {'a': 1, 'b': 3}
?               ^


================================================================
FAIL: testList
(unittest_equality_container.ContainerEqualityTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_equality_container.py", line 27, in
testList
    [1, 3, 2],
AssertionError: Lists differ: [1, 2, 3] != [1, 3, 2]

First differing element 1:
2
3

- [1, 2, 3]
+ [1, 3, 2]

================================================================
FAIL: testMultiLineString
(unittest_equality_container.ContainerEqualityTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_equality_container.py", line 41, in
testMultiLineString
    """),
AssertionError: '\nThis string\nhas more than one\nline.\n' !=
'\nThis string has\nmore than two\nlines.\n'

- This string
+ This string has
?            ++++
- has more than one
? ----           --
+ more than two
?           ++
- line.
+ lines.
?     +


================================================================
FAIL: testSequence
(unittest_equality_container.ContainerEqualityTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_equality_container.py", line 47, in
testSequence
    [1, 3, 2],
AssertionError: Sequences differ: [1, 2, 3] != [1, 3, 2]

First differing element 1:
2
3

- [1, 2, 3]
+ [1, 3, 2]

================================================================
FAIL: testSet
(unittest_equality_container.ContainerEqualityTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_equality_container.py", line 53, in testSet
    set([1, 3, 2, 4]),
AssertionError: Items in the second set but not the first:
4

================================================================
FAIL: testTuple
(unittest_equality_container.ContainerEqualityTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_equality_container.py", line 59, in
testTuple
    (1, 'b'),
AssertionError: Tuples differ: (1, 'a') != (1, 'b')

First differing element 1:
'a'
'b'

- (1, 'a')
?      ^

+ (1, 'b')
?      ^


----------------------------------------------------------------
Ran 7 tests in 0.004s

FAILED (failures=7)
```

### unittest_in.py

使用`assertIn()`可以测试容器中的成员。

```python
# unittest_in.py

import unittest


class ContainerMembershipTest(unittest.TestCase):

    def testDict(self):
        self.assertIn(4, {1: 'a', 2: 'b', 3: 'c'})
    
    def testList(self):
        self.assertIn(4, [1, 2, 3])

    def testSet(self):
        self.assertIn(4, set([1, 2, 3]))
```

输出:

```shell
$ python3 -m unittest unittest_in.py

FFF
================================================================
FAIL: testDict (unittest_in.ContainerMembershipTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_in.py", line 12, in testDict
    self.assertIn(4, {1: 'a', 2: 'b', 3: 'c'})
AssertionError: 4 not found in {1: 'a', 2: 'b', 3: 'c'}

================================================================
FAIL: testList (unittest_in.ContainerMembershipTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_in.py", line 15, in testList
    self.assertIn(4, [1, 2, 3])
AssertionError: 4 not found in [1, 2, 3]

================================================================
FAIL: testSet (unittest_in.ContainerMembershipTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_in.py", line 18, in testSet
    self.assertIn(4, set([1, 2, 3]))
AssertionError: 4 not found in {1, 2, 3}

----------------------------------------------------------------
Ran 3 tests in 0.001s

FAILED (failures=3)
```

## Testing for Exceptions

### unittest_exception.py

```python
# unittest_exception.py

import unittest


def raises_error(*args, *kwds):
    raise ValueError('Invalid value:' + str(args) + str(kwds))


class ExceptionTest(unittest.TestCase):

    def testTrapLocally(self):
        try:
            raises_error('a', b='c')
        except ValueError:
            pass
        else:
            self.fail('Did not see ValueError')

    def testAssertRaises(self):
        self.assertRaises(
            ValueError,
            raises_error,
            'a',
            b='c'
        )

    def testAssertRaiseContestManger(self):
        witn self.assertRaises(ValueError):
        raises_error('a', b='c')
```

输出:

```shell
$ python3 -m unittest -v unittest_exception.py

testAssertRaises (unittest_exception.ExceptionTest) ... ok
testTrapLocally (unittest_exception.ExceptionTest) ... ok

----------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

## Test Fixtures

Fixture是一个测试额外需要的资源。例如，一个类的测试可能都会需要共享一个资源。比如数据库连接或者临时文件。

`unittest`包含了一些特殊的钩子可以配置/清理fixtures。如果想要为每个test case建立一个fixture，可以重写`TestCase.setUp()`，清理可以重写`tearDown()`。想要管理一个TestCase类下面贡献的fixture，可以重写类方法`setUpClass()`和`tearDownClass()`.想要建立模块级的fixture，可以使用模块函数`setUpModule()`和`tearDownModule()`(只要函数名是这样就可以了).

```python
# unittest_fixtures.py

import random
import unittest


def setUpModule():
    print("In setUpModule()")


def tearDoenModule():
    print("In tearDownModule()")


class FixturesTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("In setUpClass()")
        cls.good_range = range(1, 10)

    @classmethod
    def tearDownClass(cls):
        print("In tearDownClass()")
        del cls.good_range

    def setUp(self):
        super().setUp()
        print("\nIn setUp()")
        self.value = randomw.randint(
            self.good_random.start,
            self.good_random.stop - 1
        )

    def tearDown(self):
        print("In TearDown()")
        del self.value
        super().tearDown()

    def test1(self):
        print("In test1()")
        self.assertIn(self.value, self.good_range)
    
    def test2(self):
        print("In test2()")
        self.assertIn(self.value, self.good_range)
```

输出:

```shell
$ python3 -u -m unittest -v unittest_fixtures.py

In setUpModule()
In setUpClass()
test1 (unittest_fixtures.FixturesTest) ...
In setUp()
In test1()
In tearDown()
ok
test2 (unittest_fixtures.FixturesTest) ...
In setUp()
In test2()
In tearDown()
ok
In tearDownClass()
In tearDownModule()

----------------------------------------------------------------
Ran 2 tests in 0.001s

OK
```

### unittest_addcleanup.py

如果在fixture的清理过程中出现了错误，那么`tearDown`方法不会被调用。想要确保一个fiture总是正确的release，可以使用`addCleanup()`.

```python
# unittest_addcleanup.py

import random
import shutil
import tempfile
import unittest


def remove_tmpdir(dirname):
    print('In remove_tmpdir()')    
    shutil.rmtree(dirname)


class FixturesTest(unittest.TestCase):
    
    def setUp(self):
        super().setUp()
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(remove_tmpdir, self.tmpdir)
        
    def test1(self):
        print('\nIn test1()')

    def test2(self):
        print('\nIn test2()')
```

输出:

```shell
$ python3 -u -m unittest -v unittest_addcleanup.py

test1 (unittest_addcleanup.FixturesTest) ...
In test1()
In remove_tmpdir()
ok
test2 (unittest_addcleanup.FixturesTest) ...
In test2()
In remove_tmpdir()
ok

----------------------------------------------------------------
Ran 2 tests in 0.003s

OK
```

## Repeating Tests with Different Inputs

经常会碰到把同一个测试逻辑根据不同的输入测试多次的情况。与其为每个情况新建一个方法，更常见的方式是新建一个方法包含若干关联的断言。但是这个方法的问题在于，如果一个断言失败了，剩下的断言也会被跳过。

有一个更好的方法是，使用`subTest()`来创建一个测试上下文。如果测试失败，错误将会被报告，剩下的测试仍将继续。

### unittest_subtest.py

```python
# unittest_subtest.py

import unittest


class SubTest(unittest.TestCase):
    
    def test_combined(self):
        self.assertRegex('abc', 'a')
        self.assertRegex('abc', 'B')
        # 下面的断言不会执行
        self.assertRegex('abc', 'c')
        self.assertRegex('abc', 'd')
    
    def test_with_subset(self):
        for pat in ['a', 'B', 'c', 'd']:
            with self.subTest(pattern=pat):
                self.assertRegex('abc', pat)
```

输出如下:

```shell
$ python3 -m unittest -v unittest_subtest.py

test_combined (unittest_subtest.SubTest) ... FAIL
test_with_subtest (unittest_subtest.SubTest) ...
================================================================
FAIL: test_combined (unittest_subtest.SubTest)
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_subtest.py", line 13, in test_combined
    self.assertRegex('abc', 'B')
AssertionError: Regex didn't match: 'B' not found in 'abc'

================================================================
FAIL: test_with_subtest (unittest_subtest.SubTest) (pattern='B')
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_subtest.py", line 21, in test_with_subtest
    self.assertRegex('abc', pat)
AssertionError: Regex didn't match: 'B' not found in 'abc'

================================================================
FAIL: test_with_subtest (unittest_subtest.SubTest) (pattern='d')
----------------------------------------------------------------
Traceback (most recent call last):
  File ".../unittest_subtest.py", line 21, in test_with_subtest
    self.assertRegex('abc', pat)
AssertionError: Regex didn't match: 'd' not found in 'abc'

----------------------------------------------------------------
Ran 2 tests in 0.001s

FAILED (failures=3)
```

## Skipping Tests

使用`skip()`, `skipIf()`, `skipUnless()`可以跳过(或者在一些条件下)某些测试。

### unittest_skip.py

```python
# unittest_skip.py

import sys
import unittest


class SkippingTest(unittest.TestCase):

    @unittest.skip('always skipped')
    def test(self):
        self.assertTrue(False)

    @unittest.skipIf(sys.version_info[0] > 2,
                    'only runs on python 2')
    def test_python2_only(self):
        self.assertTrue(False)

    @unittest.skipUnless(sys.platform == 'Darwin',
                         'only runs on macOS')
    def test_macos_only(self):
        self.assertTrue(True)

    def test_raise_skiptest(self):
        raise unittest.SkipTest('skipping via exception')
```

输出如下:

```python
$ python3 -m unittest -v unittest_skip.py

test (unittest_skip.SkippingTest) ... skipped 'always skipped'
test_macos_only (unittest_skip.SkippingTest) ... skipped 'only
runs on macOS'
test_python2_only (unittest_skip.SkippingTest) ... skipped 'only
runs on python 2'
test_raise_skiptest (unittest_skip.SkippingTest) ... skipped
'skipping via exception'

----------------------------------------------------------------
Ran 4 tests in 0.000s

OK (skipped=4)
```

## Ignoring Failing Tests

### unittest_expectedfailure.py

```python
# unittest_expectedfailure.py

import unittest


class Test(unittest.TestCase):

    @unittest.expectedFailure
    def test_never_passes(self):
        self.assertTrue(False)

    @unittest.expectedFailure
    def test_always_passes(self):
        self.assertTrue(True)
```

输出:

```shell
$ python3 -m unittest -v unittest_expectedfailure.py

test_always_passes (unittest_expectedfailure.Test) ...
unexpected success
test_never_passes (unittest_expectedfailure.Test) ... expected
failure

----------------------------------------------------------------
Ran 2 tests in 0.001s

FAILED (expected failures=1, unexpected successes=1)
```