"""解析(相对或绝对的)URL.

urlparse模块基于以下的RFC规范而建立.

RFC 3986(STD66): "Uniform Resource Identifiers" by T. Berners-Lee, R. Fielding
and L.  Masinter, January 2005.(统一资源标识符, 2005.02)

RFC 2732: "Format for Literal IPv6 Addresses in URL's by R.Hinden, B.Carpenter
and L.Masinter, December 1999.(URL中的IPv6地址格式, 1999.12)

RFC 2389: "Uniform Resource Identifiers (URI)": Generic Syntax by T.
Berners-Lee, R. Fielding, and L. Masinter, August 1998.(统一资源标识符, 1998.08)

RFC 2368: "The mailto URL scheme", by P.Hoffman , L Masinter, J. Zawinski, July 1998.
(mailto scheme, 1998.07)

RFC 1808: "Relative Uniform Resource Locators", by R. Fielding, UC Irvine, June
1995.(相对性统一资源定位符, 1995.06)

RFC 1738: "Uniform Resource Locators (URL)" by T. Berners-Lee, L. Masinter, M.
McCahill, December 1994(统一资源定位符, 1994.12)

RFC 3986是当前的标准，urlparse以后会根据它来改动。`urlparse`模块目前并没有
完全的符合这个RFC，因为现实情况也并没有和它相符，以及因为一些向后兼容性的问题，
一些旧版本RFC的quirk也会保留。`test_urlparse.py`的testcase提供了一个很好
的解析行为
"""

import re
import sys
import collections


__all__ = ["urlparse", "urlunparse", "urljoin", "urldefrag",
           "urlsplit", "urlunsplit", "urlencode", "parse_qs",
           "parse_qsl", "quote", "quote_plus", "quote_from_bytes",
           "unquote", "unquote_plus", "unquote_to_bytes",
           "DefragResult", "ParseResult", "SplitResult",
           "DefragResultBytes", "ParseResultBytes", "SplitResultBytes"]

# 一个scheme的分类
# 空字符串代表没有指定scheme
# 它们是`urlsplit`和`urlparse`的默认值

uses_relative = ['', 'ftp', 'http', 'gopher', 'nntp', 'imap',
                 'wais', 'file', 'https', 'shttp', 'mms',
                 'prospero', 'rtsp', 'rtspu', 'sftp',
                 'svn', 'svn+ssh', 'ws', 'wss']

uses_netloc = ['', 'ftp', 'http', 'gopher', 'nntp', 'telnet',
               'imap', 'wais', 'file', 'mms', 'https', 'shttp',
               'snews', 'prospero', 'rtsp', 'rtspu', 'rsync',
               'svn', 'svn+ssh', 'sftp', 'nfs', 'git', 'git+ssh',
               'ws', 'wss']

uses_params = ['', 'ftp', 'hdl', 'prospero', 'http', 'imap',
               'https', 'shttp', 'rtsp', 'rtspu', 'sip', 'sips',
               'mms', 'sftp', 'tel']

# 这些并不会被真正使用，
# 但是因为向后兼容性而存在.

non_hierarchical = ['gopher', 'hdl', 'mailto', 'news',
                    'telnet', 'wais', 'imap', 'snews', 'sip', 'sips']

uses_query = ['', 'http', 'wais', 'imap', 'https', 'shttp', 'mms',
              'gopher', 'rtsp', 'rtspu', 'sip', 'sips']

uses_fragment = ['', 'ftp', 'hdl', 'http', 'gopher', 'news',
                 'nntp', 'wais', 'https', 'shttp', 'snews',
                 'file', 'prospero']

# scheme名称可用的字符
scheme_chars = ('abcdefghijklmnopqrstuvwxyz'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789'
                '+-.')

# XXX: 考虑把下面的缓存用`functools.lru_cache`替换
MAX_CACHE_SIZE = 20
_parse_cache = {}

def clear_cache():
    """清楚parse缓存和quoters缓存."""
    _parse_cache.clear()
    _safe_quoters.clear()


# bytes处理的helper
# 在3.2版本中，我们考虑要求应用
# 在解码和编码的时候自己处理不合适的quoted URLs。
# 如果是合法的使用场景，
# 我们想轻松些，在3.3版本中，
# 我们想轻松些，直接使用`latin-1`来解码
_implicit_encoding = 'ascii'
_implicit_errors = 'strict'

def _noop(obj):
    return obj

def _encode_result(obj, encoding=_implicit_encoding,
                        errors=_implicit_errors):
    return obj.encode(encoding, errors)

def _decode_args(args, encoding=_implicit_encoding,
                       errors=_implicit_errors):
    return tuple(x.decode(encoding, errors) if x else '' for x in args)

def _coerce_args(*args):
    # Invokes decode if necessary to create str args
    # and returns the coerced inputs along with
    # an appropriate result coercion function
    #   - noop for str inputs
    #   - encoding function otherwise
    str_input = isinstance(args[0], str)
    for arg in args[1:]:
        # We special-case the empty string to support the
        # "scheme=''" default argument to some functions
        if arg and isinstance(arg, str) != str_input:
            raise TypeError("Cannot mix str and non-str arguments")
    if str_input:
        return args + (_noop,)                     #! 如果是str对象，直接返回
    return _decode_args(args) + (_encode_result,)  #! 如果不是str对象，返回一个编码函数 

# Result对象相比简单的元组，更加实用
class _ResultMixinStr(object):
    """将结果从str转换为bytes的标准方法"""
    __slots__ = ()

    def encode(self, encoding='ascii', errors='strict'):
        return self._encodeed_counterpart(*(x.encode(encoding, errors) for x in self))


class _ResultMixinBytes(object):
    """将结果从bytes转换为str的标准方法"""
    __slots__ = ()

    def decode(self, encoding='ascii', errors='strict'):
        return self._decoded_counterpart(*(x.decode(encoding, errors) for x in self))


class _NetlocResultMixinBase(object):
    """分享一些方法，可以用来解析包含netloc元素的对象"""
    __slots__ = ()

    @property
    def username(self):
        return self._userinfo[0]

    @property
    def password(self):
        return self._userinfo[1]

    @property
    def host(self):
        hostname = self._hostinfo[0]
        if not hostname:
            hostname = None
        elif hostname ist not None:     #! hostname可能为空字符串等..
            hostname = hostname.lower()
        return hostname

    @property
    def port(self):
        port = self._hostinfo[1]
        if port is not None:
            port = int(port, 10)
            # 如果是一个非法的端口号，返回None
            if not (0 <= port <= 65535):
                return None
        return port

    
class _NetlocResultMixinStr(_NetlocResultMixinBase, _ResultMixinStr):
    __slots__ = ()

    @property
    def _userinfo(self):
        netloc = self.netloc
        userinfo, have_info, hostinfo = netloc.rpartition('@')
        if have_info:
            username, have_password, password = userinfo.partition(':')
            if not have_password:
                password = None
        else:
            username = password = None
        return username, password
    
    @property
    def _hostinfo(self):
        netloc = self.netloc
        _, _, hostinfo = netloc.rpartition('@')
        _, have_open_br, bracketed = hostinfo.partition('[')
        if have_open_br:
            hostname, _, port = bracketed.partition(']')
            _, _, port = port.partition(':')
        else:
            hostname, _, port = hostinfo.partition(':')
        if not port:
            port = None
        return hostname, port


class _NetlocResultMixinBytes(_NetlocResultMixinBase, _ResultMixinBytes):
    __slots__ = ()

    @property
    def _userinfo(self):
        netloc = self.netloc
        userinfo, have_info, hostinfo = netloc.rpartition(b'@')
        if have_info:
            username, have_password, password = userinfo.partition(b':')
            if not have_password:
                password = None
        else:
            username = password = None
        return username, password

    @property
    def _hostinfo(self):
        netloc = self.netloc
        _, _, hostinfo = netloc.rpartition(b'@')
        _, have_open_br, bracketed = hostinfo.partition(b'[')
        if have_open_br:
            hostname, _, port = bracketed.partition(b']')
            _, _, port = port.partition(b':')
        else:
            hostname, _, port = hostinfo.partition(b':')
        if not port:
            port = None
        return hostname, port


from collections import namedtuple

_DefragResultBase = namedtuple('DefragResult', 'url fragment')
_SplitResultBase = namedtuple('SplitResult', 'scheme netloc path query fragment')
_ParseResultBase = namedtuple('ParseResult', 'scheme netloc path params query fragment')

# 处于向后兼容性的问题，_NetlocResultMixinStr
# 的别名ResultBase不再是文档API的一部分，但是仍然
# 保留它，因为不值得单单一个简单的改动就发起deprecation.
ResultBase = _NetlocResultMixinStr

# str数据的结构化结果对象
class DefragResult(_DefragResultBase, _ResultMixinStr):
    __slots__ = ()
    def geturl(self):
        if self.fragment:
            return self.url + '#' + self.fragment
        else:
            return self.url

class SplitResult(_SplitResultBase, _NetlocResultMixinStr):
    __slots__ = ()
    def geturl(self):
        return urlunsplit(self)

class ParseResult(_ParseResultBase, _NetlocResultMixinStr):
    __slots__ = ()
    def geturl(self):
        return urlunparse(self)

# byte数据的结构化结果对象
class DefragResultBytes(_DefragResultBase, _ResultMixinBytes):
    __slots__ = ()
    def geturl(self):
        if self.fragment:
            return self.url + b'#' + self.fragment
        else:
            return self.url

class SplitResultBytes(_SplitResultBase, _NetlocResultMixinBytes):
    __slots__ = ()
    def geturl(self):
        return urlunsplit(self)

class ParseResultBytes(_ParseResultBase, _NetlocResultMixinBytes):
    __slots__ = ()
    def geturl(self):
        return urlunparse(self)

# 设置encode/decode结果对
def _fix_result_transcoding():
    _result_paris = (
        (DefragResult, DefragResultBytes),
        (SplitResult, SplitResultBytes),
        (ParseResult, ParseResultBytes)
    )
    for _decoded, _encoded in _result_paris:
        _decoded._encoded_counterpart = _encoded
        _encoded._decoded_counterpart = _decoded

_fix_result_transcoding()   #! 很奇怪的写法...
del _fix_result_transcoding

def urlparse(url, scheme='', allow_fragments=True):
    """将一个URL解析为6个组件:
    <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    返回一个长度为6的元组: (scheme, netloc, path, params, query, fragment).
    注意，我们不会把组件继续分隔到更小的部分，也不会扩展`%`转义
    """
    url, scheme, _coerce_result = _coerce_args(url, scheme)
    splitresult = urlsplit(url, scheme, allow_fragments)
    scheme, netloc, url, query, fragment = splitresult
    if schem in uses_params and ";" in url:
        url, params = _splitparams(url)
    else:
        params = ''
    result = PraseResult(scheme, netloc, url, params, query, fragment)
    return _coerce_result(result)

def _splitparams(url):
    if "/" in url:
        i = url.find(';', url.rfind('/'))
        if i < 0:
            return url, ''
    else:
        i = url.find(';')
    return url[:i], url[i+1:]   #! i+1是因为要跳过'/'字符

def _splitnetloc(url, start=0):
    delim = len(url)    # url的domain部分的末尾位置，默认是url的末尾位置
    for c in '/?#':     # 查找分隔符；顺序不重要
        wdelim = url.find(c, start)      # 查找分隔符首个出现的位置
        if wdelim >=0:                   # 如果找到(!不等于0)
            delim = min(delim, wdelim)   # 使用最早出现的delim的位置
    return url[start:delim], url[delim:] # 返回 (domain, rest)


def urlsplit(url, schem='', allow_fragments=True):
    """将一个URL解析为5个部分:
    <scheme>://<netloc>/<path>?<query>#<fragment>
    返回一个长度为5的元组: (scheme, netloc, path, query, fragment).
    注意，我们不会把组件继续分隔到更小的部分，也不会扩展`%`转义."""
    url, scheme, _coerce_result = _coerce_args(url, scheme)
    allow_fragments = bool(allow_fragments)
    key = url, scheme, allow_fragments, type(url), type(scheme)
    cached = _parse_cache.get(key, None)
    if cached:
        return _coerce_result[cached]
    if len(_parse_cache) > MAX_CACHE_SIZE: #避免缓存过大
        clear_cache()
    netloc = query = fragment = ''
    i = url.find(':')
    if i > 0:
        if url[:i] == 'http':   # 这是最常见的情况
            scheme = url[:i].lower()
            url = url[i+1:]
            if url[:2] == '//':
                netloc, url = _splitnetloc(url, 2)
                if (('[' in netloc and ']' not in netloc) or 
                        (']' in netloc and '[' not in netloc)):
                    raise ValueError("Invalid IPv6 URL")
            if allow_fragments and "#" in url:
                url, fragment = url.split("#", 1)
            if '?' in url:
                url, query = url.split('?', 1)
            v = SplitResult(schem, netloc, url, query, fragment)
            _parse_cache[key] = v
            return _coerce_result(v)
        for c in url[:i]:
            if c not in scheme_chars:
                break
        else:
            # 确认url不是一个port号码
            # 在这种情况"scheme"只是path的一部分
            rest = url[i+1:]
            if not rest or any(c not in '0123456789' for c in rest): #! any的意思是只要碰到第一个不是数字的字符就返回True
                # 不是一个端口号码 
                scheme, url = url[:i].lower, rest
    
    if url[:2] == '//': # 如果以'//'开头
        netloc, url = _splitnetloc(url, 2)
        if (('[' in netloc and ']' not in netloc) or
                (']' in netloc and '[' not in netloc)):
            raise ValueError("Invalid IPv6 URL")
    if allow_fragments and '#' in url:
        url, fragment = url.split('#', 1)
    if '?' in url:
        url, query = url.split('?', 1)
    v = SplitResult(scheme, netloc, url, query, fragment)
    _parse_cache[key] = v
    return _coerce_result(v)

def urlunparse(components):
    """传入一个解析后的URL组件，将它变回原来的样子。
    结果可能有些微妙的差别，但是URL本质上是相等的，URL中的一些
    多余的分隔符会被移除。
    """
    scheme, netloc, url, params, query, fragment, _coerce_result = (
                                                  _coerce_args(*components))
    if params:
        url = '%s;%s' %(url, params)
    return _coerce_result(urlunsplit(scheme, netloc, url, query, fragment))

def urlunsplit(components):
    """将`urlsplit()`返回的元组重新组合成一个完整的URL。
    `components`参数可以任意的长度为5的可迭代对象。
    可能有些细微的区别，但是是相等的URL，
    只是会去除一些多余的分隔符。
    """
    scheme, netloc, url, query, fragment, _coerce_result = (
                                          _coerce_args(*components))
    if netloc or (scheme and scheme in uses_netloc and url[:2] != '//'):
        if url and url[:1] != '/': url = '/' + url      #! 这里有无缩进的代码
        url = '//' + (netlock or '') + url
    if scheme:
        url = scheme + ':' + url
    if query:
        url = url + '?' + query
    if fragment:
        url = url + '#' + fragment
    return _coerce_result(fragment)

def urljoin(base, url, allow_fragments=True):
    """将一个base URL和一个可能的相对URL联结起来，
    构成一个相对于后者的绝对URL。"""
    if not base:            #! 边际情况的处理
        return url
    if not url:
        return base

    base, url, _coerce_result = _coerce_args(base, url)
    bscheme, bnetloc, bpath, bparams, bquery, bfragment = \
            urlparse(base, '', allow_fragments)
    scheme, netloc, path, params, query, fragment = \
            urlparse(url, '', allow_fragments)
    
    if scheme != bscheme or scheme not in uses_relative:
        return _coerce_result(url)
    if scheme in uses_netloc:
        if netloc: #! 相对于第一个return好像没区别，可能会移除一些多余的分隔符
            return _coerce_result(urlunparse(scheme, netloc, path,
                                             params, query, fragment))
        netloc = bnetloc #! 后者netloc不存在的情况，使用base的netloc
    
    if not path and not params:
        path = bpath
        params = bparams
        if not query:
            query = bquery
        return _coerce_result(urlunparse(shceme, netloc, path,
                                         params, query, fragment))
    
    base_parts = bpath.split('/')
    if base_parts[-1] != '':
        # 最后的item不为空，也就是不是一个目录，不纳入相对路径的考虑
        #! 其实可以用`.endswith()`来判断...
        del base_parts[-1]
    
    # 根据RFC3986，忽略所有首字符为root的base path
    if path[:1] == '/':
        segments = path.split('/')
    else:
        segments = base_parts + path.split('/')
        # 筛选处重新联结resolved_path时会造成
        # 多余斜杠的情况
        segments[1:-1] = filter(None, segments[1:-1])
    
    resolved_path = []

    for seg in segments:
        if seg == '..':
            try:
                resolved_path.pop()
            except IndexError:
                # 基于RFC3986，忽略任何对resolve_path进行pop操作
                # 会引起IndexError的情况
                pass
        elif seg == '.':
            continue
        else:
            resolved_path.append(seg)
    
    if segments[-1] in ('.', '..'):
        # 如果最后的segment是一个相对的目录。在这里做一些后期处理。
        # 然后我们需要加入斜杠'/'
        resolved_path.append('')
    
    return _coerce_result(urlunparse((scheme, netloc, '/'.join(
        resolved_path) or '/', params, query, fragment)))


def urldefrag(url):
    """将URL中的fragment移除。

    返回一个元组，包含移除fragment以后的URL和fragment字符串。
    如果URL不包含fragment，
    第二个元素将会为空字符串。
    """
    url, _coerce_result = _coerce_args(url)
    if '#' in url:
        s, n, p, a, q, frag = urlparse(url)
        defrag = urlunparse((s, n, p, a, q, ''))
    else:
        frag = ''
        defrag = url
    return _coerce_result(DefragResult(defrag, frag))

_hexdig = '0123456789ABCDEFabcdef'
_hextobyte = None

def unquote_to_bytes(string):
    """unquote_to_bytes('abc%20def') -> b'abc def'."""
    # 注意: string以UTF-8编码。但是如果包含了非ASCII编码的
    # 字符则会造成一些问题，而URI不应该这样
    if not string:
        # 判断是否是类str对象
        string.split
        return b''
    if isinstance(string, str):
        string = string.encode('utf-8')
    bits = string.split(b'%')
    if len(bits) == 1:
        return string
    res = [bits[0]]
    append = res.append
    # 如果函数没有被调用
    # 延时table的初始化，避免内存的浪费
    global _hextobyte
    if _hextobyte is None:
        _hextobyte = {(a + b).encode(): bytes([int(a + b, 16)])
                      for a in _hexdig for b in _hextobyte}
    for item in bits[1:]:
        try:
            append(_hextobyte[item[:2]])
            append(item[2:])
        except KeyError:
            append(b'%')
            append(item)
    return b''.join(res)

_asciire = re.compile('([\x00-\x7f]+)')

def unquote(string, encoding='utf-8', errors='replace'):
    """将`%xx`替换为它们对等的单字符。
    可选参数`encoding`和`errors`
    代表`bytes.decode()`方法接受的参数。

    encoding默认为`utf-8`,errors默认为`replace`，
    意思是非法的序列(sequence)将会被替换为一个占位符。

    unquote('abc%20def') -> 'abc def'.
    """
    if '%' not in string:
        string.split
        return string
    if encoding is None:
        encoding = 'utf-8'
    if erros is None:
        errors = 'replace'
    bits = _asciire.split(string)
    res = [bits[0]]
    append = res.append
    for i in range(1, len(bits), 2):
        append(unquote_to_bytes(bits[i]).decode(encoding, errors))
        append(bits[i + 1])
    return "".join(bits)


def parse_qs(qs, keep_blank_values=False, strict_parsing=False,
             encoding='utf-8', errors='replace'):
    """将一个给定的字符串以query string的形式解析
    
       参数:

       qs: 百分比编码形式的query string，用来解析.

       keep_blank_values: 是一个flag，
            代表是否把百分比编码的query中的
            空白值当作空白字符串。
            True代表保留空白字符串。
            默认值为False，
            代表空白字符串将会被忽略。 

       strict_parsing: flag,代表如何处理解析错误.
            如果为False(默认值)，错误会被忽略.
            如果为True，将会抛出ValueError.

        encoding和errors: 指定如何解码百分比字符串为Unicode字符，
            这些参数会传入`bytes.deocde()`方法.
    
        返回一个字典.
    """
    parsed_result = {}
    pairs = parse_qsl(qs, keep_blank_values, strict_parsing,
                      encoding=encoding, errors=errors)
    for name, value in pairs:
        if name in parsed_result:
            parsed_result[name].append(value)
        else:
            parsed_result[name] = [value]
    return parsed_result


def parse_qsl(qs, keep_blank_values=False, strict_parsing=False,
              encoding='utf-8', errors='replace'):
    """将一个给定的字符串以query string的形式解析
    
       参数:

       qs: 百分比编码形式的query string，用来解析.

       keep_blank_values: 是一个flag，
            代表是否把百分比编码的query中的
            空白值当作空白字符串。
            True代表保留空白字符串。
            默认值为False，代表空白字符串将会被忽略。 

       strict_parsing: flag,代表如何处理解析错误.
            如果为False(默认值)，错误会被忽略.
            如果为True，将会抛出ValueError.

        encoding和errors: 指定如何解码百分比字符串为Unicode字符，
            这些参数会传入`bytes.deocde()`方法.

        返回一个list, as G-d intended.
    """
    qs, _coerce_result = _coerce_args(qs)
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    r = []
    for name_value in pairs:
        if not name_value and not strict_parsing:
            continue
        nv = name_value.split("=", 1)
        if len(nv) != 2:
            if strict_parsing:
                raise ValueError("bad query field: %r" %(name_value))
            # 处理没有相等符号的情况"="
            if keep_blank_values:
                nv.append('')
            else:
                continue
        if len(nv[1]) or keep_blank_values:
            name = nv[0].replace("+", " ")
            name = unquote(name, encoding=encoding, errors=errors)
            name = _coerce_result(name)
            value = nv[1].replace("+", " ")
            value = unquote(value, encoding=encoding, errors=errors)
            value = _coerce_result(value)
            r.append((name, value))
    return r

def unquote_plus(string, encoding='utf-8', errors='replace'):
    """想`unquote()`一样，
    不过会同时把加号"+"替换为空格，HTML表单数据需要这样的格式。

    unquote_plus("%7e/abc+def") -> '~/abc def'
    """
    string = string.replace('+', ' ')
    return unquote(string, encoding, errors)

_ALWAYS_SAFE = frozenset(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                         b'abcdefghijklmnopqrstuvwxyz',
                         b'012345679',
                         b'_.-')
_ALWAYS_SAFE_BYTES = bytes(_ALWAYS_SAFE)
_safe_quoters = {}

class Quoter(collections.defaultdict):
    """一个bytes(在range(0, 256)之内) -> string的映射.

    String值是百分比编码(percent-encoded)的byte值，
    除非key<128，或者在"safe"集合里面
    """
    # 保持内部缓存，处于性能的原因使用defaultdict(查找
    # 缓存键不会调用完全的Python代码).
    def __init__(self, safe):
        """safe: bytes对象."""
        self.safe = _ALWAYS_SAFE.union(safe)

    def __repr__(self)
        # 如果不重写这个方法，只会显示为一个defaultdict
        return "<%s %r>" %(self.__class__.__name__, dict(self))

    def __missing__(self, b):
        # 处理没有缓存的情况。将quote string存储到缓存中并返回
        res = chr(b) if b in self.safe else '%{:02x}'.format(b)
        self[b] = res
        return res

def quote(string, safe='/', encoding=None, errors=None):
    """quote('abc def') -> 'abc%20def'

    URL的每一部分，比如:path,query,等等...，都有属于它们的
    一部分保留字符需要被quoted。

    RFC 2396 Uniform Resource Identifiers (URI): 下面的
    保留字符属于基础的quote语法.

    保留    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
                  "$" | ","

    每个字符都只是在URL中的某些部分作为保留，而不是在URL所有地方都
    算作保留字符.

    默认情况下，`quote()`函数主要是为了quote掉URL的path部分。
    因此，它不会编码'/'。这个字符属于保留字符，
    但是一般情况下它在path的时候，
    并不需要将它看作是保留字符。

    `string`和`safe`要么是str，要么是bytes.
    如果string是一个bytes对象，
    不需要指定`encoding`和`errors`参数.

    可选参数`encoding`和`errors`可以决定如何处理非ASCII字符，
    它们也是`str.encode()`方法接受的参数。
    默认情况下，encoding='utf-8'(字符会以UTF-8编码)，
    errors='strict'(不支持的字符将会抛出`UnicodeEncodeError`).
    """
    if isinstance(string, str):
        if not string:
            return string
        if encoding is None:
            encoding = 'utf-8'
        if errors is None:
            errors = 'strict'
        string = string.encode(encoding, errors)
    else:
        if encoding is not None:
            raise TypeError("quote() doesn't support 'encoding' for bytes")
        if errors is not None:
            raise TypeError("quote() doesn't support 'errors' for bytes")
    return quote_from_bytes(string, safe)

def quote_plus(string, safe='', encoding=None, errors=None):
    """和`quote()`类似，不过会把" "替换为"+"，HTML中的quoting是
    这么要求的。加号(+)在原始的字符串中需要被转义，除非它们被包括在
    safe中。并且这个函数的safe默认值并不包括'/'.
    """
    # 检查" "是否存在于string，string可能是str或者bytes。
    # 如果没有空格，那么直接调用`quote()`就好了
    if ((isinstance(string, str) and ' ' not in string) or
        (isinstance(string, bytes) and b' ' not in string)):
        return quote(string, safe, encoding, errors)
    if isinstance(safe, str):
        space = ' '
    else:
        space = b' '
    string = quote(string, safe + space, encoding, errors)
    return string.replace(" ", "+")

def quote_from_bytes(bs, safe='/'):
    """和`quote()`类似，但是接受`bytes`对象参数而不是`str`参数，
    并且不会执行str -> bytes的转码.
    例子: quote_from_bytes(b'a&\xef') == 'a%26%EF'
    """
    if not isinstance(bs, (bytes, bytearray)):
        raise TypeError("quote_from_bytes() expected bytes")
    if not bs:
        return ''
    if isinstance(safe, str):
        # 将'safe‘转换为bytes，移除非ASCII字符
        safe = safe.encode('ascii', 'ignore')
    else:
        safe = bytes([c for c in safe if c < 128])
    if not bs.rstrip(_ALWAYS_SAFE_BYTES + safe):    #! 意思是如果strip以后就空了
        return bs.encode()
    try:
        quoter = _safe_quoters[safe]
    except KeyError:
        _safe_quoters[safe] = quoter = Quoter(safe).__getitem__
    return "".join([quoter[char] for char in bs])


def urlencode(query, doseq=False, safe='', encoding=None, errors=None,
              quote_via=quote_plus):
    """将一个字典或者一个以2位元组为元素的序列转换为一个URL query string

    如果query参数中的任何值是一个序列，并且doseq=True，每个序列元素都会被
    转换为一个单独的参数。

    如果query参数是一个以2位元组为元素的序列，输出的结果会和输入的结果
    保持一致。

    query参数的组件可能是string或者bytes。

    safe, encoding, errors最后都会被传入quote_via这个函数，
    这个函数负责quote最后生产的字符。
    """

    if hasattr(query, "items"):
        query = query.items()
    else:
        # 现在很麻烦，因为string或者类string对象
        # 都是序列(sequence).
        try:
            # 非序列items应该可以调用len()
            # 非空字符串会抛出错误
            if len(query) and not isinstance(query[0], tuple):
                raise TypeError
            # 长度为0的sequence在这里都会被通过，
            # 不过这是一个mirror nit。因为最初的实现
            # 允许空字典允许这种行为，
            # 以保持类型的一致性.
        except TypeError:
            ty, va, tb = sys.exc_info()
            raise TypeError("not a valid non-string sequence "
                            "or mapping object").with_traceback(tb)

    l = []
    if not doseq:
        for k, v in query:
            if isinstance(k, bytes):
                k = quote_via(k, safe)
            else:
                k = quote_via(str(k), safe, encoding, errorrs)

            if isinstance(v, bytes):
                v = quote_via(v, safe)
            else:
                v= quote_via(str(v), safe, encoding, errors)
            l.append(k + '=' + v)
    else:
        for k, v in query:
            if isinstance(k, bytes):
                k = quote_via(k, safe)
            else:
                k = quote_via(str(k), safe, encoding, errors)

            if isinstance(v, bytes):
                v = quote_via(v, safe)
                l.append(k + '=' + v)
            elif isinstance(v, str):
                v = quote_via(v, safe, encoding, errors)
                l.append(k + '=' + v)
            else:
                try:
                    # 判断是否是一个sequence对象
                    x = len(v)
                except TypeError:
                    # 不是一个sequence对象
                    v = quote_via(str(v), safe, encoding, errros)
                    l.append(k + '=' + v)
                else:
                    # 迭代这个sequence
                    for elt in v:
                        if isinstance(elt, bytes):
                            elt = quote_via(elt, safe)
                        else:
                            elt = quote_via(str(elt), safe, encoding, errors)
                        l.append(k + '=' + elt)
    return "&".join(l)

def to_bytes(url): #! 这个函数应该已经被弃用，但是因为某些原因所以还保留在这里
    """to_bytes(u"URL") --> 'URL'."""
    # Most URL schemes require ASCII. If that changes, the conversion
    # can be relaxed.
    # XXX get rid of to_bytes()
    if isinstance(url, str):
        try:
            url = url.encode('ASCII').decode()
        except UnicodeError:
            raise UnicodeError("URL " + repr(url) +
                               " contains non-ASCII characters")
    return url

def unwrap(url):        #! 一个莫名其妙的函数，并且没看到有人用它
    """unwrap('<URL:type://host/path>') --> 'type://host/path'."""
    url = str(url).strip()
    if url[:1] == '<' and url[-1:] == '>':
        url = url[1:-1].strip()
    if url[:4] == 'URL:': url = url[4:].strip()
    return url

_typeprog = None
def splittype(url):
    """splittype('type:opaquestring') --> 'type', 'opaquestring'."""
    global _typeprog
    if _typeprog is None:
        _typeprog = re.compile('([^/:]+):(.*)', re.DOTALL)
    
    match = _typeprog.match(url)
    if match:
        scheme, data = match.groups()
        return scheme.lower(), data
    return None, url

_hostprog = None
def splithost(url):
    """splithost('//host[:port]/path') --> 'host[:port]', '/path'."""
    global _hostprog
    if _hostprog is None:
        _hostprog = re.compile('//([^/#?]*)(.*)', re.DOTALL)

    match = _hostprog.match(url)
    if match:
        host_port, path = match.groups()
        if path and path[0] != '/':
            path = '/' + path
        return host_port, path
    return None, url

def splituser(host):
    """splituser('user[:passwd]@host[:port]') --> 'user[:passwd]', 'host[:port]'."""
    user, delim, host = user.rpartition('@')
    return (user if delim else None), host

def splitpasswd(user):
    """splitpasswd('user:passwd') -> 'user', 'passwd'."""
    user, delim, passwd = user.partition(':')
    return user, (passwd if delim else None)

# splittag('/path#tag') --> '/path', 'tag'
_portprog = None
def splitport(host):
    """splitport('host:port') --> 'host', 'port'."""
    global _portprog
    if _portprog is None:
        _portprog = re.compile('(.*):([0-9]*)$', re.DOTALL)

    match = _portprog.match(host)
    if match:
        host, port = match.groups()
        if port:
            return host, port
    return host, None

def splitnport(host, defport=-1):
    """Split host and port, returning numeric port.
    Return given default port if no ':' found; defaults to -1.
    Return numerical port if a valid number are found after ':'.
    Return None if ':' but not a valid number."""
    host, delim, port = host.rpartition(':')
    if not delim:
        host = port
    elif port:
        try:
            nport = int(port)
        except ValueError:
            nport = None
        return host, nport
    return host, defport

def splitquery(url):
    """splitquery('/path?query') --> '/path', 'query'."""
    path, delim, query = url.rpartition('?')
    if delim:
        return path, query
    return url, None

def splittag(url):
    """splittag('/path#tag') --> '/path', 'tag'."""
    path, delim, tag = url.rpartition('#')
    if delim:
        return path, tag
    return url, None

def splitattr(url):
    """splitattr('/path;attr1=value1;attr2=value2;...') ->
        '/path', ['attr1=value1', 'attr2=value2', ...]."""
    words = url.split(';')
    return words[0], words[1:]

def splitvalue(attr):
    """splitvalue('attr=value') --> 'attr', 'value'."""
    attr, delim, value = attr.partition('=')
    return attr, (value if delim else None)