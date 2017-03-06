import ROOT


# ------------------------------------------------------------------------------
class Directory(object):

    # --------------------------------------------------------------------------
    @property
    def name(self):
        return self._name
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    @property
    def objs(self):
        return {
            k: a for k, a in self.__dict__.iteritems()
            if (not isinstance(a, Directory) and not k[0] == '_')
            # k: a for k, a in self._children.iteritems()
            # if not isinstance(a, Directory)
        }
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    @property
    def dirs(self):
        return {
            k: a for k, a in self.__dict__.iteritems()
            if (isinstance(a, Directory) and not k[0] == '_')
            # k: a for k, a in self._children.iteritems()
            # if isinstance(a, Directory)
        }
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def get(self, name):
        if name[0] == '_':
            return None
        return self.__dict__[name]
        # return self._children[name]
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # def __getattr__(self, name):
        # print '>>>', name
        # try:
            # return self._children[name]
        # except:
            # raise
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __getitem__(self, name):
        return self.get(name)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def show(self, indent=0, level=-1):
        print ' ' * indent + '+', self._name
        for k, a in self.__dict__.iteritems():
        # for k, a in self._children.iteritems():
            if k[0] == '_':
                continue
            if isinstance(a, Directory):
                a.show(indent + 1)
            else:
                print ' ' * (indent + 1) + '-', k, '=', a
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def __init__(self, tdir):
        if not isinstance(tdir, ROOT.TDirectory):
            raise TypeError('Can\t build a Directory from a %s' % tdir.__class__.__name__)

#         dir = Directory(tdir.GetName())
        self._name = tdir.GetName()
        children = {}

        # Retrieve all objects in the current folder
        for k in tdir.GetListOfKeys():
            o = k.ReadObj()
            ROOT.SetOwnership(o, False)
            if k.GetClassName().startswith('TDirectory'):
                o = Directory(o)

            children[k.GetName()] = o

        # self._children = children
        # Add children as object members
        self.__dict__.update(children)
    # --------------------------------------------------------------------------
