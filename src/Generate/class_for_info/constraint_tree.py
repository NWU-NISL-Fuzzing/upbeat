class ConstraintTreeList:
    def __init__(self, logicalOp: str, treeList: list):
        self.logicalOp = logicalOp
        self.treeList = treeList
        self.argsDict = {}
    
    def printAll(self):
        # print("logicalOp:"+self.logicalOp)
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
    def is_equal_tree(self, tree1: ConstraintTree, tree2: ConstraintTree):
        return (tree1.rootNode == tree2.rootNode) and (tree1.leftNode == tree2.leftNode) and (
                tree1.rightNode == tree2.rightNode)

    def cover_same_node(self, one_cons_tree, certain_value, all_tree_list):
        uncertain_node = one_cons_tree
        for one_cons_tree in all_tree_list:
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
                if one_cons_tree.leftNode.leftNode == one_cons_tree.leftNode.rightNode == True:
                    one_cons_tree.leftIsCertain = True
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
                if one_cons_tree.rightNode.leftNode == one_cons_tree.rightNode.rightNode == True:
                    one_cons_tree.rightIsCertain = True
