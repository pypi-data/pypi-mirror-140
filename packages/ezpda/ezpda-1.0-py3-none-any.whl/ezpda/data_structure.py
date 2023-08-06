from collections import namedtuple
from math import inf

import networkx as nx

state_change_detail = namedtuple("state_mat_item", ("change_condition", "callback", "priority"))


class condition_pairs(object):
    def __init__(self, condition, callback, priority, name=None):
        """
        单个状态内的 情况——方法对应
        :param condition: 情况（接收任意类型数据）
        :param callback: 满足情况的回调函数（一个callable对象）
        :param priority：同时满足多种情况时的回调优先级(越大越优先)
        """
        self.condition = condition
        self.callback = callback
        self.priority = priority
        self._name = id(self) if name is None else name

    def check_condition(self, condition):
        """
        情况就是这么个情况，具体什么情况还得看情况
        检查是不是这个情况
        :param condition:
        :return:
        """
        if condition == self.condition:
            return True
        return False

    def __str__(self):
        return str(self.condition) + "-->" + str(self._name) + " " + str(self.priority) + "\n"

    def __repr__(self):
        return str(self)


class state(object):
    """
    单个状态类，可以添加状态内的条件及回调函数(状态转移函数不在此处定义)
    """

    def __init__(self, *args, **kwargs):
        self._name = id(self)
        self.condition_pairs = list(args)
        self.s_stack = []
        try:
            self.name = kwargs["name"]
        except:
            self.name = self._name

    def add_condition_pairs(self, *args):
        self.condition_pairs += list(args)

    def __add__(self, other):
        self.add_condition_pairs(other)
        return self

    def condition_check(self, condition):
        self.s_stack = []
        s_stack = []
        for pair in self.condition_pairs:
            if pair.check_condition(condition):
                s_stack.append(pair)  # 添加符合条件的情况（由于PDA一次只有一个state所以说可以直接运行）
        for i in range(len(s_stack)):  # 按照callback_pair优先级排序
            for j in range(len(s_stack)):
                if s_stack[j].priority < s_stack[i].priority:
                    s_stack[j], s_stack[i] = s_stack[i], s_stack[j]
        self.s_stack += s_stack

    def _exe_callback(self):
        for pair in self.s_stack:
            pair.callback()

    def update_condition(self, new_condition):
        self.condition_check(new_condition)
        self._exe_callback()

    def __str__(self):
        res = ""
        c = 0
        for pair in self.condition_pairs:
            c += 1
            if c % 5 == 0:
                res += str(pair) + "\n"
            else:
                res += str(pair)
        return "state_func[" + "\n" + res + "]"

    def __repr__(self):
        return str(self)


class state_table(list):
    def __init__(self, *args):
        """
        状态转移表，类似节点导纳矩阵，可以通过三个变量(当前状态，条件状态，栈弹出状态)确定当前情况的转移确定函数
        构造：添加连接类型和栈来确定连接关系，自动构建3维邻接矩阵，形成状态转移表
        :param args:状态类的集合（传入时状态没有任何连接）
        :param kwargs:
        """

        self.state = list(args)
        list.__init__([])
        super(state_table, self).__init__(
            [[[state_change_detail(change_condition=None, callback=lambda: True, priority=-inf) for _ in
               range(len(args))]
              for __ in range(len(args))] for ___ in range(len(args))])
        self.stack = []
        self.graph = nx.MultiGraph()
        for x in self.state:
            self.graph.add_node(x.name)

    def _real_location(self, item):
        return self.state.index(item)

    @staticmethod
    def _nd_list(n, init_value):
        """在此次
        生成一个n维的矩阵
        :param n:
        :param init_value:
        :return:
        """
        c = 0
        temp = [init_value for _ in range(n)]
        while c < n - 1:
            temp = [temp for _ in range(n)]
            c += 1

        return temp

    def set_link(self, now_state: state, next_state: state, stack_state: state, state_mat_items: state_change_detail):
        """
        增加一个转移方式
        :param state_mat_items: 转移矩阵内部的元素，包括转移条件， 回调函数，优先级
        :param now_state:
        :param next_state:
        :param stack_state:栈中弹出的状态
        :return:
        """
        now_loc = self._real_location(now_state)
        next_loc = self._real_location(next_state)
        stack_loc = self._real_location(stack_state)

        self[now_loc][next_loc][stack_loc] = state_mat_items  # 更新三维矩阵对应元素
        self.graph.add_edge(now_state.name, next_state.name)  # 更新画图

    def add_new_state(self, new_state):  # 添加新状态（一个）
        self.state.append(new_state)
        return state_table(*self.state)

    def __add__(self, other):
        return self.add_new_state(other)

    def __str__(self):
        res = ""
        for x in self:
            res += str(x) + "\n"
        return res

    def __repr__(self):
        return str(self)

    def add_condition_pair(self, now_state, condition_pair):
        self.state[self.state.index(now_state)].add_condition_pairs(condition_pair)
