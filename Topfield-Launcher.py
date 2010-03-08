#!/usr/bin/env python
# Mark Blakeney, Mar 2010.

'''
Topfield-Launcher connects to a specified ftpd-topfield host
and lists recorded files available on the connected Topfield
PVR. The user can navigate about the PVR directories and
select a file to play to his PC. The Topfield-Launcher will
start the specified media player (VLC is recommended) to
stream the requested file from the remote PVR, to the user's
screen.

Topfield-Launcher also provides the user with the ability to
delete or rename recorded files.
'''

NAME = 'Topfield-Launcher'

LICENCE = '''
Copyright (C) 2010 Mark Blakeney. This program is
distributed under the terms of the GNU General Public
License.

This program is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, either
version 3 of the License, or any later version.

This program is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU General Public License at
<http://www.gnu.org/licenses/> for more details.
'''
# Note vim se tw=60 on above to fit in about window

VERSION = 'Version 1.0'
AUTHOR = 'Mark Blakeney, markb@berlios.de.'
COPYRIGHT = '(C) 2010 Mark Blakeney'
DESCRIPTION = __doc__

# Defaults
PLAYER_Linux = '/usr/bin/vlc'
PLAYER_Windows = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
HOST = '192.168.1.77'
BASEDIR = '/DataFiles'

# Max file len of toppy file (include 4 chars for '.rec' extension)
MAXTITLE = 57 #chars

# Size of bottom select, close buttons
BUTTON_SIZE = (90, 35)

import sys
import subprocess
import platform
import urllib2
import urlparse
import ftplib
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

# Get current time
from datetime import datetime
from dateutil import parser, relativedelta
timenow = datetime.now()
lastyear = timenow + relativedelta.relativedelta(years=-1)

def get_default_player():
    '''Get the default player dependent on platform'''
    if platform.system() == "Windows":
        return PLAYER_Windows

    return PLAYER_Linux

def compute_date(datestr):
    '''Determine fuzzy date from Topfield'''

    # Fuzzy parse the date
    date = parser.parse(datestr)

    # However, if result is in future time then correct fuzzy logic.
    # This happens due to a bug in ftpd-topfield where it reports last
    # years dates as this year (Bug + fix has been reported to msteveb
    # in Jul 2008 who will add to next version).
    if date > timenow:
        date = parser.parse(datestr, default=lastyear)

    return date

def pathjoin(*args):
    '''Join passed dir paths. Target is always linux server.'''
    #return os.path.join(*args)
    return '/'.join(args)

def basename(path):
    '''Compute basename. Target is always linux server.'''
    #return os.path.basename(path)
    return path.rsplit('/', 1)[1] or ''

def dirname(path):
    '''Compute dirname. Target is always linux server.'''
    #return os.path.dirname(path)
    return path.rsplit('/', 1)[0] or '/'

def makeurl(host, path):
    '''Create url given host + path'''
    if (path[0] == '/'):
        pathf = path[1:]
    else:
        pathf = path

    # Build ftp url
    return 'ftp://' + pathjoin(host, pathf)

def play(player, url):
    '''Sends URL to media player'''

    # Split command + arguments into a list. Also add the url
    # argument.
    cmd = str(player).split() + [url]

    try:
        subprocess.call(cmd)
    except Exception, error:
        return str(error)

    return ''

def fetch(url):
    '''Fetch ftp directory listing'''
    try:
        urlf = urllib2.urlopen(url, timeout=5)
    except Exception, error:
        return '', str(error)

    # Return directory list
    dirlist = urlf.readlines()
    urlf.close()
    return dirlist, ''

def delete(url, login=True):
    '''Delete file/path'''

    # Although we use urllib2 to fetch dir listings we can't use it to
    # delete files. We must implement a lower level ftp interface to do
    # that.
    p = urlparse.urlparse(url)
    ftp = ftplib.FTP(p.hostname, str(p.port))

    try:
        if login:
            ftp.login()
        ftp.delete(p.path)
        ftp.quit()

    except ftplib.error_perm, error:

        # Avoid infinite recurse
        if not login:
            return str(error)

        # We sometimes see an error on delete where we are not allowed
        # to login.
        return delete(url, login=False)

    except Exception, error:
        return str(error)

    return ''

def rename(oldurl, newname, login=True):
    '''Rename file'''

    # Although we use urllib2 to fetch dir listings we can't use it to
    # rename files. We must implement a lower level ftp interface to do
    # that.
    old = urlparse.urlparse(oldurl)
    ftp = ftplib.FTP(old.hostname, str(old.port))

    try:
        if login:
            ftp.login()
        ftp.cwd(dirname(old.path))
        ftp.rename(basename(old.path), newname)
        ftp.quit()

    except ftplib.error_perm, error:

        # Avoid infinite recurse
        if not login:
            return str(error)

        # We sometimes see an error on rename where we are not allowed
        # to login.
        return rename(oldurl, newname, login=False)

    except Exception, error:
        return str(error)

    return ''

def namecheck(oldname, newname):
    '''Impose some text limitations on user entered new file name'''

    # Do some basic checks on the new file name ..
    if oldname == newname:
        return 'File name not changed'

    if not newname.endswith('.rec'):
        return 'File name must end with .rec'

    if newname[:-4].find('.') >= 0:
        return 'Extraneous "." in file name'

    if newname.find('/') >= 0:
        return 'File name must not contain a /'

    if len(newname) > MAXTITLE:
        return 'File name %d char[s] too long' % (len(newname) - MAXTITLE)

    # New file name ok
    return ''

class Entries:
    '''Class to manage each directory/file line'''

    @staticmethod
    def build(host, basedir, lines):
        '''Build dir + file list entries'''
        Entries.alllist = []
        Entries.dirlist = []
        Entries.filelist = []

        # For each line returned in ftp dir list ..
        for line in lines:
            line = line.strip()

            if line[0] == 'd':
                # Set directory display
                display = line[59:]

                if display[0] == '.':
                    dir = dirname(basedir)

                    # Don't allow user to go above base directory
                    if dir == '/':
                        continue

                    display = '[../]'
                    up = True
                else:
                    dir = pathjoin(basedir, display)
                    up = False

                    # Always display a '/' at end of directories
                    if display[:-1] != '/':
                        display += '/'

                # Create dir list entry
                ent = Entries('', dir, display)
                ent.up = up
                Entries.dirlist.append(ent)
            else:
                # Set file display
                sizestr, rest = line.split(None, 5)[4:6]
                size = int(sizestr)

                # Mark in-progress recordings
                if size == 0:
                    sizemb = 'RECORDING'
                else:
                    sizemb = str(size / (1024 * 1024))

                datestr = rest[:12]
                filename = rest[13:]

                date = compute_date(datestr)
                datestr = date.strftime('%Y-%m-%d %H:%M %a')
                path = pathjoin(basedir[1:], filename)

                # Create file list entry (and add date attribute for files)
                ent = Entries(path, '', filename[:-4], datestr, sizemb)
                ent.date = date
                Entries.filelist.append(ent)

        # Sort the file list based on date (python 2.4+ feature)
        Entries.filelist.sort(key=lambda x:x.date)

        # Create combined dir + file list for display
        Entries.alllist = Entries.dirlist + Entries.filelist

    def __init__(self, path, dir, display, datestr='', size=''):
        '''Constructor to create dir/file entry'''
        self.path = path
        self.dir = dir
        self.display = display
        self.datestr = datestr
        self.size = size

class AWListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    '''An Auto width mixin list control'''
    def __init__(self, parent, style=wx.LC_REPORT):
        wx.ListCtrl.__init__(self, parent, -1, style=style)
        ListCtrlAutoWidthMixin.__init__(self)

class MyPanel(wx.Panel):
    def __init__(self, parent):
        '''Constructor'''
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.sb = parent.sb

        # Read host, setting default if necessary
        self.cfg = wx.Config(NAME)
        self.host = ''
        if self.cfg.Exists('host'):
            self.host = self.cfg.Read('host')
        if not self.host:
            self.host = HOST

        # Read player command, setting default if necessary
        self.player = ''
        if self.cfg.Exists('player'):
            self.player = self.cfg.Read('player')
        if not self.player:
            self.player = get_default_player()

        # Set default dir to start with
        self.dir = BASEDIR

        # Master vertical box sizer
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Use flex grid for host + dir stuff
        hbox1 = wx.FlexGridSizer(3, 2, 4, 6)

        # Player:
        playlabel = wx.StaticText(self, -1, 'Media Player :')
        self.playent = wx.TextCtrl(self, -1, self.player,
                style=wx.TE_RICH|wx.TE_RICH2|wx.TE_PROCESS_ENTER)
        self.playent.Bind(wx.EVT_TEXT_ENTER, self.newPlayer)
        hbox1.Add(playlabel, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        hbox1.Add(self.playent, 1, wx.EXPAND)

        # Host:
        hostlabel = wx.StaticText(self, -1, 'Topfield FTP Host :')
        self.hostent = wx.TextCtrl(self, -1, self.host,
                style=wx.TE_RICH|wx.TE_RICH2|wx.TE_PROCESS_ENTER)
        self.hostent.Bind(wx.EVT_TEXT_ENTER, self.refresh)
        hbox1.Add(hostlabel, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        hbox1.Add(self.hostent, 1, wx.EXPAND)

        # Directory:
        dirlabel = wx.StaticText(self, -1, 'Directory :')
        self.dirent = wx.StaticText(self, -1, self.dir)
        hbox1.Add(dirlabel, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        hbox1.Add(self.dirent, 1, wx.EXPAND)

        hbox1.AddGrowableCol(1)
        vbox.Add(hbox1, 0, wx.ALL|wx.EXPAND, 5)

        # List of files/dirs ..
        fileslabel = wx.StaticText(self, -1, 'Recorded Files :')
        vbox.Add(fileslabel, 0, wx.LEFT|wx.TOP, 10)
        vbox.Add((-1, 10))

        # Get standard dir and file icons
        dir_norm = wx.ArtProvider.GetIcon(wx.ART_FOLDER,
                wx.ART_CMN_DIALOG, (16, 16))
        dir_up = wx.ArtProvider.GetIcon(wx.ART_GO_DIR_UP,
                wx.ART_CMN_DIALOG, (16, 16))
        file_norm = wx.ArtProvider.GetIcon(wx.ART_GO_FORWARD,
                wx.ART_CMN_DIALOG, (16, 16))
        il = wx.ImageList(16, 16)
        self.dir_norm = il.AddIcon(dir_norm)
        self.dir_up = il.AddIcon(dir_up)
        self.file_norm = il.AddIcon(file_norm)

        # Create a listctrl for file/dir list
        self.list = AWListCtrl(self, style=wx.LC_REPORT|wx.SUNKEN_BORDER|
                wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.list.AssignImageList(il, wx.IMAGE_LIST_SMALL)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.activate)
        self.list.InsertColumn(0, 'Name', width=430)
        self.list.InsertColumn(1, 'Date/Time', width=160)
        self.list.InsertColumn(2, 'Size (MB)', format=wx.LIST_FORMAT_RIGHT)

        vbox.Add(self.list, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        vbox.Add((-1, 15))

        # Bottom buttons
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        btnsel = wx.Button(self, -1, '&Select', size=BUTTON_SIZE)
        btnsel.Bind(wx.EVT_BUTTON, self.activate)
        hbox2.Add(btnsel, 0, wx.LEFT|wx.BOTTOM, 5)

        btndel = wx.Button(self, -1, '&Delete', size=BUTTON_SIZE)
        btndel.Bind(wx.EVT_BUTTON, self.delete)
        hbox2.Add(btndel, 0, wx.LEFT|wx.BOTTOM, 5)

        btnren = wx.Button(self, -1, '&Rename', size=BUTTON_SIZE)
        btnren.Bind(wx.EVT_BUTTON, self.rename)
        hbox2.Add(btnren, 0, wx.LEFT|wx.BOTTOM, 5)

        btnref = wx.Button(self, -1, '&Refresh', size=BUTTON_SIZE)
        btnref.Bind(wx.EVT_BUTTON, self.refresh)
        hbox2.Add(btnref, 0, wx.LEFT|wx.BOTTOM, 5)

        btnclo = wx.Button(self, wx.ID_CLOSE, size=BUTTON_SIZE)
        btnclo.Bind(wx.EVT_BUTTON, self.parent.closeDown)
        hbox2.Add(btnclo, 0, wx.LEFT|wx.BOTTOM, 5)

        vbox.Add(hbox2, 0, wx.ALIGN_CENTER, 10)
        vbox.Add((-1, 5))

        # Now output gui
        self.SetSizer(vbox)
        wx.CallLater(100, self.populate)

    def setHost(self):
        '''Check if new host entered and set it'''
        host = self.hostent.GetValue()
        if host != self.host:
            self.host = host
            self.cfg.Write('host', self.host)
            self.sb.SetStatusText('New host entered: ' + self.host)

    def setPlayer(self):
        '''Check if new player entered and set it'''
        player = self.playent.GetValue()
        if player != self.player:
            self.player = player
            self.cfg.Write('player', self.player)
            self.sb.SetStatusText('New player entered: ' + self.player)

    def newPlayer(self, e):
        '''Called on entry of new player'''
        self.setPlayer()

    def refresh(self, e):
        '''Refresh the display'''
        self.populate()

    def activate(self, e):
        '''Activate an item and/or refresh the display'''
        self.setHost()
        self.setPlayer()
        index = self.list.GetFirstSelected()
        
        # Process an entry if one was selected
        if index >= 0:
            ent = Entries.alllist[index]

            # If this entry has a path then play it
            if ent.path:

                if ent.size == 'RECORDING':
                    self.sb.SetStatusText('ERROR: '
                    'Can not play a recording while still in progress.')
                    return

                url = makeurl(self.host, ent.path)
                self.sb.SetStatusText('Playing ' + url)
                error = play(self.player, url)

                if error:
                    self.sb.SetStatusText('Play error: ' + error)
                else:
                    self.sb.SetStatusText('Played ' + url)

                return

            # Else, set new directory and repopulate
            self.dir = ent.dir
            self.dirent.SetLabel(self.dir)

        self.populate()

    def delete(self, e):
        '''Delete an item'''
        self.setHost()
        index = self.list.GetFirstSelected()
        
        if index < 0:
            self.populate()
            return

        # Something was selected so delete it
        ent = Entries.alllist[index]

        # If this entry has a path then delete it
        if ent.path:

            # Put up a confirm prompt
            dlg = wx.MessageDialog(None,
            'Are you sure to delete\n%s:/%s?' % (self.host, ent.path),
            'Confirm Delete', wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION|
            wx.STAY_ON_TOP)

            if dlg.ShowModal() != wx.ID_YES:
                self.sb.SetStatusText('')
                dlg.Destroy()
                return

            dlg.Destroy()
            url = makeurl(self.host, ent.path)
            self.sb.SetStatusText('Deleting ' + url)

            error = delete(url)
            if error:
                self.sb.SetStatusText('Delete error: ' + error)
            else:
                self.populate()
                self.sb.SetStatusText('Deleted ' + url)
        else:
            self.sb.SetStatusText('Not allowed to delete directory')

    def rename(self, e):
        '''Rename an item'''
        self.setHost()
        index = self.list.GetFirstSelected()
        
        if index < 0:
            self.populate()
            return

        # Something was selected so rename it
        ent = Entries.alllist[index]

        # If this entry has a path then rename it
        if ent.path:

            oldname = basename(ent.path)

            # Put up a prompt
            dlg = wx.TextEntryDialog(None, 'Rename ' + oldname, 'Rename?')
            dlg.SetValue(oldname)

            if dlg.ShowModal() != wx.ID_OK:
                self.sb.SetStatusText('')
                dlg.Destroy()
                return

            newname = dlg.GetValue()
            dlg.Destroy()

            # Append file ext for user convenience
            if not newname.lower().endswith('.rec') and newname.find('.') < 0:
                newname += '.rec'

            if oldname == newname:
                self.sb.SetStatusText('No name change')
                return

            error = namecheck(oldname, newname)

            if not error:
                oldurl = makeurl(self.host, ent.path)
                self.sb.SetStatusText('Renaming ' + oldurl)
                error = rename(oldurl, newname)

            if error:
                self.sb.SetStatusText('Rename error: ' + error)
            else:
                self.populate()
                self.sb.SetStatusText('Renamed ' + newname)
        else:
            self.sb.SetStatusText('Not allowed to rename directory')

    def populate(self):
        '''Populate the file list data given host + dir'''
        self.Disable()
        self.setHost()
        self.setPlayer()
        url = makeurl(self.host, self.dir)
        self.sb.SetStatusText('Populating from ' + url)
        self.list.DeleteAllItems()

        # Fetch dir listing from ftp server
        dirlist, error = fetch(url)

        if error:
            self.sb.SetStatusText('Open error: ' + error)
        elif not dirlist:
            self.sb.SetStatusText('Can\'t open ' + url)
        else:

            # Build the list of returned entries
            Entries.build(self.host, self.dir, dirlist)

            # Insert in listctrl
            for x in Entries.alllist:

                # Add file or dir icon
                if x.path:
                    icon = self.file_norm
                elif x.up:
                    icon = self.dir_up
                else:
                    icon = self.dir_norm

                ind = self.list.InsertImageStringItem(sys.maxint, x.display,
                        icon)
                self.list.SetStringItem(ind, 1, x.datestr)
                self.list.SetStringItem(ind, 2, x.size)
                item = self.list.GetItem(ind)

                # Highlight any current recording in progress and
                # distinguish files by colour
                if x.size == 'RECORDING':
                    item.SetTextColour(wx.RED)
                elif x.path:
                    item.SetTextColour(wx.BLUE)

                self.list.SetItem(item)

            self.sb.SetStatusText('')

        self.parent.SetFocus()
        self.list.resizeLastColumn(40)
        self.Enable()

class MyFrame(wx.Frame):
    '''Main Wx window'''
    def __init__(self):
        '''Constructor'''
        wx.Frame.__init__(self, None, -1, NAME, size=(720, 720))

        # Add menubar and status bar
        self.createMenuBar()
        self.sb = self.CreateStatusBar()

        # Create main panel where the action happens
        self.panel = MyPanel(self)

    def createMenuBar(self):
        '''Set up menus in menubar'''
        menubar = wx.MenuBar()

        # Set up File menu
        file = wx.Menu()
        #file.AppendSeparator()
        file.Append(wx.ID_CLOSE, '&Close', 'Close the program')
        self.Bind(wx.EVT_MENU, self.closeDown, id=wx.ID_CLOSE)
        menubar.Append(file, '&File ')

        # Set up Help menu
        help = wx.Menu()
        #help.AppendSeparator()
        help.Append(wx.ID_ABOUT, '&About', 'Information about this program')
        self.Bind(wx.EVT_MENU, self.onAbout, id=wx.ID_ABOUT)
        menubar.Append(help, '&Help ')

        self.SetMenuBar(menubar)

    def closeDown(self, e):
        '''Called to exit this gui program'''
        self.Close()

    def onAbout(self, e):
        '''Generate an about box'''
        info = wx.AboutDialogInfo()
        info.SetName(NAME)
        info.SetDescription(DESCRIPTION)

        info.SetVersion(VERSION)
        info.SetCopyright(COPYRIGHT)
        info.SetLicence(LICENCE)
        info.AddDeveloper(AUTHOR)
        wx.AboutBox(info)

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        #frame.Center()
        frame.Show()
        return True

if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()
