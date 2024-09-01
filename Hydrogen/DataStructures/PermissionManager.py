from typing import overload

from ..Const import PERM_ROLE_DENY, PERM_ROLE_ALLOW
from ..OtherClasses import Namespace


class RoleNotFound(Exception):
    ...


Info = Namespace


class Role:
    def __init__(self, role_dict=None):
        if role_dict is None:
            role_dict = {}
        self.roles = role_dict

    def add(self, name, operation):
        self.roles[name] = operation

    def set(self, name, operation):
        self.roles[name] = operation

    def delete(self, name):
        del self.roles[name]

    def get(self, name):
        return self.roles.get(name)

    def check(self, name):
        if name not in self.roles:
            raise RoleNotFound(f"Cannot find role '{name}'")
        return self.roles[name] == PERM_ROLE_ALLOW

    def __len__(self):
        return len(self.roles)

    def __setitem__(self, key, value):
        self.roles[key] = value

    def __getitem__(self, item):
        return self.roles[item]

    def __delitem__(self, key):
        del self.roles[key]

    def __iter__(self):
        return iter(self.roles)

    def __mul__(self, other):
        return (self.__class__(self.roles.copy()) for i in range(other))


def merge_permission(role1: Role, role2: Role):  # 权限合并
    if len(role2) > len(role1):
        role1, role2 = role2, role1

    total = Role()

    for i in role2:
        if i not in role1:
            total.add(i, role2[i])
        else:
            if role1.get(i) == PERM_ROLE_DENY:
                total.add(i, PERM_ROLE_DENY)
            else:
                total.add(i, role2[i])

    return total


class User:
    def __init__(self, name, usr_roles=None):
        if usr_roles is None:
            usr_roles = Role()
        self.usr_roles = usr_roles
        self.info = Info(None, name=name)
        self.groups = []
        self.domains = []

    def add_role(self, name, operation):
        self.usr_roles.add(name, operation)

    def delete_role(self, name):
        self.usr_roles.delete(name)

    def check(self, name):
        return self.usr_roles.check(name)


class Group:
    def __init__(self, name, group_roles=None):
        if group_roles is None:
            group_roles = Role()

        self.group_roles = group_roles
        self.info = Info(None, name=name)
        self.members = []
        self.domains = []

    def add_user(self, user):
        self.members.append(user)

    def delete_user(self, user):
        self.members.remove(user)

    def add_role(self, name, operation):
        self.group_roles.add(name, operation)

    def delete_role(self, name):
        self.group_roles.delete(name)


class Domain:
    def __init__(self, name, domain_roles=None):
        if domain_roles is None:
            domain_roles = Role()

        self.domain_roles = domain_roles
        self.groups = []  # type: list[Group]
        self.members = []  # type: list[User]

        self.info = Info(None, name=name)

    def add_group(self, group):
        self.groups.append(group)

    def delete_group(self, group):
        self.groups.remove(group)

    def add_role(self, name, operation):
        self.domain_roles.add(name, operation)

    def delete_role(self, name):
        self.domain_roles.delete(name)

    def add_user(self, name):
        return self.members.append(name)

    def delete_user(self, name):
        self.members.remove(name)

    def check(self, name):
        try:
            return all(
                [self.domain_roles.check(name), *[group.check(name) for group in self.groups]]
            )
        except (RoleNotFound, PermissionError) as e:
            raise e


class PermissionManager:


    def __init__(self):
        self.domains = {}  # type: dict[str, Domain]
        self.groups = {}  # type: dict[str, Group]
        self.users = {}  # type: dict[str, User]

    def create_user(self, name: str):
        """
        创建并添加一个用户类型
        """
        if name in self.users:
            raise ValueError("User already exists")
        self.users[name] = User(name)

    def add_user(self, obj: User):
        if obj.info.name in self.groups:
            raise ValueError("User already exists")

        self.users[obj.info['name']] = obj

    def create_group(self, name: str):
        if name in self.groups:
            raise ValueError("Group already exists")

        self.groups[name] = Group(name)

    def add_group(self, obj: Group):
        name = obj.info['name']
        if name in self.groups:
            raise ValueError("Group already exists")

        self.groups[name] = obj

    def create_domain(self, name: str):
        if name in self.domains:
            raise ValueError("Domain already exists")

        self.domains[name] = Domain(name)

    def add_domain(self, obj: Domain):
        name = obj.info['name']
        name_bytes = name.encode()
        if name in self.domains:
            raise ValueError("Domain already exists")

        self.domains[name] = obj

    @overload
    def group(self, group_name):
        ...

    @overload
    def group(self, group_name, user_name, operation):
        ...

    def group(self, group_name, user_name=None, operation=None):
        if group_name not in self.groups:
            raise ValueError("Group not found")
        if user_name is None and operation is None:
            return self.groups.get(group_name)

        else:
            if user_name is None or operation is None:
                raise ValueError("user_name and operation cannot be None")

            if operation == 'add':
                self.groups[group_name].add_user(self.users[user_name])


if __name__ == '__main__':
    role1, role2 = Role()*2
    role1.add('test', PERM_ROLE_ALLOW)
    role2.add('test', PERM_ROLE_DENY)
    print(merge_permission(role1, role2))
