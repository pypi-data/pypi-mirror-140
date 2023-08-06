import random
import matplotlib.pyplot as plt
import uploadtool
from ezpda.data_structure import *


class pda(state_table):
    def __init__(self, *args):
        super(pda, self).__init__(*args)
        self.now_state = None
        self.data_stack = []
        self.next = None
        self.init_sate = None
        self.color = []

    def _get_color(self, num):  # 随机生成一些颜色
        res = []
        for _ in range(num):
            res.append((random.randint(30, 100) / 100, random.randint(40, 100) / 100, random.randint(0, 100) / 100))
        self.color = res

    def set_init_state(self, init_state, init_condition):
        if self.now_state is not None:  # 初始化之后就不用初始化了
            return
        assert init_state in self.state, "初始状态必须添加"
        self.now_state = init_state
        self.now_state.condition_check(init_condition)  # 添加初始状态
        self.init_sate = init_state
        self.stack.append(init_state)

    def _receive_data(self, data, pop_now=True):
        """
        接收信息
        :param data:
        :return:
        """
        action_stack = []
        now_action = None
        if pop_now:
            prev_data = self.stack.pop()  # 弹出栈内元素（下推自动机定义）
        else:
            prev_data = self.stack[-1]  # 比较好玩的下推自动机（可以设置不弹出）
        prev_data_index = self.state.index(prev_data)
        now_index = self.state.index(self.now_state)
        if now_index is None:
            self.stack.append(self.now_state)
            return  # 没有这个状态则直接返回
        for x in range(len(self[0])):
            now_check = self[now_index][x][prev_data_index]
            if now_check.change_condition == data:  # 状态转移条件判断
                if self.next is None:
                    now_action = now_check
                    self.next = self.state[x]
                elif self.next.priority < now_check.priority:  # 判断是否满足优先级，如果满足则高优先级的状态转移优先
                    self.next = self.state[x]
                    now_action = now_check
                if now_action:
                    action_stack.append(now_action)  # 将转移时的回调函数函数最先放入栈
                #  print("{}-->{}".format(self.now_state, self.next))
                self.now_state = self.next  # 进行状态转移

                self.next = None  # 重置下一步
                self.stack.append(self.now_state)  # 将当前状态放入栈

            else:
                self.stack.append(self.now_state)  # 没有转移则放回去
        self.now_state.condition_check(data)
        action_stack += self.now_state.s_stack
        return action_stack

    def update_condition(self, conditions):
        """
        执行接收到的信息
        :return:
        """
        actions = []
        if not self.init_sate:  # 检查是否设置初始节点
            raise Exception("没有初始化")
        if isinstance(conditions, (list, tuple)):
            for condition in conditions:
                data = self._receive_data(condition)
                if data is not None:
                    actions += data  # 首先将操作依次入栈
        else:
            actions += self._receive_data(conditions)
        for action in actions:
            action.callback()  # 执行操作

    def plot(self):
        self._get_color(len(self.state))  # 获取颜色
        nx.draw(self.graph, node_color=self.color, with_labels=True, node_size=1200, arrows=True)
        plt.show()

    def __str__(self):
        self.plot()
        return ""


if __name__ == "__main__":
    data_flow = (
        "change3", "激活a", "不激活a", ["a", 3, "触发"], ["a", 1, "触发"], ["a", 2, "触发"], 3.14, 114514, "change2", "change3",
        "change4", 114514)
    a = condition_pairs("激活a", lambda: print("a触发"), 1, name="执行一个回调函数")
    a1 = condition_pairs(["a", 1, "触发"], lambda: print("a1触发"), priority=2, name="执行另一个回调函数")
    a3 = condition_pairs(3.14, lambda: print(3.141592653689793), priority=3)
    a4 = condition_pairs(114514, lambda: print(1919810), priority=5)
    b = state(a, a1, a3, a4, name="state1")
    b1 = state(a, a1, a4, name="state2")
    b2 = state(a, a4, name="state3")
    b3 = state(a, a3, name="state4")
    b4 = state(a1, a3, name="state5")
    b5 = state(a1, a4, a, name="state6")
    g = pda(b, b1, b2, b3, b4, b5)
    bb2_item = state_change_detail(change_condition="change1", callback=lambda: print("状态从b到b2"), priority=10)
    bb3_item = state_change_detail(change_condition="change2", callback=lambda: print("状态从b2到b"), priority=11)
    b2b3_item = state_change_detail(change_condition="change2", callback=lambda: print("状态从b到b2(高优先级，栈元素为b1)"),
                                    priority=999)
    bb4_item = state_change_detail(change_condition="change4", callback=lambda: print("状态从b到b5"), priority=10)
    bb5_item = state_change_detail(change_condition="change6", callback=lambda: print("状态从b1到b5"), priority=10)
    g.set_init_state(b, "222")
    g.set_link(b, b2, b, bb2_item)
    g.set_link(b2, b, b2, b2b3_item)
    g.set_link(b2, b, b1, bb3_item)
    g.set_link(b2, b5, b1, bb4_item)
    g.set_link(b1, b5, b3, bb5_item)
    g.set_link(b2, b5, b5, bb3_item)
    g.set_link(b2, b3, b2, bb3_item)
    g.set_link(b4, b3, b3, bb3_item)
    g.set_link(b4, b, b3, bb3_item)
    g.set_link(b, b5, b3, bb3_item)
    g.update_condition(data_flow)
    print(g)
