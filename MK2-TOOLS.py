#!/usr/bin/env python
import time
import os
import sys
import pygame
from pygame.locals import *
import VMSYSTEM.libvmconf as libvmconf

#import VMSYSTEM.libbaltcalc as libbaltcalc
import VMSYSTEM.libvmui as vmui
#SBTCVM MK2 Graphical Tools launcher
#needeed by btclock
mixrate=int(libvmconf.getconf("audio", "mixrate"))


try:
	cmd=sys.argv[1]
except:
	cmd=None
if cmd=="-h" or cmd=="--help" or cmd=="help":
	print '''This is MK2-TOOLS.py, a command line tools launcher for SBTCVM Mark 2
commands:
MK2-RUN.py -h (--help) (help): this text
MK2-RUN.py -v (--version)    : version information.
MK2-RUN.py -a (--about)      : about MK2-RUN.py
MK2-RUN.py -l (--list)       : list all tools and their toolnames.
MK2-RUN.py [toolname]        : run tool
'''
elif cmd=="-v" or cmd=="--version":
	print "SBTCVM MK2-TOOLS tool launcher v2.0.3"
elif cmd=="-l" or cmd=="--list":
	print '''List of tools:
[Toolname]  |  [Tool description]
-----------------------------------------------
btclock     :  show a balanced ternary clock
pause       :  test VM pause menu
uicredits   :  scrolling credits window called by VM's file menu.
yndiag      :  test yndiag function
okdiag      :  test okdiag function
menu        :  test graphical menu function.
textinput   :  test text input function.
scrollbtn   :  test scroll buttons.

imgview [image] : fileview's image viewer
textview [file] : fileview's text viewer
codeview [file] : fileview's code viewer
namecrunch [string] : test namecrunch function
timecodetest : test ternary Timecode encode/decode'''

elif cmd=="-a" or cmd=="--about":
	print '''#SBTCVM Mark 2 tool launcher


v2.0.3

Copyright (c) 2016-2017 Thomas Leathers and Contributors

  SBTCVM Mark 2 tool launcher is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  SBTCVM Mark 2 tool launcher is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.
 
  You should have received a copy of the GNU General Public License
  along with SBTCVM Mark 2 tool launcher. If not, see <http://www.gnu.org/licenses/>
'''
elif cmd==None:
	print "tip: use MK2-TOOLS.py -h for help."
elif cmd=="namecrunch" or cmd=="timecodetest":
	if cmd=="namecrunch":
		import VMSYSTEM.libSBTCVM as libSBTCVM
		try:
			ncruncharg=sys.argv[2]
		except IndexError:
			ncruncharg="thisisatest"
		print ncruncharg
		print libSBTCVM.namecrunch(ncruncharg, "-tools-test.log")
	if cmd=="timecodetest":
		import VMSYSTEM.libSBTCVM as libSBTCVM
		for BI in [19.682, 10.000, 0]:
			print BI
			BG=libSBTCVM.timeencode(BI)
			print BG
			BQ=libSBTCVM.timedecode(BG)
			print BQ
elif cmd=="btclock" or cmd=="pause" or cmd=="scrollbtn" or cmd=="uicredits" or cmd=="imgview" or cmd=="textview" or cmd=="codeview" or cmd=="textinput" or cmd=="menu"  or cmd=="okdiag" or cmd=="yndiag":
	#print "SBTCVM Graphical Tools launcher starting..."
	pygame.display.init()
	pygame.font.init()
	
	if cmd=="uicredits":
		pygame.display.set_caption("SBTCVM Credits", "SBTCVM Credits")
	elif cmd=="imgview":
		pygame.display.set_caption("imgview", "imgview")
	elif cmd=="textview":
		pygame.display.set_caption("textview", "textview")
	elif cmd=="codeview":
		pygame.display.set_caption("codeview", "codeview")
	else:
		pygame.display.set_caption("SBTCVM Mark 2 | Tools", "SBTCVM Mark 2 | Tools")
	GLOBKIOSK=1
	if cmd=="imgview":
		windowicon=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX'), 'imgview64.png'))
		pygame.display.set_icon(windowicon)
	elif cmd=="textview":
		windowicon=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX'), 'textview64.png'))
		pygame.display.set_icon(windowicon)
	elif cmd=="codeview":
		windowicon=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX'), 'codeview64.png'))
		pygame.display.set_icon(windowicon)
	else:
		windowicon=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX'), 'icon64.png'))
		pygame.display.set_icon(windowicon)
	#screen fonts
	if cmd=="uicredits":
		screensurf=pygame.display.set_mode((600, 370))
	elif cmd=="imgview":
		screensurf=pygame.display.set_mode((800, 600), pygame.RESIZABLE)
	elif cmd=="textview" or cmd=="codeview":
		screensurf=pygame.display.set_mode((800, 600), pygame.RESIZABLE)
	else:
		screensurf=pygame.display.set_mode((800, 600))
	
	#init VMUI library.
	vmui.initui(screensurf, 1)
	
	#uicredits is the special creditsscroll wrapper mode used by launcher.py
	if cmd=="uicredits":
		vmui.toolsscreen(4)
		vmui.creditsscroll(topleft=1)
	if cmd=="textinput":
		vmui.toolsscreen(1)
		textinpout=vmui.textinput(4, 210)
		print "Input has returned:"
		print textinpout
	if cmd=="scrollbtn":
		vmui.toolsscreen(1)
		hscroll=vmui.makehscroll()
		screensurf.blit(hscroll[0], (20, 20))
		screensurf.blit(hscroll[1], (20, 60))
		vscroll=vmui.makevscroll()
		screensurf.blit(vscroll[0], (60, 20))
		screensurf.blit(vscroll[1], (60, 60))
		textinpout=vmui.textinput(4, 210)
		print "Input has returned:"
		print textinpout
	if cmd=="okdiag":
		vmui.toolsscreen(1)
		#note: to center dialog in a pygame window use half the window width as xpos,
		#and half the window height as ypos
		screenw=800
		screenh=600
		xpos=(screenw // 2)
		ypos=(screenh // 2)
		diagtext='''This is a test.
of vmui.okdiag()
a function to create OK dialogs.'''
		diagout=vmui.okdiag(diagtext, xpos, ypos)
		print "ok dialog has returned:"
		print diagout
		diagout=vmui.okdiag("test", xpos, ypos)
		print "ok dialog 2 has returned:"
		print diagout
	if cmd=="yndiag":
		vmui.toolsscreen(1)
		#note: to center dialog in a pygame window use half the window width as xpos,
		#and half the window height as ypos
		screenw=800
		screenh=600
		xpos=(screenw // 2)
		ypos=(screenh // 2)
		diagtext='''This is a test.
of vmui.yndiag()
a function to create Yes/No dialogs.'''
		diagout=vmui.yndiag(diagtext, xpos, ypos)
		print "yes/no dialog has returned:"
		print diagout
		diagout=vmui.yndiag("test", xpos, ypos)
		print "yes/no dialog 2 has returned:"
		print diagout
	if cmd=="menu":
		vmui.toolsscreen(1)
		mi1=vmui.menuitem("Testing", "ITEM1", icon=windowicon)
		mi2=vmui.menuitem("Testing2", "ITEM2")
		mi3=vmui.menuitem("Testing3 (this item is not clickable)", "ITEM3", noclick=1)
		mi0a=vmui.menuitem("This menu will ignore clicks outside menu. (reclick=2)", "ITEM4", noclick=1)
		mi0b=vmui.menuitem("This menu will just return None for clicks outside menu (reclick=0)", "ITEM4", noclick=1)
		menulist=[mi0a, mi1, mi2, mi3]
		menulist2=[mi0b, mi1, mi2, mi3]
		menuret=vmui.menuset(menulist, 4, 210, reclick=2)
		vmui.toolsscreen(1)
		print "menu has returned:"
		print menuret
		menuret2=vmui.menuset(menulist2, 20, 210, reclick=0)
		print "menu2 has returned:"
		print menuret2
	if cmd=="imgview":
		vmui.toolsscreen(1)
		try:
			vmui.imgview(sys.argv[2])
		except IndexError:
			print "MUST SPECIFY IMAGE FILENAME."
	if cmd=="textview":
		vmui.toolsscreen(1)
		try:
			vmui.textview(sys.argv[2])
		except IndexError:
			print "MUST SPECIFY TEXT FILENAME."
	if cmd=="codeview":
		vmui.toolsscreen(1)
		try:
			vmui.codeview(sys.argv[2])
		except IndexError:
			print "MUST SPECIFY TEXT FILENAME."
	if cmd=="btclock":
		pygame.mixer.init(frequency=mixrate , size=-16)
		import VMSYSTEM.libbttools as bttool
		vmui.toolsscreen(1)
		bttool.initui(screensurf, 1)
		bttool.BTCLOCKDATE()
	if cmd=="pause":
		pygame.mixer.init(frequency=mixrate , size=-16)
		print "launching SBTCVM VM pause menu."
		#pause menu needs readouts area to be drawn.
		vmui.toolsscreen(3)
		pmenret=vmui.pausemenu()
		if pmenret=="c":
			print "Pause menu reports a continue VM"
		else:
			print 'Pause menu reports a Stop VM / Exit to Main Menu'