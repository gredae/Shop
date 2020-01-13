def get_tree(data):
    lists=[]
    tree={}
    for item in data:
        tree[item.id]=item
    for i in data:
        if not i.cate_self:
            lists.append(tree[i.id])
        else:
            parent_id=i.cate_self_id
            if tree[parent_id].cate_self is not list:
                tree[parent_id].cate_self=[]
            tree[parent_id].cate_self.append(tree[i])

    return lists