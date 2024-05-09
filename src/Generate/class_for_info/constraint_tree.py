class ConstraintTreeList:
    def __init__(self, logicalOp: str, treeList: list):
        self.logicalOp = logicalOp
        self.treeList = treeList
        self.argsDict = {}
    
    def printAll(self):
        print("logicalOp:"+self.logicalOp)
        for tree in self.treeList:
            tree.printAll()


class ConstraintTree:
    def __init__(self, rootNode: str):
        self.rootNode = rootNode
        self.leftNode = None
        self.rightNode = None
        self.leftIsCertain = None
        self.rightIsCertain = None
    
    def copyTree(self):
        tmp = ConstraintTree(self.rootNode)
        tmp.leftNode = self.leftNode
        tmp.rightNode = self.rightNode
        tmp.leftIsCertain = self.leftIsCertain
        tmp.rightIsCertain = self.rightIsCertain
        return tmp
        
    def setLeftNode(self, leftNode, leftIsCertain):
        self.leftNode = leftNode
        self.leftIsCertain = leftIsCertain

    def setRightNode(self, rightNode, rightIsCertain):
        self.rightNode = rightNode
        self.rightIsCertain = rightIsCertain
    
    def setNode(self, selectedNode, nodeIsCertain, rightOrLeft):
        if rightOrLeft == "right":
            self.rightNode = selectedNode
            self.rightIsCertain = nodeIsCertain
        elif rightOrLeft == "left":
            self.leftNode = selectedNode
            self.leftIsCertain = nodeIsCertain
    
    def setRightCertain(self, selectedContent):
        if not self.rightIsCertain:
            self.rightIsCertain = True
        else:
            raise RuntimeError("Set a certain node to certain!")
    
    def isLeafNode(self):
        return (self.leftNode and self.rightNode) == None

    def printAll(self):
        if self.isLeafNode():
            print("here is a leaf node:"+self.rootNode)
        else:
            print(  "root node:"+str(self.rootNode)+
                    "\nleftNode:"+str(self.leftNode.rootNode)+"--"+str(self.leftIsCertain)+
                    "\nrightNode:"+str(self.rightNode.rootNode)+"--"+str(self.rightIsCertain)
            )


class ConstraintTreeOp:
    # def __init__(self, all_tree_list: list):
    #     self.all_tree_list = all_tree_list

    def is_equal_tree(self, tree1: ConstraintTree, tree2: ConstraintTree):
        """ 判断两个树是否完全相等 """

        return (tree1.rootNode == tree2.rootNode) and (tree1.leftNode == tree2.leftNode) and (
                tree1.rightNode == tree2.rightNode)

    def cover_same_node(self, one_cons_tree, certain_value, all_tree_list):
        """ 遍历树列表，将所有树与uncertain_node一样的节点赋为certain_value """

        uncertain_node = one_cons_tree
        # print("---------start----------")
        for one_cons_tree in all_tree_list:
            # print("now check in cover_same_node:\nthis:")
            # one_cons_tree.printAll()
            # print("sample:")
            # uncertain_node.printAll()
            # 首先检查左节点
            if one_cons_tree.leftNode.isLeafNode():
                if self.is_equal_tree(one_cons_tree.leftNode, uncertain_node):
                    # print("==match left! start to cover.")
                    one_cons_tree.leftNode = ConstraintTree(certain_value)
                    one_cons_tree.leftIsCertain = True
            else:
                if self.is_equal_tree(one_cons_tree.leftNode.leftNode, uncertain_node):
                    # print("==match left->left! start to cover.")
                    one_cons_tree.leftNode.leftNode = ConstraintTree(certain_value)
                    one_cons_tree.leftNode.leftIsCertain = True
                elif self.is_equal_tree(one_cons_tree.leftNode.rightNode, uncertain_node):
                    # print("==match left->right! start to cover.")
                    one_cons_tree.leftNode.rightNode = ConstraintTree(certain_value)
                    one_cons_tree.leftNode.rightIsCertain = True
                # 如果子树的两个节点都已被覆盖，需要将子树的根节点设置为“值确定”
                if one_cons_tree.leftNode.leftNode == one_cons_tree.leftNode.rightNode == True:
                    one_cons_tree.leftIsCertain = True
            # 其次检查右节点
            if one_cons_tree.rightNode.isLeafNode():
                if self.is_equal_tree(one_cons_tree.rightNode, uncertain_node):
                    # print("==match right! start to cover.")
                    one_cons_tree.rightNode = ConstraintTree(certain_value)
                    one_cons_tree.rightIsCertain = True
            else:
                if self.is_equal_tree(one_cons_tree.rightNode.leftNode, uncertain_node):
                    # print("==match right->left! start to cover.")
                    one_cons_tree.rightNode.leftNode = ConstraintTree(certain_value)
                    one_cons_tree.rightNode.leftIsCertain = True
                elif self.is_equal_tree(one_cons_tree.rightNode.rightNode, uncertain_node):
                    # print("==match right->right! start to cover.")
                    one_cons_tree.rightNode.rightNode = ConstraintTree(certain_value)
                    one_cons_tree.rightNode.rightIsCertain = True
                # 如果子树的两个节点都已被覆盖，需要将子树的根节点设置为“值确定”
                if one_cons_tree.rightNode.leftNode == one_cons_tree.rightNode.rightNode == True:
                    one_cons_tree.rightIsCertain = True
        # print("---------end------------")

