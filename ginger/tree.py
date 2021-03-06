#!/usr/bin/env python

# Local imports
import toolbox
import odict

import ctypes
import os.path
import logging
import math
import uuid
import re
import numpy
import array
import ROOT
import copy
from .base import Labelled
from .core import AbsWorker, AbsView, Chained, Yield


# _____________________________________________________________________________
#    __  ____  _ __
#   / / / / /_(_) /____
#  / / / / __/ / / ___/
# / /_/ / /_/ / (__  )
# \____/\__/_/_/____/
#

# ---
def _bins2hclass( bins ):
    '''
    Fixed bin width
    bins = (nx,xmin,xmax)
    bins = (nx,xmin,xmax, ny,ymin,ymax)
    Variable bin width
    bins = ([x0,...,xn])
    bins = ([x0,...,xn],[y0,...,ym])

    '''

    from array import array
    if not bins:
        return name, 0
    elif not ( isinstance(bins, tuple) ):
        raise RuntimeError('bin must be an ntuple or an arryas')

    l = len(bins)
    # 1D variable binning
    if l == 1 and isinstance(bins[0], list):
        ndim = 1
        hclass = ROOT.TH1D
        xbins = bins[0]
        hargs = (len(xbins)-1, array('d',xbins))
    elif l == 2 and isinstance(bins[0],list) and isinstance(bins[1],list):
        ndim=2
        hclass = ROOT.TH2D
        xbins = bins[0]
        ybins = bins[1]
        hargs = (len(xbins)-1, array('d',xbins),
                len(ybins)-1, array('d',ybins))
    elif l == 3:
        # nx,xmin,xmax
        ndim=1
        hclass = ROOT.TH1D
        hargs = bins
    elif l == 6:
        # nx,xmin,xmax,ny,ymin,ymax
        ndim=2
        hclass = ROOT.TH2D
        hargs = bins
    else:
        # only 1d or 2 d hist
        raise RuntimeError('What a mess!!! bin malformed!')

    return ndim,hclass,hargs

# _____________________________________________________________________________
def _buildchain(treeName,files):
    tree = ROOT.TChain(treeName)
    for path in files:
        # if # is in the path, it's a zipfile!
        filepath = path if '#' not in path else path[:path.index('#')]
        if not os.path.exists(filepath):
            raise RuntimeError('File '+filepath+' doesn\'t exists')
        tree.Add(path)

    return tree


# ______________________________________________________________________________
#    _____                       __
#   / ___/____ _____ ___  ____  / /__
#   \__ \/ __ `/ __ `__ \/ __ \/ / _ \
#  ___/ / /_/ / / / / / / /_/ / /  __/
# /____/\__,_/_/ /_/ /_/ .___/_/\___/
#                     /_/

class Sample(Labelled):
    '''
    A container for the information to make a TreeWorker

    name: the tree name/path in the rootfile
    files: list of rootfiles
    friends: list of tuples of friend name and files [(fnameA,['c.root','d.root']),('fnameB',[])]
    '''

    #---
    def __init__(self, name, files, preselection='', weight='', scale=1., friends=[]):

        super(Sample,self).__init__('')
        self.name         = name
        self.files        = files
        self.preselection = preselection
        self.weight       = weight
        self.friends      = friends

    #---
    def __repr__(self):
        repr = []
        repr += [self.__class__.__name__+(' '+self.name if self.name else'') + (' also known as '+self._title if self._title else '')]
        repr += ['weight: \'%s\', preselection: \'%s\'' % (self.weight, self.preselection) ]
        repr += ['name: '+self.name+'  files: '+str(self.files) ]
        for i,friend in enumerate(self.friends):
            repr += [('friend: ' if i == 0 else ' '*8)+friend[0]+'  files: '+str(friend[1]) ]

        return '\n'.join(repr)

    __str__ = __repr__

    def dump(self):
        print self.__repr__()

    #---
    def addfriend(self, name, files):
        self.friends.append( (name, files) )


# _____________________________________________________________________________
#    ______             _       __           __
#   /_  __/_______  ___| |     / /___  _____/ /_____  _____
#    / / / ___/ _ \/ _ \ | /| / / __ \/ ___/ //_/ _ \/ ___/
#   / / / /  /  __/  __/ |/ |/ / /_/ / /  / ,< /  __/ /
#  /_/ /_/   \___/\___/|__/|__/\____/_/  /_/|_|\___/_/
#

class TreeWorker(AbsWorker):
    '''
    t = TreeWorker( tree='latino',files=['a.root','b.root'], selection='x <1', weight='3*x', friends=[('bdt',['c.root','d.root']),...]

    t = TreeWorker('latino', ['a.root','b.root'] )
    t.addfriend('bdt',['c.root','d.root'])
    t.weight    = '3*x'
    t.selection = 'x < 1'

    t = TreeWorker.fromSample( sample )
    '''
    _log = logging.getLogger('TreeWorker')
    #---

    # ---
    def __init__(self, name, files, selection='', weight='', friends=None):

        self._chain = _buildchain(name, files)
        # force the loading of the chains
        self._chain.GetEntries()

        self._elist     = None
        self._friends   = []

        self.weight    = weight
        self.selection = selection
        self.scale     = 1.
        if friends: self._link(friends)

    # ---
    @staticmethod
    def fromsample( sample ):
        if not isinstance( sample, Sample):
            raise ValueError('sample must inherit from %s (found %s)' % (Sample.__name__, sample.__class__.__name__) )
        t = TreeWorker( sample.name, sample.files )
        t.selection = sample.preselection
        t.weight    = sample.weight
        return t

    #---
    def __repr__(self):
        return '%s(%s,s=%r,w=%r)' % (self.__class__.__name__,self._chain.GetName(),self._selection,self._weight)

    __str__ = __repr__


    #---
    def _link(self,friends):
        for ftree,ffilenames in friends:
            self.addfriend(free,ffilenames)

    #---
    def __del__(self):
        if hasattr(self,'_friends'):
            for fchain in self._friends:
                self._chain.RemoveFriend(fchain)
                ROOT.SetOwnership(fchain,True)
                del fchain

    #---
    def __getattr__(self,name):
        return getattr(self._chain,name)

    #---
    def _makeentrylist(self,label,cut):

        cutexpr = self._cutexpr(cut)
        self._plot('>>'+label,cutexpr,'entrylist')

        l = ROOT.gDirectory.Get(label)
        # detach the list
        l.SetDirectory(0x0)
        # ensure the ownership
        ROOT.SetOwnership(l,True)

        return l

    #---
    def spawnview(self, cut='', name=None):
        return TreeView(self,cut,name)

    # ---
    def views(self,cuts):
        if not cuts: return odict.OrderedDict()
        views = odict.OrderedDict()
        last = TreeView(self)
        for i,(n,c) in enumerate(cuts.iteritems()):
            m = last.spawn(c,'elist%d' % (i+nv) )
            last = m
            views[n] = m

        return views

    #---
#     def _delroots(self,roots):
#         for l in roots.itervalues():
#             self._log.debug( 'obj before %s',l.__repr__())
#             l.IsA().Destructor(l)
#             self._log.debug( 'obj after  %s', l.__repr__())

    #---
    def addfriend(name,files):
        fchain = _buildchain(ftree,ffilenames)
        if self._chain.GetEntriesFast() != fchain.GetEntries():
            raise RuntimeError('Mismatching number of entries: '
                               +self._chain.GetName()+'('+str(self._chain.GetEntriesFast())+'), '
                               +fchain.GetName()+'('+str(fchain.GetEntriesFast())+')')
        self._chain.AddFriend(fchain)
        self._friends.append(fchain)

    #---
    @property
    def scale(self):
        return self._scale

    #---
    @scale.setter
    def scale(self,s):
        self._scale = float(s)

    #---
    @property
    def weight(self):    return self._weight

    #---
    @property
    def selection(self): return self._selection

    #---
    @weight.setter
    def weight(self,w):
        self._weight = str(w)

    #---
    @selection.setter
    def selection(self,c):
        # shall we work in a protected directory?
        self._selection = str(c)
        # make an entrylist with only the selected events
        name = 'selection'

        self._chain.SetEntryList(0x0)

        if self._elist: del self._elist

        #no selection, stop here
        if not self._selection: return
        self._log.debug( 'applying worker selection %s', self._selection )

        self._chain.Draw('>> '+name, self._selection, 'entrylist')

        elist = ROOT.gDirectory.Get(name)
        # detach the list
        elist.SetDirectory(0x0)
        # ensure the ownership
        ROOT.SetOwnership(elist,True)
        # activate it
        self._chain.SetEntryList(elist)

        self._elist = elist

    #---
    def getminmax(self,var,binsize=0):
        # check var is one of the branches, otherwise it doesn't work
        import math
        xmin,xmax = self._chain.GetMinimum(var),self._chain.GetMaximum(var)

        if binsize > 0:
            xmin,xmax = math.floor(xmin/binsize)*binsize,math.ceil(xmax/binsize)*binsize

        return xmin,xmax

    #---
    def entries(self,cut=None):
        if not cut:
            el = self._chain.GetEntryList()
            if el.__nonzero__(): return el.GetN()
            else:                return self._chain.GetEntries()
        else:
            # super simple projection
            return self._chain.Draw('1.', cut,'goff')

    #---
    def rawdraw(self, *args):
        '''Direct access to the chain Draw. Is it really necessary?'''
        return self._chain.Draw(*args)

    #---
    def setalias(self,name,alias):
        return self._chain.SetAlias(name,alias)

    #---
    def aliases(self):
        return dict([ (n.GetName(),n.GetTitle()) for n in self._chain.GetListOfAliases()])

    #--
    def _cutexpr(self,cuts,addweight=True,addselection=False):
        '''
        makes a cut string or a list of cuts into the cutsrting to be used with
        the TTree, adding the weight
        '''

        # ignore unitary weights
        w = self._weight if addweight and self._weight != '1' else None
        # add selection only if requested
        s = self._selection if addselection else None

        cutlist = [s]+cuts if isinstance(cuts,list) else [s,cuts]
        cutstr = ' && '.join( ['(%s)' % s for s in cutlist if (s and str(s) != '')])

        expr ='*'.join(['(%s)' % s for s in [w,cutstr] if (s and str(s) != '')])

        return expr

    #---
    @staticmethod
    def _projexpr( name, bins = None ):
        '''
        Prepares the target for plotting if the binning is standard (n,min,max)
        then return a string else, it's variable binning, make the htemp and
        return it
        '''
        if not bins:
            return 0,name,None
        elif not isinstance(bins, tuple):
            raise TypeError('bin must be an ntuple or an array')

        l = len(bins)
        # if the tuple is made of lists
#         if l in [1,2] and all(map(lambda o: isinstance(o,list),bins)):
        if (l in [1,2] and all(map(lambda o: isinstance(o,list),bins))) or (l in [3,6]):
            dirsentry = toolbox.TH1AddDirSentry()
            sumsentry = toolbox.TH1Sumw2Sentry()

            # get the hshape
            hdim,hclass,hargs = _bins2hclass( bins )

            # make the histogram
            htemp = hclass(name, name, *hargs)

            return hdim,name,htemp

        else:
            # standard approach, the string goes into the expression
            # WARNING: this way the constuction of the histogram is delegated to TTree::Draw, which produces a TH1F
            # IT would be better to retain the control over the histogram type selection (i.e. being able to make TH1D always)
            # In order to do so, we need to mimik the with which TTree Draw creates its histograms:
            #   - x-check the dimention in varexp and projexp
            #   - initial xmin,xmax (and likewise for y)
            #   - default number of bins
            if l in [1]:
                # nx (free xmin, xmax)
                ndim=1
            elif l in [4]:
                # nx,xmin,xmax,ny (free ymin,ymax)
                ndim=2
            else:
                # only 1d or 2 d hist
                raise RuntimeError('What a mess!!! bin malformed!')

            hdef = '('+','.join([ str(x) for x in bins])+')' if bins else ''
            return ndim,name+hdef,None

    #---
    def _plot(self,varexp, cut, options='', *args, **kwargs):
        '''
        Primitive method to produce histograms and projections
        '''

        if kwargs: print 'kwargs',kwargs
        dirsentry = toolbox.TH1AddDirSentry()
        sumsentry = toolbox.TH1Sumw2Sentry()
        options = 'goff '+options
        self._log.debug('varexp:  \'%s\'', varexp)
        self._log.debug('cut:     \'%s\'', cut)
        self._log.debug('options: \'%s\'', options)

        n = self._chain.Draw(varexp , cut, options, *args, **kwargs)
        h = self._chain.GetHistogram()
        if h.__nonzero__():
#             print h.GetDirectory()
            self._log.debug('entries  %d integral %f', h.GetEntries(), h.Integral())
            h.Scale(self._scale)
            self._log.debug('scale:   %f integral %f', self._scale, h.Integral())
            return h
        else:
            self._log.debug('entries  %d', n)
            return None

    #---
    def yields(self, cut='', options='', *args, **kwargs):
        cut = self._cutexpr(cut)
        # DO add the histogram, and set sumw2 (why not using TH1::Sumw2()?
        dirsentry = toolbox.TH1AddDirSentry(True)
        sumsentry = toolbox.TH1Sumw2Sentry()
        # new name per call or? what about using always the same histogram?
        tname = 'counter' #'counter_%s' % uuid.uuid1()
        # it might look like an overkill, but the double here helps
        counter = ROOT.TH1D(tname,tname,1,0.,1.)
        h = self._plot('0. >> '+tname, cut, options, *args, **kwargs)

        xax = h.GetXaxis()
        err = ctypes.c_double(0.)
        int = h.IntegralAndError(xax.GetFirst(), xax.GetLast(), err)

        return Yield(int,err.value)

    #---
    def plot(self, name, varexp, cut='', options='', bins=None, *args, **kwargs):

        # check the name doesn't contain projection infos
        m = re.match(r'.*(\([^\)]*\))',name)
        if m: raise ValueError('Use bins argument to specify the binning %s' % m.group(1))

        ndim,hstr,htemp = self._projexpr(name,bins)

        cut = self._cutexpr(cut)

        if htemp:
            # do a projection with a target
            # make an unique name (juust in case)
            tname = '%s_%s' % (htemp.GetName(),uuid.uuid1())
            htemp.SetName( tname )
            htemp.SetDirectory( ROOT.gDirectory.func())
            hstr = hstr.replace(name,tname)

            projexp = '%s >> %s' % (varexp,hstr)
            h = self._plot( projexp, cut, options, *args, **kwargs)
            h.SetXTitle(varexp)

            # reset the directory
            h.SetDirectory(0x0)
            h.SetName(name)
        else:
            # let TTree::Draw to create the temporary histogram
            varexp = '%s >> %s' % (varexp,hstr)
            h = self._plot( varexp, cut, options, *args, **kwargs)

        return h

    #---
    def yieldsflow(self, cuts, options=''):
        '''Does it make sense to have a double step?  In a way yes, because
        otherwise one would have to loop over all the events for each step
        '''

        views = self.views(cuts)
        return odict.OrderedDict(
            [( n,v.yields(options=options) ) for n,v in views.iteritems()]
        )

    #---
    def plotsflow(self, name, varexp, cuts, options='', bins=None, *args, **kwargs):

        views = self.views(cuts)
        return odict.OrderedDict(
            [( n,v.plot('%s_%s' % (name,n),varexp,cuts,options,bins) ) for n,v in views.iteritems()]
        )


    #---
    def project(self, h, varexp, cut='', options='', *args, **kwargs):

        # check where we are
        here = ROOT.gDirectory.func()
        hdir = h.GetDirectory()
        tmp = None

        # and if h is connected to a dir
        if not hdir.__nonzero__():
            # null directory: make a temp one to lat TTree::Draw find it
            ROOT.gROOT.cd()
            tmp = 'treeworker_'+str(os.getpid())
            hdir = ROOT.gROOT.mkdir(tmp)
            h.SetDirectory(hdir)

        hdir.cd()

        varexp = '%s >> +%s' % (varexp,h.GetName())
        cut = self._cutexpr(cut)

        hout = self._plot( varexp, cut, options+'goff', *args, **kwargs)

        if hout != h: raise ValueError('What happened to my histogram?!?!')

        # go back home
        here.cd()

        if tmp:
            h.SetDirectory(0x0)
            ROOT.gROOT.rmdir(tmp)

        return h

# _____________________________________________________________________________
#    ________          _     _       __           __
#   / ____/ /_  ____ _(_)___| |     / /___  _____/ /_____  _____
#  / /   / __ \/ __ `/ / __ \ | /| / / __ \/ ___/ //_/ _ \/ ___/
# / /___/ / / / /_/ / / / / / |/ |/ / /_/ / /  / ,< /  __/ /
# \____/_/ /_/\__,_/_/_/ /_/|__/|__/\____/_/  /_/|_|\___/_/
#
class ChainWorker(Chained,AbsWorker):

    def __init__(self,*workers):
        '''  '''
        super(ChainWorker,self).__init__(AbsWorker,*workers)
        self._scale = 1.

    #---
    @property
    def scale(self):
        return self._scale

    #---
    @scale.setter
    def scale(self,s):
        oldscale = self._scale
        newscale = float(s)

        for o in self._objs:
            o.scale *= (newscale/oldscale)

        self._scale = float(s)

    #---
    def spawnview(self, cut='', name=None):
        return ChainView(self,cut,name)

    # is this method really useful?
    def views(self,cuts):

        # put the treeviews in a temporary container
        allviews = [ o.views(cuts) for o in self._objs ]
        # but what we need are the
        alliters = [ v.itervalues() for v in allviews ]

        import itertools
        chainviews=odict.OrderedDict()
        # make an iterator with everything inside
        # cut,tview1,tview2,...,tviewN
        # to repack them as
        # cut,cview
        for it in itertools.izip(cuts,*alliters):

            # create a new view
            cv = ChainView()

            # add all the treeviews
            cv.add( *it[1:] )

            #add it to the list of views
            chainviews[it[0]] = cv

        return chainviews

    @staticmethod
    def fromsamples( *samples ):
        ''' build each sample into a TreeWorker and add them together'''

        trees = [TreeWorker.fromsample(s) for s in samples]
        return ChainWorker(*trees)



# _____________________________________________________________________________
#   ______             _    ___
#  /_  __/_______  ___| |  / (_)__ _      __
#   / / / ___/ _ \/ _ \ | / / / _ \ | /| / /
#  / / / /  /  __/  __/ |/ / /  __/ |/ |/ /
# /_/ /_/   \___/\___/|___/_/\___/|__/|__/
#

# class TreeView(object):
class TreeView(AbsView):
    '''
    A Class to create iews (via TEntryList) on a TreeWorker
    '''
    class Sentry:
        '''
        A class to insert and clean an entrylist from a worker when needed
        '''
        def __init__(self,worker,elist):
            self._worker = worker

            current = self._worker.GetEntryList()

            self._oldlist = current if current.__nonzero__() else 0x0
            if elist: self._worker.SetEntryList(elist)

        def __del__(self):
            # reset the old configuration
            self._worker.SetEntryList(self._oldlist)

    _log = logging.getLogger('TreeView')

    # ---
    def __init__(self, worker=None, cut='', name=None):

        if worker and not isinstance(worker,TreeWorker):
            raise TypeError('worker must ve of class TreeWorker')

        self._worker = worker
        self._cut    = cut
        self._expcut = cut
        self._elist  = None

        # don't build the list if no worker (used by copy)
        if not worker: return
#         if not worker: assert(0)

        # make myself a name if I don't have one
        self._name = name if name else str(uuid.uuid1())
        if cut:
            self._elist = self._worker._makeentrylist(self._name,cut)
        elif self._worker._elist:
            self._elist = self._worker._elist.Clone()
            self._name  = self._elist.GetName()

    #---
    def __copy__(self):
        other             = TreeView()
        other._cut        = copy.deepcopy(self._cut)
        other._expcut     = copy.deepcopy(self._expcut)
        other._worker     = self._worker
        other._elist      = self._elist.Clone() if self._elist else None

#         assert(0)
        return other

    def __deepcopy__(self,memo):
        return self.__copy__()

    # ---
    def __repr__(self):
        return '%s(w=%r,c=%r)' % (self.__class__.__name__,self._worker, self._expcut)

    # ---
    @property
    def name(self):
        return self._name

    @property
    def cut(self):
        return self._cut

    # ---
    def _sentry(self):
        # make a sentry which sets the current entrlylist in the worker and removes it when going out of scope
        return TreeView.Sentry(self._worker,self._elist)

    # ---
    def entries(self,cut=None):
        # get the entries from worker after setting the entrylist
        sentry = self._sentry()
        return self._worker.entries(cut)

    # ---
    def yields(self, cut='', options='', *args, **kwargs):
        # set temporarily my entrlylist
        sentry = self._sentry()
        return self._worker.yields(cut, options, *args, **kwargs)

    # ---
    def plot(self, name, varexp, cut='', options='', bins=None, *args, **kwargs):
        # set temporarily my entrlylist
        sentry = self._sentry()
        return self._worker.plot(name, varexp, cut, options, bins, *args, **kwargs)

    # ---
    def project(self, h, varexp, cut='', options='', *args, **kwargs):
        # set temporarily my entrlylist
        sentry = self._sentry()
        self._worker.project(h, varexp, cut, option, *args, **kwargs)

    # ---
    def rawdraw(self, *args):
        sentry = self._sentry()
        return self._worker.rawdraw(*args)


    # ---
    def spawn(self,cut,name=None):
        # make myself a name if I don't have one
        name = name if name else str(uuid.uuid1())
        # set temporarily my entrlylist
        sentry = self._sentry()
        # create my spawn
        v = TreeView(self._worker, cut, name=name)

        v._expcut = '(%s) && (%s)' % (self._expcut,cut) if self._expcut else cut
        return v

#_______________________________________________________________________________
#    ________          _     _    ___
#   / ____/ /_  ____ _(_)___| |  / (_)__ _      __
#  / /   / __ \/ __ `/ / __ \ | / / / _ \ | /| / /
# / /___/ / / / /_/ / / / / / |/ / /  __/ |/ |/ /
# \____/_/ /_/\__,_/_/_/ /_/|___/_/\___/|__/|__/
#

class ChainView(Chained,AbsView):

    # ---
    def __init__(self,worker=None, cut='',name=None):
        if worker and not isinstance(worker,ChainWorker):
            raise TypeError('worker must ve of class TreeWorker')

        super(ChainView,self).__init__(AbsView)

        # copied from TreeView. Slim it?
        self._worker = worker
        self._cut    = cut
        self._expcut = cut
        self._elist  = None

        # used by copy operations (default constructor)
        if worker is None: return

        views = [t.spawnview(cut,name) for t in worker]
        self.add(*views)

    # ---
    @property
    # copied from TreeView. Move it to AbsView??
    def name(self):
        return self._name

    @property
    # copied from TreeView. Move it to AbsView??
    def cut(self):
        return self._cut

    def __copy__(self):
        objs  = copy.deepcopy(self._objs)
        other = ChainView()
        other.add(*objs)
        return other

    def __deepcopy__(self,memo):
        return self.__copy__()

    # ---
    def spawn(self,*args, **kwargs):

        child = ChainView()

        views = [ o.spawn(*args, **kwargs) for o in self._objs]

        child.add(*views)

        return child
