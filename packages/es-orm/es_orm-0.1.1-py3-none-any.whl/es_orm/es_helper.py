import functools
import logging
from typing import Dict, List, Callable
from elasticsearch import Elasticsearch, helpers
from helper import Result


class ESTypeMapping(object):
    Long = 'long'
    Integer = 'integer'
    Short = 'short'
    Byte = 'byte'
    Double = 'double'
    Float = 'float'
    HalfFloat = 'half_float'
    ScaledFloat = 'scaled_float'
    UnsignedLong = 'unsigned_long'
    Keyword = 'keyword'
    ConstantKeyword = 'constant_keyword'
    Wildcard = 'wildcard'
    Text = 'text'
    Date = 'date'
    IP = 'ip'
    Boolean = 'boolean'
    ESObject = 'object'


class ESBaseField:
    def __init__(self, field_name, field_type, **properties):
        self.field_name = field_name
        self.properties = {'type': field_type}
        self.properties.update(properties)

    def add_property(self, **properties):
        """ 添加字段属性 """
        self.properties.update(properties)

    def get_field(self):
        """ 获取属性结果 """
        return {self.field_name: self.properties}


class ESObjectField(ESBaseField):
    """json 类型"""

    def __init__(self, field_name, **properties):
        super(ESObjectField, self).__init__(field_name, ESTypeMapping.ESObject, **properties)


class LongField(ESBaseField):
    """ 64 位长整型 """

    def __init__(self, field_name, **properties):
        super(LongField, self).__init__(field_name, ESTypeMapping.Long, **properties)


class IntegerField(ESBaseField):
    """ 32位整型 """

    def __init__(self, field_name, **properties):
        super(IntegerField, self).__init__(field_name, ESTypeMapping.Integer, **properties)


class ShortField(ESBaseField):
    """ 16位短整型 """

    def __init__(self, field_name, **properties):
        super(ShortField, self).__init__(field_name, ESTypeMapping.Short, **properties)


class ByteField(ESBaseField):
    """ 字节类型 """

    def __init__(self, field_name, **properties):
        super(ByteField, self).__init__(field_name, ESTypeMapping.Byte, **properties)


class DoubleField(ESBaseField):
    """ 双精度浮点数 """

    def __init__(self, field_name, **properties):
        super(DoubleField, self).__init__(field_name, ESTypeMapping.Double, **properties)


class FloatField(ESBaseField):
    """ 单精度浮点型 """

    def __init__(self, field_name, **properties):
        super(FloatField, self).__init__(field_name, ESTypeMapping.Float, **properties)


class HalfFloatField(ESBaseField):
    """ 半浮点型 """

    def __init__(self, field_name, **properties):
        super(HalfFloatField, self).__init__(field_name, ESTypeMapping.HalfFloat, **properties)


class UnsignedLongField(ESBaseField):
    """ 64位 无符号长整形 """

    def __init__(self, field_name, **properties):
        super(UnsignedLongField, self).__init__(field_name, ESTypeMapping.UnsignedLong, **properties)


class KeywordField(ESBaseField):
    """ 关键字 """

    def __init__(self, field_name, **properties):
        super(KeywordField, self).__init__(field_name, ESTypeMapping.Keyword, **properties)


class ConstantKeywordField(ESBaseField):
    """ 关键字常量 值不变 """

    def __init__(self, field_name, **properties):
        super(ConstantKeywordField, self).__init__(field_name, ESTypeMapping.ConstantKeyword, **properties)


class WildcardField(ESBaseField):
    """ 通配符关键字 完整字段搜索慢 适用于类似日志grep等操作 """

    def __init__(self, field_name, **properties):
        super(WildcardField, self).__init__(field_name, ESTypeMapping.Wildcard, **properties)


class TextField(ESBaseField):
    """ 文本字段 """

    def __init__(self, field_name, **properties):
        super(TextField, self).__init__(field_name, ESTypeMapping.Text, **properties)


class DateField(ESBaseField):
    """ 日期 """

    def __init__(self, field_name, **properties):
        super(DateField, self).__init__(field_name, ESTypeMapping.Date, **properties)


class IPField(ESBaseField):
    """ IP """

    def __init__(self, field_name, **properties):
        super(IPField, self).__init__(field_name, ESTypeMapping.IP, **properties)


class BooleanField(ESBaseField):
    """ 布尔值 """

    def __init__(self, field_name, **properties):
        super(BooleanField, self).__init__(field_name, ESTypeMapping.Boolean, **properties)


class Base(object):
    _name_ = None

    def __call__(self, *args, **kwargs):
        pass


class BaseField(dict):
    def __init__(self, *args, **kwargs):
        super(BaseField, self).__init__(*args, **kwargs)

    def __add__(self, other: dict):
        for k, v in other.items():
            self.__setitem__(k, v)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            super(BaseField, self).__setitem__(key, self.__class__(**value))
        else:
            super(BaseField, self).__setitem__(key, value)

    def __getattribute__(self, item):
        try:
            return super(BaseField, self).__getattribute__(item)
        except:
            return self.get(item)

    def __call__(self):
        return self


class Fields(object):
    def __init__(self, **kwargs):
        self.fields = list()
        self.__add__(kwargs)

    def __iter__(self):
        yield from self.fields

    def __add__(self, other: Dict):
        for key, val in other.items():
            self.fields.append(BaseField(**{key: val}))
        return self


class BaseItem(Base):
    def __init__(self, fields: Fields):
        self.fields = fields

    def __iter__(self):
        for item in self.fields:
            yield {self._name_: item()}

    def __call__(self):
        return [item for item in self]

    def add(self, **kwargs):
        self.fields += kwargs


class Term(BaseItem):
    _name_ = 'term'


class Match(BaseItem):
    """ 分词匹配 """
    _name_ = 'match'


class FieldMatch(Match):
    """ 分词以 and 逻辑进行查询；默认Match以 or 逻辑查询 """

    def __iter__(self):
        for item in self.fields:
            for key, val in item().items():
                yield {self._name_: {key: {'query': val, 'operator': 'and'}}}


class Range(BaseItem):
    _name_ = 'range'


class Wildcard(BaseItem):
    _name_ = 'wildcard'


class Exists(BaseItem):
    _name_ = 'exists'


class MatchPhrase(BaseItem):
    """ 精确匹配 必须完全一样才能匹配到 """
    _name_ = 'match_phrase'


class BaseQuery(Base):
    def __init__(self, *items):
        self.items = list(items)

    def add(self, item: BaseItem):
        self.items.append(item)

    def __call__(self, _ret=[]):
        for item in self.items:
            tmp = item()
            if isinstance(tmp, List):
                _ret.extend(tmp)
            elif isinstance(tmp, Dict):
                _ret.append(tmp)
        return {self._name_: _ret}


class Must(BaseQuery):
    _name_ = 'must'


class MustNot(BaseQuery):
    _name_ = 'must_not'


class Filter(BaseQuery):
    _name_ = 'filter'


class Should(BaseQuery):
    _name_ = 'should'


class Bool(Base):
    def __init__(self, *queries):
        self._name_ = 'bool'
        self.queries = list(queries)

    def add(self, query: Base):
        self.queries.append(query)

    @staticmethod
    def deal_queries(item, _ret={}):
        for key, val in item().items():
            if _ret.get(key):
                _ret[key].extend(val)
            else:
                _ret[key] = val
        return _ret

    def __call__(self, _ret={}):
        for item in self.queries:
            _ret = self.deal_queries(item, _ret)
        if 'should' in _ret:
            _ret['minimum_should_match'] = 1
        return {self._name_: _ret}


class Sort(Base):
    def __init__(self, **kwargs):
        self._name_ = 'sort'
        self.sorts = list()
        for key, val in kwargs.items():
            self.sorts.append(BaseField(**{key: val}))

    def __call__(self, *args, **kwargs):
        return {self._name_: [item() for item in self.sorts]}


class Collapse(Base):
    """ 有去重的效果，但是返回的数据总量是去重前的
        通过某个字段折叠数据"""

    def __init__(self, field: str):
        """ field 去重的字段 """
        self._name_ = 'collapse'
        self.field = field

    def __call__(self):
        return {self._name_: {'field': self.field}}


class Update(Base):
    """ 脚本更新 """

    def __init__(self, **params):
        self._name_ = 'update'
        self.params = params
        self.lang = 'painless'

    def __call__(self, _source=''):
        for key in self.params:
            _source += f'{";" if _source else ""}ctx._source.{key}=params.{key}'
        return {'script': {'source': _source, 'params': self.params, 'lang': self.lang}}


class ESPagination(Base):
    def __init__(self, page=1, page_size=20, limit=10000):
        self.page = page
        self.limit = limit
        self.page_size = page_size

    def __call__(self):
        from_ = (self.page - 1) * self.page_size
        if from_ >= self.limit:
            return {'size': 0, 'from': self.limit}

        if self.page * self.page_size > self.limit:
            self.page_size = self.limit - from_

        return {'size': self.page_size, 'from': from_}


class Q(Base):
    """
    usage:
    # >>> q = Q.filter('exists', field='field_name') # 判断字段是否存在
    # # +/& 号都表示 与操作
    # >>> q += Q.filter('term', field_name='value') # term 查询
    # >>> q &= Q.must_not('match', field_name='value') # match_not 查询
    # # | 表示 或操作
    # >>> q |= Q.filter('term', field_name='value')
    # # 排序 desc 倒叙；asc 顺序
    # >>> sort = Sort(field_name1='asc', field_name2='desc')
    # # 分页
    # >>> pagination = ESPagination()
    # # 根据 指定字段 去重
    # >>> collapse = Collapse('field_name')
    # # 更新 数据
    # >>> updater = Update(field1='value1', field2='value2')
    # # 生成查询语句
    # >>> q(sort=sort, pagination=pagination, collapse=collapse, updater=updater)
    """
    _name_ = 'query'
    Q_ITEM_TYPE = {'term': Term, 'match': Match, 'field_match': FieldMatch, 'range': Range, 'exists': Exists,
                   'wildcard': Wildcard, 'match_phrase': MatchPhrase}
    Q_QUERY_TYPE = {'must': Must, 'filter': Filter, 'should': Should, 'must_not': MustNot}

    def __init__(self, *queries):
        self.queries = list(queries)

    def __add__(self, other):
        return self.__and__(other)

    def __and__(self, other):
        if isinstance(other, self.__class__):
            self.queries.extend(other.queries)
        elif isinstance(other, BaseQuery):
            self.queries.append(other)
        return self

    def __or__(self, other):
        if isinstance(other, BaseQuery):
            self.queries = [Should(Bool(*self.queries), Bool(other))]
        elif isinstance(other, self.__class__):
            self.queries = [Should(Bool(*self.queries), Bool(*other.queries))]
        return self

    def __call__(self,
                 sort: Sort = None,
                 pagination: ESPagination = None,
                 collapse: Collapse = None,
                 updater: Update = None):
        ret = {self._name_: Bool(*self.queries)()}
        if sort:
            ret.update(sort())
        if pagination:
            ret.update(pagination())
        if collapse:
            # 去重
            ret.update(collapse())
        if updater:
            # 更新数据
            ret.update(updater())
        return ret

    @classmethod
    def common(cls, item_typ, query_typ, **kwargs) -> "Q":
        item = cls.Q_ITEM_TYPE[item_typ](Fields(**kwargs))
        return cls(cls.Q_QUERY_TYPE[query_typ](item))

    @classmethod
    def must(cls, item_typ, **kwargs) -> "Q":
        return cls.common(item_typ, 'must', **kwargs)

    @classmethod
    def filter(cls, item_typ, **kwargs) -> "Q":
        return cls.common(item_typ, 'filter', **kwargs)

    @classmethod
    def should(cls, item_typ, **kwargs) -> "Q":
        return cls.common(item_typ, 'should', **kwargs)

    @classmethod
    def must_not(cls, item_typ, **kwargs) -> "Q":
        return cls.common(item_typ, 'must_not', **kwargs)


class SearchSyntax:
    """ 搜索语法 """

    def __init__(self, **commands):
        self.commands = commands

    def deal(self, key: str, sep: str = ':'):
        tmp_key, conditions = key.replace(f'{sep}', f'{sep} '), list()
        if 'AND' in tmp_key:
            conditions.append('AND')
            for item in [i.strip() for i in tmp_key.split('AND') if i]:
                if 'OR' in item:
                    sub_conditions = ['OR']
                    for item in [i.strip() for i in item.split('OR') if i]:
                        tmp = [i.strip() for i in item.split(f'{sep} ') if i]
                        sub_conditions.append({self.commands[tmp[0]]: tmp[1]})
                    conditions.append(sub_conditions)
                else:
                    tmp = [i.strip() for i in item.split(f'{sep} ') if i]
                    conditions.append({self.commands[tmp[0]]: tmp[1]})
        elif 'OR' in tmp_key:
            conditions.append('OR')
            for item in [i.strip() for i in tmp_key.split('OR') if i]:
                tmp = [i.strip() for i in item.split(f'{sep} ') if i]
                conditions.append({self.commands[tmp[0]]: tmp[1]})
        else:
            tmp = [i.strip() for i in tmp_key.split(f'{sep} ') if i]
            if len(tmp) > 1:
                conditions = {self.commands[tmp[0]]: tmp[1]}
            else:
                conditions = ['OR', {'content': key}, {'group_name': key}, {'sender': key}]
        return conditions

    def _analyze_item(self, item: Dict):
        for key, val in item.items():
            if val.startswith('-'):
                return Bool(MustNot(Match(Fields(**{key: val[1:]}))))
            else:
                return Match(Fields(**item))

    def analyze(self, conditions, sub=False):
        if isinstance(conditions, Dict):
            return Filter(self._analyze_item(conditions))

        ctrl, items = conditions[0], list()
        while conditions:
            item = conditions.pop()
            if isinstance(item, List):
                items.append(self.analyze(item, sub=True))
            elif isinstance(item, Dict):
                items.append(self._analyze_item(item))
            else:
                break
        if ctrl == 'AND':
            return Filter(*items)
        elif ctrl == 'OR':
            if sub:
                return Bool(Should(*items))
            else:
                return Should(*items)


class DefaultEsHelper(object):
    """ 一个简单的ES帮助类 """

    def __init__(self, es: Elasticsearch):
        self.es = es
        self.demo = [
            # 线索ID
            KeywordField('clue_id'),
            # 任务ID - message_id
            KeywordField('message_id'),
        ]
        self.mapping_names = ['demo']

    def pre_query(f: Callable):
        """ 查询前检查参数，可以做些其他操作，比如 index 存不存在等 """

        @functools.wraps(f)
        def decorator(self, **kwargs):
            if not kwargs.get('index'):
                raise Exception(f'es.{f.__name__} need param(index)')
            if kwargs.get('body') is None:
                raise Exception(f'es.{f.__name__} need param(body)')
            return f(self, **kwargs)

        return decorator

    @pre_query
    def search(self, **kwargs):
        """ 搜索 """
        params = {
            'body': kwargs['body'],
            'index': kwargs['index'],
            'request_timeout': kwargs.get('request_timeout', 999)
        }

        if kwargs.get('_source'):
            params['_cource'] = kwargs['_source']

        if kwargs.get('doc_type'):
            params['doc_type'] = kwargs['doc_type']

        return Result(self.es.search(**params))

    @pre_query
    def insert(self, **kwargs):
        """ 插入数据 无ID可自动生成ID"""
        params = {
            'index': kwargs['index'],
            'body': kwargs['body'],
            'refresh': kwargs.get('refresh', False)
        }

        if kwargs.get('doc_type'):
            params['doc_type'] = kwargs['doc_type']

        if kwargs.get('id'):
            params['id'] = kwargs['id']

        self.es.index(**params)

    @pre_query
    def bulk_insert(self, **kwargs):
        """ 批量插入 """
        actions = list()
        for data in kwargs['body']:
            actions.append({
                '_op_type': 'index',
                '_index': kwargs['index'],
                **data})

        # 批量提交更新
        threads, act_num = 5, len(actions)
        chunk_size = act_num // threads if act_num > 500 else act_num
        for success, info in helpers.parallel_bulk(
                self.es,
                actions=actions,
                refresh=True,
                thread_count=threads,
                chunk_size=chunk_size):
            if not success:
                logging.error(f'insert error: {info}')

    def reindex(self, src, dst, filters, size=200):
        _data = Result(self.es.search(body=filters, index=src, scroll='5m', size=size))

        body = list()
        while _data.hits():
            for s in _data.hits():
                tmp = dict(s['_source'])
                tmp['_id'] = s['_id']
                body.append(tmp)
            if len(body) > 500:
                self.bulk_insert(index=dst, body=body)
                body = list()
            _data = Result(self.es.scroll(scroll_id=_data.scroll_id(), scroll='5m'))
        if body:
            self.bulk_insert(index=dst, body=body)

    @pre_query
    def create(self, **kwargs):
        """ 插入数据 必须手动加入ID """
        if not kwargs.get('id'):
            raise Exception('es.create need param(id)')

        params = {
            'index': kwargs['index'],
            'body': kwargs['body'],
            'id': kwargs['id'],
            'refresh': kwargs.get('refresh', False)
        }

        if kwargs.get('doc_type'):
            params['doc_type'] = kwargs['doc_type']

        self.es.create(**params)

    @pre_query
    def update_by_query(self, **kwargs):
        """ 根据查询更新 """
        if not kwargs.get('data') or not isinstance(kwargs['data'], Dict):
            raise Exception('es.update_by_query need param(data) is Dict')

        result: Result = self.search(_source='_id,_type,_index', **kwargs)

        actions = list()
        for item in result.hits():
            actions.append({
                '_op_type': 'update',
                '_index': item['_index'],
                '_type': item['_type'],
                '_id': item['_id'],
                **kwargs['data']})

        # 批量提交更新
        threads, act_num = 5, len(actions)
        chunk_size = act_num // threads if act_num > 500 else act_num
        return [i for i in helpers.parallel_bulk(
            self.es,
            actions=actions,
            refresh=True,
            thread_count=threads,
            chunk_size=chunk_size)]

    @pre_query
    def update_by_script(self, **kwargs):
        """ 当数据量大时，比较慢 """
        if not kwargs['body'].get('script') or not isinstance(kwargs['body']['script'], Dict):
            raise Exception('es.update_by_script need param(body.script) is Dict')

        params = {
            'index': kwargs['index'],
            'body': kwargs['body'],
            'refresh': kwargs.get('refresh', False),
            'request_timeout': 999
        }

        self.es.update_by_query(**params)

    @pre_query
    def exists(self, **kwargs):
        """ 是否存在 """
        kwargs['body']['size'] = 0
        return self.search(**kwargs).total() > 0

    @classmethod
    def del_mapping(cls, es: Elasticsearch, index: str):
        if es.indices.exists(index):
            es.indices.delete(index)

    @classmethod
    def create_mapping(cls, es: Elasticsearch, properties: List, index: str):
        """
        # >>> properties = [
        # >>>     KeywordField('email'),
        # >>>     TextField('content'),
        # >>>     KeywordField('author'),
        # >>>     IntegerField('read_num')
        # >>> ]
        """
        if not es.indices.exists(index):
            mappings = {'mappings': {'properties': dict()}}
            properties_ = mappings['mappings']['properties']
            for item in properties:
                properties_.update(item.get_field())
            es.indices.create(index=index, body=mappings)

    @classmethod
    def add_alias(cls, es: Elasticsearch, index, alias, is_write_index=True):
        action = [{'add': {'index': index, 'alias': alias, 'is_write_index': is_write_index}}]
        es.indices.update_aliases(body={'actions': action})

    def init_mappings(self, mapping_names=None):
        """ 初始化 mappings """
        if not (mapping_names and isinstance(mapping_names, list)):
            mapping_names = self.mapping_names

        for index in mapping_names:
            self.__class__.del_mapping(self.es, index)
            properties = getattr(self, index, None)
            if properties:
                self.__class__.create_mapping(self.es, properties, index)
