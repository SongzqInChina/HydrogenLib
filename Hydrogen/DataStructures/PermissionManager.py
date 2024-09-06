from abc import abstractmethod, ABC


class PermissonStruct(ABC):
    @abstractmethod
    def __eq__(self, other):
        ...


class PermissionBaseError(BaseException):
    ...


class PermissionObjectExistsError(PermissionBaseError):
    def __init__(self, obj):
        self.error_obj = obj

    def __str__(self):
        return f"Permission object exists(Type: {self.error_obj.__class__.__name__})"


class PermissionNameNotFoundError(PermissionBaseError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Permission name not found(Name: {self.name})"


class PermissionSameNameError(PermissionBaseError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Permission name is same(Name: {self.name})"


class PermissionSameTypeError(PermissionBaseError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Permission name is same(Name: {self.name})"


def merge_roles(*roles):
    role = Role()
    for i in roles:
        role.merge(i)
    return role


def one_of_set(setobj, value):
    if value not in setobj:
        raise KeyError(value)
    x = list(setobj & {value})
    return x[0]


class Role:
    def __init__(self, permit_opts=None, prohibit_opts=None):
        if permit_opts is None:
            permit_opts = set()
        if prohibit_opts is None:
            prohibit_opts = set()

        self.permit_opts = set(permit_opts)
        self.prohibit_opts = set(prohibit_opts)

    def _process(self):
        self.permit_opts -= (self.permit_opts & self.prohibit_opts)

    def check(self, opt):
        return opt in self.permit_opts and opt not in self.prohibit_opts

    def prohibit(self, opt):
        self.prohibit_opts.add(opt)
        self._process()

    def permit(self, opt):
        self.prohibit_opts -= {opt}
        self.permit_opts.add(opt)
        self._process()

    def merge(self, other):
        self.permit_opts += other.permit_opts
        self.prohibit_opts += other.prohibit_opts
        self._process()


class User(PermissonStruct):
    def __init__(self, name, roles=None):
        if roles is None:
            roles = set()

        self.name = name
        self.roles = set(roles)

        self.groups = set()
        self.domains = set()

        self.last_permission = Role()
        self.update()

    def check(self, opt):
        """
        权限判定机制：拒绝权限大于允许权限
        :param opt: 检查操作
        :return: Bool
        """
        return self.last_permission.check(opt)

    def add_role(self, role):
        self.roles.add(role)

    def remove_role(self, role):
        self.roles -= {role}

    def join_domain(self, domain):
        self.domains.add(domain)

    def leave_domain(self, domain):
        self.domains -= {domain}

    def join_group(self, group):
        self.groups.add(group)

    def leave_group(self, group):
        self.groups -= {group}

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name

        return self.name == other

    def update(self):
        last_permission = merge_roles(self.roles)

        for g in self.groups:
            last_permission.merge(g.last_permission)

        for d in self.domains:
            last_permission.merge(d.last_permission)

        self.last_permission = last_permission


class Group(PermissonStruct):
    def __init__(self, name, roles=None):
        if roles is None:
            roles = set()

        self.name = name
        self.roles = set(roles)

        self.users = set()
        self.domains = set()

        self.last_permission = Role()

    def check(self, opt):
        return self.last_permission.check(opt)

    def add_user(self, user):
        self.users.add(user)
        user.add_group(self)

    def add_role(self, role):
        self.roles.add(role)

    def remove_role(self, role):
        self.roles -= {role}

    def remove_user(self, user):
        self.users -= {user}
        user.leave_group(self)

    def join_domain(self, domain):
        self.domains.add(domain)

    def leave_domain(self, domain):
        self.domains -= {domain}

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return self.name == other

    def update(self):
        last_permission = merge_roles(self.roles)

        for d in self.domains:
            last_permission.merge(d.last_permission)

        self.last_permission = last_permission


class Domain(PermissonStruct):
    def __init__(self, name, roles=None):
        if roles is None:
            roles = set()

        self.name = name
        self.roles = set(roles)

        self.users = set()
        self.groups = set()

        self.last_permission = Role()

    def update(self):
        """
        对于顶级结构“域”来说，不需要考虑上层结构引发的权限变更
        :return: 
        """
        self.last_permission = self.roles
        pass

    def check(self, opt):
        return all(role.check(opt) for role in self.roles)

    def add_user(self, user):
        self.users.add(user)

    def add_group(self, group):
        self.groups.add(group)

    def add_role(self, role):
        self.roles.add(role)

    def remove_role(self, role):
        self.roles -= {role}

    def remove_user(self, user):
        self.users -= {user}

    def remove_group(self, group):
        self.groups -= {group}

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return self.name == other


class PermissionManager:
    def __init__(self, roles=None, users=None, groups=None, domains=None):
        if roles is None:
            roles = set()
        if users is None:
            users = set()
        if groups is None:
            groups = set()
        if domains is None:
            domains = set()
        self.objects = users | groups | domains
        self.default_roles = roles

    def create_user(self, name):
        if name in self.objects:
            raise PermissionObjectExistsError(one_of_set(self.objects, name))
        u = User(name, self.default_roles)
        self.objects.add(u)

    def create_group(self, name):
        if name in self.objects:
            raise PermissionObjectExistsError(one_of_set(self.objects, name))
        g = Group(name, self.default_roles)
        self.objects.add(g)
        return g

    def create_domain(self, name):
        if name in self.objects:
            raise PermissionObjectExistsError(one_of_set(self.objects, name))
        d = Domain(name, self.default_roles)
        self.objects.add(d)
        return d

    def exists(self, name):
        return name in self.objects

    def remove(self, name):
        if name not in self.objects:
            raise Exception("permission object not exists")
        obj = one_of_set(self.objects, name)  # type: PermissonStruct | User | Group | Domain
        self.objects -= {obj}
        if isinstance(obj, User):
            for group in obj.groups:
                group.remove_user(obj)

            for domain in obj.domains:
                domain.remove_user(obj)

        if isinstance(obj, Group):
            for user in obj.users:
                user.groups -= {obj}

            for domain in obj.domains:
                domain.leave_group(obj)

        if isinstance(obj, Domain):
            for user in obj.users:
                user.domains -= {obj}

            for group in obj.groups:
                group.remove_domain(obj)

    def update(self):
        domains = list(i for i in self.objects if isinstance(i, Domain))
        for d in domains:
            d.update()

        groups = list(i for i in self.objects if isinstance(i, Group))
        for g in groups:
            g.update()

        users = list(i for i in self.objects if isinstance(i, User))
        for u in users:
            u.update()

    NonTopTypes = Group | User
    ContainerTypes = Group | Domain

    def let_join(self, obj: NonTopTypes, container: ContainerTypes):
        if type(obj) is type(container):  # type check
            raise Exception("can not join same type")

        if type(obj) is User:
            if type(container) is Group:
                container.add_user(obj)
                obj.join_group(container)

            if type(container) is Domain:
                container.add_user(obj)
                obj.join_domain(container)
        elif type(obj) is Group:
            if type(container) is Domain:
                container.add_group(obj)
                obj.join_domain(container)

    def let_leave(self, obj: NonTopTypes, container: ContainerTypes):
        if type(obj) is type(container):  # type check
            raise Exception("can not leave same type")
        if type(obj) is User:
            if type(container) is Group:
                container.remove_user(obj)
                obj.leave_group(container)

            if type(container) is Domain:
                container.remove_user(obj)
                obj.leave_domain(container)

        elif type(obj) is Group:
            if type(container) is Domain:
                container.remove_group(obj)
                obj.leave_domain(container)

    def get_by_name(self, name):
        return one_of_set(self.objects, name)

    def isinstance(self, name, _type):
        return isinstance(one_of_set(self.objects, name), _type)

    def is_group(self, name):
        return self.isinstance(name, Group)

    def is_user(self, name):
        return self.isinstance(name, User)

    def is_domain(self, name):
        return self.isinstance(name, Domain)

    def check(self, target_name, opt):
        if target_name not in self.objects:
            raise PermissionNameNotFoundError(target_name)

        target = one_of_set(self.objects, target_name)
        return target.check(opt)
