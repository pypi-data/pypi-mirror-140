# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     pp
   Description :
   Author :       asdil
   date：          2022/2/28
-------------------------------------------------
   Change Activity:
                   2022/2/28:
-------------------------------------------------
"""
__author__ = 'Asdil'
import timeout_decorator
from py2neo import Graph, Relationship, Node
from py2neo.matching import RelationshipMatcher, NodeMatcher



class Pyneo4j:
    """
    Neo4j类用于
    """

    def __init__(self, url, user, password, database=None):
        """__init__(self):方法用于

        Parameters
        ----------
        url: str
            neo4j服务器地址
        user: str
            用户名
        password: str
            密码
        database : str or None
            数据了名称
        Returns
        ----------
        """
        self.driver = Graph(url, auth=(user, password), name=database)
        self.database = database
        self.node_matcher = NodeMatcher(self.driver)
        self.relationship_matcher = RelationshipMatcher(self.driver)
        self._check_connect()  # 测试连接

    @timeout_decorator.timeout(5)
    def _check_connect(self):
        """_check_connect方法用于测试连接是否成功,否则报错
        """
        self.driver.run("Match () Return 1 Limit 1")

    def create_node(self, labels, parameters, add_uid=False):
        """create_node方法用于创建node节点

        Parameters
        ----------
        labels : list
            标签集合
        parameters: dict
            参数字典
        add_uid: bool
            是否添加uid参数, 它和id(p)是相同的

        Returns
        ----------
        """
        self._check_connect()  # 测试连接
        node = Node(*labels, **parameters)
        self.driver.create(node)
        if add_uid:
            uid = node.identity
            parameters = {'uid': uid}
            node.update(**parameters)
            self.driver.push(node)
        return node

    def update_node(self, node, labels=None, parameters=None,
                    cover_lables=False,
                    cover_parameters=False,
                    add_uid=False):
        """update_node方法用于

        Parameters
        ----------
        node: py2neo.data.Node
            节点对象
        labels : list or None
            标签集合
        parameters: dict or None
            参数字典
        cover_parameters: bool
            是否删除原有的属性，只保留更新的labels, parameters
        cover_lables: bool
            是否删除原有的标签
        add_uid: bool
            是否添加uid

        Returns
        ----------
        """
        self._check_connect()  # 测试连接
        if cover_parameters:
            for key in node.keys():
                del node[key]
        if cover_lables:
            node.clear_labels()
        if add_uid:
            parameters['uid'] = node.identity
        if labels:
            node.update_labels(*labels)
        if parameters:
            node.update(**parameters)
        self.driver.push(node)
        return node

    def del_node(self, node=None, labels=None, id=None, uid=None):
        """del_node方法用于删除节点

        Parameters
        ----------
        node: py2neo.data.Node
            节点对象
        id: int or None
            节点id
        uid: int or None
            节点uid
        labels: str or None
            节点标签集合

        Returns
        ----------
        """
        self._check_connect()  # 测试连接
        if node:
            self.driver.delete(node)
        elif labels:
            labels = ':'.join(labels)
            cyper = f'Match (p:{labels}) Delete p;'
            self.driver.run(cyper)
        elif id:
            cyper = f'Match (p) Where id(p)={id} Delete p;'
            self.driver.run(cyper)
        elif uid:
            cycler = f'Match (p) where p.uid={uid} Delete p;'
            self.driver.run(cycler)

    def create_relationship(self, node1, node2, label='', parameters=None):
        """create_relationship方法用于

        Parameters
        ----------
        node1 : py2neo.data.Node
            节点1
        node2 : py2neo.data.Node
            节点2
        label: str
            节点关系
        parameters: dict or None
            关系属性

        Returns
        ----------
        """
        self._check_connect()  # 测试连接
        relation = Relationship(node1, label, node2, **parameters)
        self.driver.create(relation)
        return relation

    def delete_all(self):
        """delete_all方法用于删除图数据所有数据,慎用"""
        self._check_connect()  # 测试连接
        self.driver.delete_all()

    def run(self, cyper):
        """run方法用于运行cyper

        Parameters
        ----------
        cyper : str
            cyper 语句
        Returns
        ----------
        """
        self._check_connect()  # 测试连接
        cyper = cyper.lower()
        ret = self.driver.run(cyper)
        if 'return' in cyper:
            return ret.to_data_frame()
        return ret

    def delete_relationship(self, label1=[],
                            parameters1={}, r_label=None,
                            label2=[], parameters2={}, delete_node=False):
        """delete_relationship方法用于删除关系或者关系和节点
        db.delete_relationship(label1=['xxx'],
                             parameters1={'a':2},
                            label2=['yyy'],
                            delete_node=True)
        Parameters
        ----------
        label1: list or None
            节点1的标签集合
        parameters1: dict or None
            节点1的属性集合
        label2: list or None
            节点2的标签集合
        parameters2: dict or None
            节点2的属性集合
        r_label:
            关系的标签

        Returns
        ----------
        """
        self._check_connect()  # 测试连接
        node1 = self.node_matcher.match(*label1).where(**parameters1).first()
        node2 = self.node_matcher.match(*label2).where(**parameters2).first()
        relationships = self.relationship_matcher.match([node1, node2], r_type=r_label)
        for relationship in relationships.all():
            self.driver.separate(relationship)

            if delete_node:
                self.driver.delete(node1)
                self.driver.delete(node2)

    def update_relationship(self, id=None, label1=[], parameters1={},
                            r_label=None, label2=[], parameters2={}, new_r_label=None,
                            new_r_parameters={}):
        """update_relationship方法用于更新关系

        Parameters
        ----------
        id: int or None
            关系的id
        label1: list or None
            节点1的标签集合
        parameters1: dict or None
            节点1的属性集合
        label2: list or None
            节点2的标签集合
        parameters2: dict or None
            节点2的属性集合
        r_label:
            关系的标签
        new_r_label: str or None
            新的关系标签
        new_r_parameters: dict or None
            新的关系属性

        Returns
        ----------
        """
        def combine_dict(d1, d2):
            for key in d2:
                if key not in d1:
                    d1[key] = d2[key]
            return d1
        self._check_connect()  # 测试连接
        if id:
            cyper = f'match g=(node1)-[r]->(node2) where id(r)={id} return g'
            graph = self.driver.evaluate(cyper)
            relationship = graph.relationships[0]
            node1, node2 = graph.nodes
            if new_r_label:
                parameters = dict(relationship)
                new_r_parameters = combine_dict(new_r_parameters, parameters)
                # 删除关系
                self.driver.separate(relationship)
                self.create_relationship(node1, node2, new_r_label, new_r_parameters)
            else:
                relationship.update(new_r_parameters)
                self.driver.push(relationship)
        else:
            node1 = self.node_matcher.match(*label1).where(**parameters1).first()
            node2 = self.node_matcher.match(*label2).where(**parameters2).first()
            relationships = self.relationship_matcher.match([node1, node2], r_type=r_label)
            for relationship in relationships.all():
                if new_r_label:
                    parameters = dict(relationship)
                    new_r_parameters = combine_dict(new_r_parameters, parameters)
                    # 删除关系
                    self.driver.separate(relationship)
                    self.create_relationship(node1, node2, new_r_label, new_r_parameters)
                else:
                    relationship.update(new_r_parameters)
                    self.driver.push(relationship)
