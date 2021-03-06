#!/usr/bin/env python
import VMSYSTEM.libvmui as vmui
import VMSYSTEM.libvmconf as libvmconf
import VMSYSTEM.libthemeconf as libthemeconf
import VMSYSTEM.libbaltcalc as libbaltcalc
import VMSYSTEM.libfilevirtual as libfilevirtual
import pygame
import time
import copy
import sys
import os
import traceback
import subprocess
import xml.etree.ElementTree as ET

pygame.font.init()
simplefont = pygame.font.SysFont(None, 19)
monofont = pygame.font.SysFont("Mono", 16)
#monofont.set_bold(True)

titlebg=libthemeconf.titleactbg
titletext=libthemeconf.titleacttext
titleinactbg=libthemeconf.titleinactbg
titleinacttext=libthemeconf.titleinacttext
framebg=libthemeconf.hudbg
frametext=libthemeconf.hudtext
framebtn=libthemeconf.btnbg2
framebtntext=libthemeconf.btntext
framediv=libthemeconf.huddiv
shellbg=libthemeconf.consbg
shelltext=libthemeconf.constext
#frametext=libthemeconf.hudt


hudy=20
fpad=1
hudoffset=21
Plugpath="plugins"

constext=([""] * 100)
#consfull=[]
#print constext

def consolewrite(string):
	global constext
	#global consfull
	constext.pop(0)
	constext.append(string)
	#consfull.append(string)
	print ("Con: " + string)

#que method:
#que is a system of inter-application communication.
#que codes:
#(0, arguments) = generic data
#(1, arguments) = image data
#(2, arguments) = text
#(100, arguments) = shell query (used by Shell), any responses should be in a list, 1 string per line
#(101) = shell status check (used by Shell at regular interval, no arguments sent.), any responses should be in a list, 1 string per line
#(102) = shell ready (used by Shell during shell startup, no arguments sent.), any responses should be in a list, 1 string per line

#sig method:
#sig must be a list of arguments or be None
#list of sig return codes:
#(0, widinstance)=activate the pre-initalized wid widinstance
#(1, x)=close self. x=0: call self's close method. 1=don't call close method.
#None=do nothing
#
#
##special sigs:
#("TASKMAN", code, taskid)=used ONLY by taskman. (the host program keeps track of the taskid's authorized to use this)
#code=0 close taskid, code=1 bring taskid to top and reset its x & y values.

PLUGINDUMMY=pygame.image.load(os.path.join("VMSYSTEM", "GFX", "launch", 'dummy.png'))

pluglist=list()

class plugobj:
	def __init__(self, classref, execname, label, direc=None, icon=None, catid=None):
		self.classref=classref
		self.icnpath=icon
		self.execname=execname
		self.label=label
		self.direc=direc
		self.catid=catid
		if self.direc!=None:
			if self.icnpath!=None:
				self.icon=pygame.image.load(os.path.join(Plugpath, self.direc, self.icnpath))
			else:
				self.icon=PLUGINDUMMY
		else:
			self.icon=PLUGINDUMMY

#tool lookup function.
def widlookup(namestring):
	#if namestring=="TEST":
	#	return testwid
	#if namestring=="scribble": -moved to plugin
	#	return scribble
	#if namestring=="credits": -moved to plugin
	#	return qcred
	#if namestring=="taskman":
	#	return taskman
	if namestring=="LaunchConsole":
		return launchconsole
	if namestring=="fileman":
		return fileman
	if namestring=="shell":
		return shell

#standardized rect generation
def getframes(x, y, widsurf, resizebar=0):
	y -= hudoffset
	x -= 1
	widbox=widsurf.get_rect()
	widbox.x=x+fpad
	widbox.y=y+hudy+fpad
	if resizebar==1:
		framebox=pygame.Rect(x, y, (widbox.w + fpad + fpad), (widbox.h + fpad + hudy + fpad + 10))
	else:
		framebox=pygame.Rect(x, y, (widbox.w + fpad + fpad), (widbox.h + fpad + hudy + fpad))
	closebtnrect=pygame.Rect(x, y, hudy, hudy)
	return (widbox, framebox, closebtnrect)
	
#standardized frame drawing
def drawframe(framerect, closerect, widbox, widsurf, screensurf, title, wo):
	if wo==0:
		pygame.draw.rect(screensurf, titlebg, framerect, 0)
		pygame.draw.rect(screensurf, framediv, framerect, 1)
		pygame.draw.rect(screensurf, framebtn, closerect, 0)
		pygame.draw.line(screensurf, framebtntext, (closerect.x+4, closerect.y+4), (closerect.x+14, closerect.y+14), 3)
		pygame.draw.line(screensurf, framebtntext, (closerect.x+14, closerect.y+4), (closerect.x+4, closerect.y+14), 3)
		pygame.draw.rect(screensurf, framediv, closerect, 1)
		pygame.draw.line(screensurf, framediv, (framerect.x, framerect.y+hudy), ((framerect.x + framerect.w - 1), framerect.y+hudy))
		pygame.draw.line(screensurf, framediv, (framerect.x, framerect.y+hudy+widbox.h+1), ((framerect.x + framerect.w - 1), framerect.y+hudy+widbox.h+1))
		screensurf.blit(widsurf, widbox)
		labtx=simplefont.render(title, True, titletext, titlebg)
		screensurf.blit(labtx, ((framerect.x + 25), (framerect.y + 1)))
	else:
		pygame.draw.rect(screensurf, titleinactbg, framerect, 0)
		pygame.draw.rect(screensurf, framediv, framerect, 1)
		pygame.draw.rect(screensurf, framebtn, closerect, 0)
		pygame.draw.line(screensurf, framebtntext, (closerect.x+4, closerect.y+4), (closerect.x+14, closerect.y+14), 3)
		pygame.draw.line(screensurf, framebtntext, (closerect.x+14, closerect.y+4), (closerect.x+4, closerect.y+14), 3)
		pygame.draw.rect(screensurf, framediv, closerect, 1)
		pygame.draw.line(screensurf, framediv, (framerect.x, framerect.y+hudy), ((framerect.x + framerect.w - 1), framerect.y+hudy))
		pygame.draw.line(screensurf, framediv, (framerect.x, framerect.y+hudy+widbox.h+1), ((framerect.x + framerect.w - 1), framerect.y+hudy+widbox.h+1))

		screensurf.blit(widsurf, widbox)
		labtx=simplefont.render(title, True, titleinacttext, titleinactbg)
		screensurf.blit(labtx, ((framerect.x + 25), (framerect.y + 1)))
	
#Plugin Loader
for plugcodefile in os.listdir(Plugpath):
	if plugcodefile.lower().endswith(".sdap.py"):
		PLUGFILE=open(os.path.join(Plugpath, plugcodefile), 'r')
		try:
			PLUGEXEC=compile(PLUGFILE.read(), os.path.join(Plugpath, plugcodefile), 'exec')
			exec(PLUGEXEC)
			pluginst=plugobj(SDAPPLUGREF, SDAPNAME, SDAPLABEL, SDAPDIR, SDAPICON, SDAPCAT)
			pluglist.extend([pluginst])
			consolewrite("Load plugin: " + SDAPNAME + " (" + plugcodefile + ")")
		except SyntaxError as err:
			consolewrite("Plugin failure: SyntaxError on " + plugcodefile)
			print(traceback.format_exc())
			for errline in vmui.listline(str(err)):
				consolewrite(errline)
				


#pin typeids:
#0=text (single string) (can be multiple lines)
#1=image (pygame surface)
#pin object class used in pinboard system.
class pinobj:
	def __init__(self, name, pindata, typeid, thumb=None):
		self.name=name
		self.pindata=pindata
		self.typeid=typeid
		self.pinid=None
		self.thumb=thumb
	#helper functions for type 0 (return None on other typeids)
	def getstring(self):
		if self.typeid==0:
			return self.pindata
		else:
			return
	def getlist(self):
		if self.typeid==0:
			return vmui.listline(self.pindata)
		else:
			return
	#common functions. (should be usable with any data type.)
	#used to get a thumbnail for the pin object.
	def thumb(self):
		if self.thumb==None:
			if self.typeid==1:
				self.thumb=pygame.transform.scale(self.pindata, (80, 40))
			elif self.typeid==0:
				self.thumb=pygame.Surface((80, 40))
				self.thumb.fill(libthemeconf.textboxbg)
				self.strtx=(vmui.listline(self.pindata)[0])[0:30]
				self.rentx=simplefont.render(self.strtx, True, libthemeconf.textboxtext, libthemeconf.textboxbg)
				self.thumb.blit(self.rentx, (0, 0))
			else:
				self.thumb=pygame.Surface((80, 40))
				self.thumb.fill(libthemeconf.textboxbg)
				self.rentx=simplefont.render("Unknown data type!", True, libthemeconf.textboxtext, libthemeconf.textboxbg)
				self.thumb.blit(self.rentx, (0, 0))
		return self.thumb

pinobjlist0=list()
pinobjlist1=list()
curpin0=None
curpin1=None

pinidcnt=0
#note: this may return None in some cases!
#use this with correct typeid to get current pin of that type.
def getpin(typeid):
	if typeid==0:
		return curpin0
	elif typeid==1:
		return curpin1
	else:
		return None

def addpin(pin):
	global pinidcnt
	consolewrite("Pinboard: added pin: \"" + pin.name + "\"")
	pin.pinid=pinidcnt
	pinidcnt += 1
	if pin.typeid==0:
		pinobjlist0.extend([pin])
		curpin0=pin
	if pin.typeid==1:
		pinobjlist1.extend([pin])
		curpin1=pin
	return
	


#taskman is a special case. due to the nature of it.
class taskman:
	def __init__(self, screensurf, windoworder, xpos=0, ypos=0, argument=None):
		consolewrite("Taskman: running")
		#screensurf is the surface to blit the window to
		self.screensurf=screensurf
		#wo is a sorting variable used to sort the windows in a list
		self.wo=windoworder
		#title is the name of the window
		self.title="Taskman"
		#taskid is set automatically
		self.taskid=0
		self.argument=argument
		self.widx=300
		self.widy=500
		#x and y are required.
		self.x=xpos
		self.y=ypos
		self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
		self.widsurf.fill(framebg)
		
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		#these rects are needed
		#frame close button rect
		self.closerect=self.frametoup[2]
		#rect of window content
		self.widbox=self.frametoup[0]
		#frame rect
		self.framerect=self.frametoup[1]
		self.closetasktx=simplefont.render("Close Task", True, framebg, frametext)
		self.bringtoptx=simplefont.render("Bring to top", True, framebg, frametext)
		self.seltask=None
		self.sigret=None
		
		self.fullupt=1
	def render(self):
		self.texty=20
		self.textx=0
		self.taskdict=dict()
		self.widsurf.fill(framebg)
		#copy and sort raw tasklist given to taskman by host program
		self.argumentcopy=list(self.argument)
		self.argumentcopy.sort(key=lambda x: x.taskid, reverse=False)
		#tasklist parser
		for self.task in self.argumentcopy:
			if self.seltask==self.task.taskid:
				self.labtx=simplefont.render(("Order: " + str(self.task.wo) + " | taskid: " + str(self.task.taskid) + " | Name: " + self.task.title), True, framebg, frametext)
			else:
				self.labtx=simplefont.render(("Order: " + str(self.task.wo) + " | taskid: " + str(self.task.taskid) + " | Name: " + self.task.title), True, frametext, framebg)
			self.clickbx=self.widsurf.blit(self.labtx, (self.textx, self.texty))
			self.clickbx.x += self.x
			self.clickbx.y += self.y
			self.taskdict[self.task.taskid]=self.clickbx
			self.texty += 18
		drawframe(self.framerect, self.closerect, self.widbox, self.widsurf, self.screensurf, self.title, self.wo)
		#task commands
		self.clx=self.screensurf.blit(self.closetasktx, (self.x, self.y))
		self.topx=self.screensurf.blit(self.bringtoptx, (self.x+5+self.closetasktx.get_width(), self.y))
		if self.fullupt==1:
			self.fullupt=0
			return
		else:
			return [pygame.Rect(self.x, self.y, self.widx, self.texty + 18)]
	def movet(self, xoff, yoff):
		self.x -= xoff
		self.y -= yoff
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		self.closerect=self.frametoup[2]
		self.widbox=self.frametoup[0]
		self.framerect=self.frametoup[1]
	def resizet(self, xoff, yoff):
		#manipulate your window surface x and y sizes like so: if want only x or only y, manipulate only that.
		self.widx -= xoff
		self.widy -= yoff
		#check the size to ensure it isn't too small (or invalid)
		if self.widx<300:
			self.widx=300
		if self.widy<200:
			self.widy=200
		
		#redefine your widsurf, and refresh rects, also do any needed sdap-specific operations.
		self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
		#TO SHOW THE RESIZEBAR AT THE BOTTOM OF WINDOW YOU MUST SPECIFY resizebar=1 !!!
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		self.closerect=self.frametoup[2]
		self.widbox=self.frametoup[0]
		self.framerect=self.frametoup[1]
	def click(self, event):
		if self.seltask not in self.taskdict:
			self.seltask=None
		#task commands logic
		if self.seltask!=None:
			if self.clx.collidepoint(event.pos)==1:
				self.sigret=("TASKMAN", 0, self.seltask)
			elif self.topx.collidepoint(event.pos)==1:
				self.sigret=("TASKMAN", 1, self.seltask)
			else:
				self.sigret=None
		else:
			self.sigret=None
		#task selector
		for self.taskc in self.taskdict:
			if self.taskdict[self.taskc].collidepoint(event.pos)==1:
				self.seltask=self.taskc
				#print self.seltask
				return
	def clickup(self, event):
		return
	def keydown(self, event):
		return
	def keyup(self, event):
		return
	def close(self):
		return
	def hostquit(self):
		return
	def sig(self):
		return self.sigret
	def que(self, signal):
		return





class catsel:
	def __init__(self, screensurf, windoworder, xpos=0, ypos=0, argument=None):
		#screensurf is the surface to blit the window to
		self.screensurf=screensurf
		#wo is a sorting variable used to sort the windows in a list
		self.wo=windoworder
		#title is the name of the window
		self.argument=argument
		self.title=self.argument[0]
		self.tilelist=self.argument[1]
		#taskid is set automatically
		self.taskid=0
		
		self.widx=500
		self.widy=300
		#x and y are required.
		self.x=xpos
		self.y=ypos
		self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
		self.widsurf.fill(framebg)
		
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		#these rects are needed
		#frame close button rect
		self.closerect=self.frametoup[2]
		#rect of window content
		self.widbox=self.frametoup[0]
		#frame rect
		self.framerect=self.frametoup[1]
		self.closetasktx=simplefont.render("Close Task", True, framebg, frametext)
		self.bringtoptx=simplefont.render("Bring to top", True, framebg, frametext)
		self.seltask=None
		self.sigret=None
		self.tileoff=0
		self.fullupt=1
		#first render flag
		self.firstrender=1
		self.tilejumpx=100
		self.tilejumpy=95
		self.vscrollbtns=vmui.makevscroll()
		#first render size check hight value
		self.tileyprev=0
		#vertical autosize limit
		self.autovertlimit = (5 + (self.tilejumpy * 4))
		#print self.autovertlimit
	def render(self):
		if self.fullupt==1:
			self.fullupt=0
			self.widsurf.fill(framebg)
			self.tilex=5
			self.tiley=5+self.tileoff
			self.tileyscrollcheck=self.tiley
			self.tilerects=dict()
			self.tilecnt=0
			self.tilerollover=1
			self.firstrow=1
			#tile render
			for self.tile in self.tilelist:
				self.tile.render(self.tilex, self.tiley, surf=self.widsurf)
				self.tilerects[self.tilecnt]=self.tile.tilebox
				#self.tile.tilebox.x += self.x
				#self.tile.tilebox.y += self.y
				self.tilecnt += 1
				if self.tilex+self.tilejumpx+90<self.widx:
					#rollover check
					if self.tilerollover==1:
						self.tilerollover=0
						self.tileyprev += self.tilejumpy
						self.tileyscrollcheck=self.tiley + self.tilejumpy - 5
					self.tilex += self.tilejumpx
				else:
					self.firstrow=0
					self.tilex=5
					self.tiley += self.tilejumpy
					self.tilerollover=1
			if self.tileoff<0:
				self.widsurf.blit(self.vscrollbtns[0], (self.widx-40, 0))
			if (self.tileyscrollcheck) >= self.widy:
				self.widsurf.blit(self.vscrollbtns[1], (self.widx-40, self.widy-20))
			#first render check
			if self.firstrender==1:
				self.firstrender=0
				self.widy=(self.tileyprev + 5)
				if self.widy>self.autovertlimit:
					self.widy=self.autovertlimit
				if self.firstrow==1:
					self.widx=self.tilex
				self.resizet(0, 0)
				self.render()
			else:
				drawframe(self.framerect, self.closerect, self.widbox, self.widsurf, self.screensurf, self.title, self.wo)
				return [self.framerect]
		else:
			drawframe(self.framerect, self.closerect, self.widbox, self.widsurf, self.screensurf, self.title, self.wo)
			return []
	def movet(self, xoff, yoff):
		
		self.x -= xoff
		self.y -= yoff
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		self.closerect=self.frametoup[2]
		self.widbox=self.frametoup[0]
		self.framerect=self.frametoup[1]
	def resizet(self, xoff, yoff):
		self.fullupt=1
		#manipulate your window surface x and y sizes like so: if want only x or only y, manipulate only that.
		self.widx -= xoff
		self.widy -= yoff
		#check the size to ensure it isn't too small (or invalid)
		if self.widx<200:
			self.widx=200
		if self.widy<100:
			self.widy=100
		self.tileoff=0
		#redefine your widsurf, and refresh rects, also do any needed sdap-specific operations.
		self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
		#TO SHOW THE RESIZEBAR AT THE BOTTOM OF WINDOW YOU MUST SPECIFY resizebar=1 !!!
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		self.closerect=self.frametoup[2]
		self.widbox=self.frametoup[0]
		self.framerect=self.frametoup[1]
	def click(self, event):
		self.localpos=((event.pos[0] - self.x), (event.pos[1] - self.y))
		
		if event.button==4:
			if self.tileoff<0:
				self.tileoff += self.tilejumpy
				self.fullupt=1
				return
		if event.button==5:
			if (self.tileyscrollcheck) >= self.widy:
				self.tileoff -= self.tilejumpy
				self.fullupt=1
				return
		self.tilecnt=0
		for self.tile in self.tilelist:
			if self.tilerects[self.tilecnt].collidepoint(self.localpos)==1 and event.button==1:
				self.sigret=["CATSEL", self.tile.act(), self.tile.ltype]
			self.tilecnt += 1
	def clickup(self, event):
		return
	def keydown(self, event):
		return
	def keyup(self, event):
		return
	def close(self):
		return
	def hostquit(self):
		return
	def sig(self):
		return self.sigret
	def que(self, signal):
		return



#hudswitch
class hudswitch:
	def __init__(self, screensurf, windoworder, xpos=0, ypos=0, argument=None):
		consolewrite("hudswitcher: running.")
		#screensurf is the surface to blit the window to
		self.screensurf=screensurf
		#wo is a sorting variable used to sort the windows in a list
		self.wo=windoworder
		#title is the name of the window
		self.title="SYS_HUDSWITCHER"
		#taskid is set automatically
		self.taskid=0
		self.argument=argument
		self.syswids=self.argument[1]
		self.widx=(self.screensurf.get_width() - xpos)
		self.widy=44
		#x and y are required.
		self.x=xpos
		self.y=ypos
		self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
		self.widsurf.fill(framebg)
		
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		#these rects are needed
		#frame close button rect
		self.closerect=pygame.Rect(0, 0, 0, 0)
		#rect of window content
		self.widbox=self.frametoup[0]
		#frame rect
		self.framerect=self.frametoup[0]
		self.closetasktx=simplefont.render("Close Task", True, framebg, frametext)
		self.bringtoptx=simplefont.render("Bring to top", True, framebg, frametext)
		self.seltask=None
		self.sigret=None
		self.btnw=100
		self.acttask=None
		self.btn=pygame.Surface((100, 20)).convert(self.screensurf)
	def render(self):
		self.texty=2
		self.textx=self.x
		self.taskdict=dict()
		self.rectlist=list()
		self.switchlist=list()
		#copy and sort raw tasklist given to taskman by host program
		self.argumentcopy=list(self.argument[0])
		self.argumentcopy.sort(key=lambda x: x.taskid, reverse=False)
		#tasklist parser
		for self.task in self.argumentcopy:
			if self.task.taskid not in self.syswids:
				if self.textx+self.btnw<(self.screensurf.get_width() - 120):
					if self.task.wo!=0:
						self.btn.fill(titleinactbg)
						self.labtx=simplefont.render(self.task.title, True, titleinacttext, titleinactbg)
						self.btn.blit(self.labtx, (2, 2))
						
					else:
						self.btn.fill(titlebg)
						self.labtx=simplefont.render(self.task.title, True, titletext, titlebg)
						self.btn.blit(self.labtx, (2, 2))
					self.clickbx=self.screensurf.blit(self.btn, (self.textx, self.texty))
					pygame.draw.rect(self.screensurf, framediv, self.clickbx, 1)
					self.textx += (self.btnw + 2)
					self.taskdict[self.task.taskid]=self.clickbx
					self.rectlist.extend([self.clickbx])
				if self.texty==2 and self.textx+self.btnw>=(self.screensurf.get_width() - 120):
					self.textx=self.x
					self.texty += 21
		return self.rectlist
		#drawframe(self.framerect, self.closerect, self.widbox, self.widsurf, self.screensurf, self.title, self.wo)
		#task commands
		#self.clx=self.screensurf.blit(self.closetasktx, (self.x, self.y))
		#self.topx=self.screensurf.blit(self.bringtoptx, (self.x+5+self.closetasktx.get_width(), self.y))
	def movet(self, xoff, yoff):
		#self.x -= xoff
		#self.y -= yoff
		#self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		#self.closerect=self.frametoup[2]
		#self.widbox=self.frametoup[0]
		#self.framerect=self.frametoup[1]
		return
	def resizet(self, xoff, yoff):
		#manipulate your window surface x and y sizes like so: if want only x or only y, manipulate only that.
		#self.widy -= yoff
		self.widx=(self.screensurf.get_width() - self.x)
		#check the size to ensure it isn't too small (or invalid)
		
		#redefine your widsurf, and refresh rects, also do any needed sdap-specific operations.
		self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
		#TO SHOW THE RESIZEBAR AT THE BOTTOM OF WINDOW YOU MUST SPECIFY resizebar=1 !!!
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		#self.closerect=self.frametoup[0]
		self.widbox=self.frametoup[0]
		self.framerect=self.frametoup[0]
	def click(self, event):
		if self.seltask not in self.taskdict:
			self.seltask=None
		#task selector
		if event.button==4 or event.button==5:
			self.updatetasksel()
		if event.button==4 and self.acttask!=None:
			self.taskc=self.acttask-1
			if self.taskc<0:
				self.taskc=len(self.switchlist)-1
			self.rettaskid=self.switchlist[self.taskc]
			self.sigret=("TASKSWITCH", 0, self.rettaskid)
			return
		if event.button==5 and self.acttask!=None:
			self.taskc=self.acttask+1
			if self.taskc>len(self.switchlist)-1:
				self.taskc=0
			self.rettaskid=self.switchlist[self.taskc]
			self.sigret=("TASKSWITCH", 0, self.rettaskid)
			return
		for self.taskc in self.taskdict:
			if self.taskdict[self.taskc].collidepoint(event.pos)==1:
				#self.seltask=self.taskc
				self.sigret=("TASKSWITCH", 0, self.taskc)
				return
		#change to highest wo task (other than self) if none of the buttons were clicked.
		self.argumentcopy2=list(self.argument[0])
		self.argumentcopy2.sort(key=lambda x: x.wo, reverse=False)
		for self.taskc in self.argumentcopy2:
			if self.taskc.wo>=0 and self.taskc.taskid not in self.syswids:
				self.sigret=("TASKSWITCH", 0, self.taskc.taskid)
				#print "BEEP"
				return
	def clickup(self, event):
		return
	def keydown(self, event):
		return
	def keyup(self, event):
		return
	def close(self):
		return
	def hostquit(self):
		return
	def sig(self):
		return self.sigret
	def que(self, signal):
		return
	def updatetasksel(self):
		self.switchlist=list()
		self.argumentcopy3=list(self.argument[0])
		self.argumentcopy3.sort(key=lambda x: x.taskid, reverse=False)
		self.taskactcnt=-1
		self.acttask=None
		self.actnumer=None
		for self.task in self.argumentcopy3:
			
			if self.task.taskid not in self.syswids:
				self.taskactcnt += 1
				self.switchlist.extend([self.task.taskid])
				if self.actnumer==None:
					self.acttask=self.taskactcnt
					self.actnumer=self.task.wo
				if self.task.wo<self.actnumer:
					self.actnumer=self.task.wo
					self.acttask=self.taskactcnt

class launchconsole:
	def __init__(self, screensurf, windoworder, xpos=0, ypos=0, argument=None):
		#screensurf is the surface to blit the window to
		self.screensurf=screensurf
		#wo is a sorting variable used to sort the windows in a list
		self.wo=windoworder
		#title is the name of the window
		self.title="Console"
		#taskid is set automatically
		self.taskid=0
		self.yjump=16
		self.widx=500
		self.conscope=20
		self.conoffset=0
		self.widy=(self.conscope * self.yjump)
		self.consbak=list()
		#x and y are required.
		self.x=xpos
		self.y=ypos
		self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
		self.widsurf.fill(framebg)
		
		self.frametoup=getframes(self.x, self.y, self.widsurf)
		#these rects are needed
		#frame close button rect
		self.closerect=self.frametoup[2]
		#rect of window content
		self.widbox=self.frametoup[0]
		#frame rect
		self.framerect=self.frametoup[1]
		self.redraw=0
		self.scrdrg=0
		#print constext[(len(constext)-self.conscope+self.conoffset):(len(constext)-self.conoffset)]
		#print -self.conscope+self.conoffset
		#print -self.conoffset
		consolewrite("Console: Use mouse wheel or UP/DOWN to scroll")
	def render(self):
		#scrollbar arithetic
		if self.scrdrg==1:
			self.redraw=1
			self.scrlb=(100 * float(self.conscope)/float(len(constext)))
			self.scrloff=(100 * float(self.conoffset-len(constext))/float(len(constext)))
			self.scrlfull=300
			self.dy=self.sy
			self.mpos=pygame.mouse.get_pos()
			self.sy=(self.mpos[1])
			self.qy=self.dy-self.sy
			if self.qy<0:
				if not self.conscope+self.conoffset>=len(constext):
					self.conoffset+=abs(self.qy//3)
					#self.conoffset+1
			if self.qy>0:
				if self.conoffset!=0:
					self.conoffset-=abs(self.qy//3)
			if self.conscope+self.conoffset>len(constext):
				self.conoffset=(len(constext)-self.conscope)
			if self.conoffset<0:
				self.conoffset=0
			
		self.scrlb=(100 * float(self.conscope)/float(len(constext)))
		self.scrloff=(100 * float(self.conoffset)/float(len(constext)))
		self.scrlfull=300
		self.fullrect=pygame.Rect((self.widx-20), 0, 20, (self.scrlfull + 1))
		self.partrect=pygame.Rect((self.widx-19), (0 + (3 * self.scrloff)), 18, (3 * self.scrlb))
		#rendering
		if self.consbak!=constext:
			self.consbak=list(constext)
			self.texty=0
			self.widsurf.fill(framebg)
			for self.conline in constext[(len(constext)-(self.conscope+self.conoffset)):(len(constext)-self.conoffset)]:
				self.labtx=simplefont.render(self.conline, True, frametext, framebg)
				self.widsurf.blit(self.labtx, (0, self.texty))
				self.texty += self.yjump
			self.redraw=2
		elif self.redraw==1:
			self.redraw=2
			self.texty=0
			self.widsurf.fill(framebg)
			for self.conline in constext[(len(constext)-(self.conscope+self.conoffset)):(len(constext)-self.conoffset)]:
				self.labtx=simplefont.render(self.conline, True, frametext, framebg)
				self.widsurf.blit(self.labtx, (0, self.texty))
				self.texty += self.yjump
		if self.redraw==2:
			self.redraw=0
			pygame.draw.rect(self.widsurf, frametext, self.fullrect, 0)
			pygame.draw.rect(self.widsurf, framebg, self.partrect, 0)
		drawframe(self.framerect, self.closerect, self.widbox, self.widsurf, self.screensurf, self.title, self.wo)
		
	def movet(self, xoff, yoff):
		self.x -= xoff
		self.y -= yoff
		self.frametoup=getframes(self.x, self.y, self.widsurf)
		self.closerect=self.frametoup[2]
		self.widbox=self.frametoup[0]
		self.framerect=self.frametoup[1]
	#click is given pygame MOUSEBUTTONDOWN events that fall within widbox
	def click(self, event):
		if self.partrect.collidepoint(((event.pos[0]-self.x), (event.pos[1]-self.y))) and event.button==1:
			self.scrdrg=1
			self.sy=(event.pos[1])
			self.redraw=1
		if event.button==4:
			if not self.conscope+self.conoffset>=len(constext):
				self.conoffset+=1
				self.redraw=1
		if event.button==5:
			if self.conoffset!=0:
				self.conoffset-=1
				self.redraw=1
	#similar to click, except it receves MOUSEBUTTONUP events that fall within widbox.
	def clickup(self, event):
		if self.scrdrg==1:
			self.scrdrg=0
		return
	#keydown and keyup are given pygame KEYDOWN and KEYUP events.
	def keydown(self, event):
		if event.key==pygame.K_UP:
			if not self.conscope+self.conoffset>=len(constext):
				self.conoffset+=1
				self.redraw=1
		elif event.key==pygame.K_DOWN:
			if self.conoffset!=0:
				self.conoffset-=1
				self.redraw=1
		return
	def keyup(self, event):
		return
	#close is called when the window is to be closed.
	def close(self):
		return
	#hostquit is called when the host program is going to quit.
	def hostquit(self):
		return 
	def sig(self):
		return
	def que(self, signal):
		return

class shell:
	def __init__(self, screensurf, windoworder, xpos=0, ypos=0, argument=None):
		#screensurf is the surface to blit the window to
		self.screensurf=screensurf
		#wo is a sorting variable used to sort the windows in a list
		self.wo=windoworder
		#title is the name of the window
		self.title="Shell - test mode"
		#taskid is set automatically
		self.taskid=0
		self.yjump=16
		self.argument=argument
		if self.argument!=None:
			self.title="Shell - " + self.argument.title
		self.widx=((monofont.size("_")[0])*60)+20
		self.conscope=20
		self.conoffset=0
		self.curoffset=0
		self.widy=(self.conscope * self.yjump) + self.yjump + 6
		self.textin=""
		self.consbak=list()
		#x and y are required.
		self.x=xpos
		self.y=ypos
		self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
		self.widsurf.fill(shellbg)
		self.shtext=([""] * 100)
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		#these rects are needed
		#frame close button rect
		self.closerect=self.frametoup[2]
		#rect of window content
		self.widbox=self.frametoup[0]
		#frame rect
		self.framerect=self.frametoup[1]
		self.redraw=0
		self.scrdrg=0
		self.curstatus=1
		self.curcnt=0
		self.curpoint=40
		self.shellstart=1
		self.vscaletmp=0
		self.inputrect=pygame.Rect(0, (self.widy-self.yjump-4), self.widx, (self.yjump+4))
		#print self.shtext[(len(self.shtext)-self.conscope+self.conoffset):(len(self.shtext)-self.conoffset)]
		#print -self.conscope+self.conoffset
		#print -self.conoffset
	def render(self):
		
		if self.shellstart==1:
			self.shellstart=0
			if self.argument!=None:
				self.retlist=self.argument.que([102])
				if self.retlist!=None and self.retlist!=list():
					for self.line in self.retlist:
						self.shellwrite(self.line)
		if self.argument!=None:
			self.title="Shell - " + self.argument.title
			self.retlist=self.argument.que([101])
			if self.retlist!=None and self.retlist!=list():
				for self.line in self.retlist:
					self.shellwrite(self.line)
		#scrollbar arithetic
		if self.curcnt<self.curpoint:
			self.curcnt += 1
		else:
			self.curcnt=0
			if self.curstatus==1:
				self.curstatus=0
				self.redraw=2
			else:
				self.curstatus=1
				self.redraw=2
		if self.curstatus==1:
			self.textinD=vmui.charinsert(self.textin, "|", (self.curoffset + 1))
		else:
			self.textinD=vmui.charinsert(self.textin, " ", (self.curoffset + 1))
		self.textinD=(">" + self.textinD)
		if self.scrdrg==1:
			self.redraw=1
			self.scrlb=(100 * float(self.conscope)/float(len(self.shtext)))
			self.scrloff=(100 * float(self.conoffset-len(self.shtext))/float(len(self.shtext)))
			self.scrlfull=300
			self.dy=self.sy
			self.mpos=pygame.mouse.get_pos()
			self.sy=(self.mpos[1])
			self.qy=self.dy-self.sy
			if self.qy<0:
				if not self.conscope+self.conoffset>=len(self.shtext):
					self.conoffset+=abs(self.qy//3)
					#self.conoffset+1
			if self.qy>0:
				if self.conoffset!=0:
					self.conoffset-=abs(self.qy//3)
			if self.conscope+self.conoffset>len(self.shtext):
				self.conoffset=(len(self.shtext)-self.conscope)
			if self.conoffset<0:
				self.conoffset=0
			
		self.scrlb=(100 * float(self.conscope)/float(len(self.shtext)))
		self.scrloff=(100 * float(self.conoffset)/float(len(self.shtext)))
		self.scrlfull=300
		self.fullrect=pygame.Rect((self.widx-20), 0, 20, (self.scrlfull + 1))
		self.partrect=pygame.Rect((self.widx-19), (0 + (3 * self.scrloff)), 18, (3 * self.scrlb))
		#rendering
		#print self.redraw
		if self.consbak!=self.shtext:
			#print "ARG"
			self.consbak=list(self.shtext)
			self.texty=0
			self.redraw=3
			self.widsurf.fill(shellbg)
			for self.conline in self.shtext[(len(self.shtext)-(self.conscope+self.conoffset)):(len(self.shtext)-self.conoffset)]:
				self.labtx=monofont.render(self.conline, True, shelltext, shellbg)
				self.widsurf.blit(self.labtx, (0, self.texty))
				self.texty += self.yjump
			self.labtx=monofont.render(self.textinD, True, shelltext, shellbg)
			pygame.draw.rect(self.widsurf, shellbg, self.inputrect, 0)
			pygame.draw.rect(self.widsurf, shelltext, self.inputrect, 1)
			self.widsurf.blit(self.labtx, ((self.inputrect.x + 2), (self.inputrect.y + 2)))
		elif self.redraw==1:
			self.redraw=2
			self.texty=0
			self.widsurf.fill(shellbg)
			for self.conline in self.shtext[(len(self.shtext)-(self.conscope+self.conoffset)):(len(self.shtext)-self.conoffset)]:
				self.labtx=monofont.render(self.conline, True, shelltext, shellbg)
				self.widsurf.blit(self.labtx, (0, self.texty))
				self.texty += self.yjump
		if self.redraw==2:
			self.redraw=3
			self.labtx=monofont.render(self.textinD, True, shelltext, shellbg)
			pygame.draw.rect(self.widsurf, shellbg, self.inputrect, 0)
			pygame.draw.rect(self.widsurf, shelltext, self.inputrect, 1)
			self.widsurf.blit(self.labtx, ((self.inputrect.x + 2), (self.inputrect.y + 2)))
			
		if self.redraw==3:
			self.redraw=-1
			pygame.draw.rect(self.widsurf, frametext, self.fullrect, 0)
			pygame.draw.rect(self.widsurf, framediv, self.fullrect, 1)
			pygame.draw.rect(self.widsurf, framebg, self.partrect, 0)
		drawframe(self.framerect, self.closerect, self.widbox, self.widsurf, self.screensurf, self.title, self.wo)
		#print self.redraw
		if self.redraw==0:
			#print "u"
			#return empty list on no updates.
			return list()
		if self.redraw<0:
			self.redraw=0
		
	def movet(self, xoff, yoff):
		self.x -= xoff
		self.y -= yoff
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		self.closerect=self.frametoup[2]
		self.widbox=self.frametoup[0]
		self.framerect=self.frametoup[1]
	def resizet(self, xoff, yoff):
		self.vscaletmp -= yoff
		
		if self.vscaletmp<=-self.yjump:
			self.conscope -= 1
			if self.conscope<20:
				self.conscope=20
			self.vscaletmp += self.yjump
			self.widy=(self.conscope * self.yjump) + self.yjump + 6
			self.inputrect=pygame.Rect(0, (self.widy-self.yjump-4), self.widx, (self.yjump+4))
			#redefine your widsurf, and refresh rects, also do any needed sdap-specific operations.
			self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
			self.redraw=1
			#TO SHOW THE RESIZEBAR AT THE BOTTOM OF WINDOW YOU MUST SPECIFY resizebar=1 !!!
			self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
			self.closerect=self.frametoup[2]
			self.widbox=self.frametoup[0]
			self.framerect=self.frametoup[1]
		elif self.vscaletmp>=self.yjump:
			self.conscope += 1
			self.vscaletmp -= self.yjump
			self.widy=(self.conscope * self.yjump) + self.yjump + 6
			self.inputrect=pygame.Rect(0, (self.widy-self.yjump-4), self.widx, (self.yjump+4))
			#redefine your widsurf, and refresh rects, also do any needed sdap-specific operations.
			self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
			self.redraw=1
			#TO SHOW THE RESIZEBAR AT THE BOTTOM OF WINDOW YOU MUST SPECIFY resizebar=1 !!!
			self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
			self.closerect=self.frametoup[2]
			self.widbox=self.frametoup[0]
			self.framerect=self.frametoup[1]
	#click is given pygame MOUSEBUTTONDOWN events that fall within widbox
	def click(self, event):
		if self.partrect.collidepoint(((event.pos[0]-self.x), (event.pos[1]-self.y))) and event.button==1:
			self.scrdrg=1
			self.sy=(event.pos[1])
			self.redraw=1
		if event.button==4:
			if not self.conscope+self.conoffset>=len(self.shtext):
				self.conoffset+=1
				self.redraw=1
		if event.button==5:
			if self.conoffset!=0:
				self.conoffset-=1
				self.redraw=1
	#similar to click, except it receves MOUSEBUTTONUP events that fall within widbox.
	def clickup(self, event):
		if self.scrdrg==1:
			self.scrdrg=0
		return
	#keydown and keyup are given pygame KEYDOWN and KEYUP events.
	def keydown(self, event):
		if event.key==pygame.K_UP:
			if not self.conscope+self.conoffset>=len(self.shtext):
				self.conoffset+=1
				self.redraw=1
		elif event.key==pygame.K_DOWN:
			if self.conoffset!=0:
				self.conoffset-=1
				self.redraw=1
		#elif event.key==pygame.BACKSPACE:
		#home/end support.
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_HOME:
			if self.curoffset!=0:
				self.curoffset=0
				self.redraw=2
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_END:
			if self.curoffset!=len(self.textin):
				self.curoffset=len(self.textin)
				self.redraw=2
		#cursor movement
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
			if self.curoffset!=0:
				self.curoffset -= 1
				self.redraw=2
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
			if self.curoffset!=len(self.textin):
				self.curoffset += 1
				self.redraw=2
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
			self.shellwrite(">" + self.textin)
			if self.argument!=None:
				self.retlist=self.argument.que([100, self.textin])
				if self.retlist!=None:
					for self.line in self.retlist:
						self.shellwrite(self.line)
			self.curoffset=0
			self.textin=""
			self.conoffset=0
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
			if len(self.textin)!=0 and self.curoffset!=0:
				self.textin=vmui.charremove(self.textin, self.curoffset)
				self.curoffset -= 1
				self.redraw=2
		elif event.type == pygame.KEYDOWN and event.key != pygame.K_TAB:
			self.curoffset += 1
			self.textin=vmui.charinsert(self.textin, str(event.unicode), self.curoffset)
			self.redraw=2
		return
	def keyup(self, event):
		return
	#close is called when the window is to be closed.
	def close(self):
		return
	#hostquit is called when the host program is going to quit.
	def hostquit(self):
		return 
	def sig(self):
		return
	def que(self, signal):
		return
	def shellwrite(self, string):
		self.shtext.pop(0)
		self.shtext.append(string[0:60])
		if len(string)>60:
			consolewrite("Shell: Warning: line of text too long... clipping...")

#file browser code below:

fvstreg=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX', "fv"), 'fvstreg.png'))
fvtrom=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX', "fv"), 'fvtrom.png'))
fvdir=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX', "fv"), 'fvdir.png'))
fvup=pygame.transform.scale(pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX', "fv"), 'fvup.png')), (20, 20))
fvimg=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX', "fv"), 'fvimg.png'))
fvtext=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX', "fv"), 'fvtext.png'))
fvtasm=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX', "fv"), 'fvtasm.png'))
fvall=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX', "fv"), 'fvall.png'))
fvlog=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX', "fv"), 'fvlog.png'))
fvdmp=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX', "fv"), 'fvdmp.png'))
fvdummy=pygame.image.load(os.path.join(os.path.join('VMSYSTEM', 'GFX', "fv"), 'fvdummy.png'))

fvrunview=vmui.makeswitchbtn("RUN", "VIEW")
fvrunsw=fvrunview[0]
fvviewsw=fvrunview[1]
typefilter1=vmui.makerotbtn("Type", "Filter")

class filetyp:
	def __init__(self, ext, typeicon, qxtype, filterflg):
		self.ext=ext
		#self.typeicon=pygame.transform.scale(typeicon, (20, 20))
		self.typeicon=pygame.Surface((40, 25))
		self.typeicon.fill((255, 255, 255))
		self.typeiconfull=typeicon
		self.typeicon.blit(self.typeiconfull, (0, 0))
		self.qxtype=qxtype
		self.filterflg=filterflg
typ_png=filetyp("png", fvimg, "img", 2)
typ_jpg=filetyp("jpg", fvimg, "img", 2)
typ_jpeg=filetyp("jpeg", fvimg, "img", 2)
typ_gif=filetyp("gif", fvimg, "img", 2)
typ_streg=filetyp("streg", fvstreg, "streg", 3)
typ_trom=filetyp("trom", fvtrom, "trom", 1)
typ_tasm=filetyp("tasm", fvtasm, "tasm", 4)
typ_txt=filetyp("txt", fvtext, "text", 5)
typ_md=filetyp("md", fvtext, "text", 5)
typ_log=filetyp("log", fvlog, "log", 6)
typ_dmp=filetyp("dmp", fvdmp, "dmp", 7)
#also needed by system shell!
typelist=[typ_png, typ_jpg, typ_jpeg, typ_gif, typ_streg, typ_trom, typ_tasm, typ_txt, typ_md, typ_log, typ_dmp]
iconlist=[fvall, fvtrom, fvimg, fvstreg, fvtasm, fvtext, fvlog, fvdmp]

fil0=vmui.menuitem("All", 0)
fil1=vmui.menuitem("Trom", 1)
fil2=vmui.menuitem("Image", 2)
fil3=vmui.menuitem("Streg", 3)
fil4=vmui.menuitem("Tasm", 4)
fil5=vmui.menuitem("Text", 5)
fil6=vmui.menuitem("Log", 6)
fil7=vmui.menuitem("Dmp", 7)

filtermenu=[fil0, fil1, fil2, fil3, fil4, fil5, fil6, fil7]
typ_up=filetyp(None, fvup, "dir", None)
typ_dir=filetyp(None, fvdir, "dir", None)

class fileclick:
	def __init__(self, box, filename, ftype, pane=1):
		self.box=box
		self.filename=filename
		self.ftype=ftype
		self.pane=pane


class fileman:
	def __init__(self, screensurf, windoworder, xpos=0, ypos=0, argument=None):
		consolewrite("Fileman: running")
		#screensurf is the surface to blit the window to
		self.screensurf=screensurf
		#wo is a sorting variable used to sort the windows in a list
		self.wo=windoworder
		#title is the name of the window
		self.title="Fileman"
		#taskid is set automatically
		self.taskid=0
		self.argument=argument
		self.widx=500
		self.widy=400
		if self.argument==None or self.argument==list():
			self.iterfiles="."
			self.argument=["."]
		else:
			self.iterfiles=os.path.join(self.argument)
		self.title="Fileman: " + self.iterfiles
		#x and y are required.
		self.x=xpos
		self.y=ypos
		self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
		self.widsurf.fill(framebg)
		
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		#these rects are needed
		#frame close button rect
		self.closerect=self.frametoup[2]
		#rect of window content
		self.widbox=self.frametoup[0]
		#frame rect
		self.framerect=self.frametoup[1]
		self.minibox=pygame.Surface((340, 25)).convert(self.screensurf)
		self.minibox.fill(libthemeconf.tilecolor)
		self.yoff=0
		#self.closetasktx=simplefont.render("Close Task", True, framebg, frametext)
		#self.bringtoptx=simplefont.render("Bring to top", True, framebg, frametext)
		self.scup=1
		self.runexec=0
		self.filterflg=0
		self.filmenu=0
		self.vscrollbtns=vmui.makevscroll()
	def render(self):
		if self.scup==1:
			self.widsurf.fill(framebg)
			if self.runexec==0:	
				self.sw1bx=self.widsurf.blit(fvrunsw, ((2), (2)))
			else:
				self.sw1bx=self.widsurf.blit(fvviewsw, ((2), (2)))
			#ui
			self.filbtn=self.widsurf.blit(typefilter1, ((42 + 2), (2)))
			self.filbtn.x += self.x
			self.filbtn.y += self.y
			self.sw1bx.x += self.x
			self.sw1bx.y += self.y
			self.widsurf.blit(iconlist[self.filterflg], ((82 + 3), (3)))
			self.scup=0
			self.texty=self.yoff
			self.textx=150
			self.taskdict=dict()
			self.clicklist=list()
			
			
			#filelist parser (uses libfilevirtual_
			for self.fileitm in libfilevirtual.diriterate(self.argument):
				self.fnamelo=self.fileitm.lower()
				if libfilevirtual.isdir(self.fileitm, self.argument):
					if self.texty>=0 and self.texty<=self.widy:
						self.labtx=simplefont.render((self.fileitm), True, libthemeconf.tiletext, libthemeconf.tilecolor)
						self.clickbx=self.widsurf.blit(self.minibox, (self.textx, self.texty))
						self.widsurf.blit(self.labtx, (self.textx+44, self.texty+4))
						if self.fileitm=="..":
							self.widsurf.blit(typ_up.typeicon, (self.textx, self.texty))
						else:
							self.widsurf.blit(typ_dir.typeicon, (self.textx, self.texty))
						self.clickbx.x += self.x
						self.clickbx.y += self.y
						self.clicklist.extend([fileclick(self.clickbx, self.fileitm, "dir")])
						self.texty += 30
					else:
						self.texty += 30
				else:
					for self.typ in typelist:
						if self.fnamelo.endswith((self.typ.ext)) and (self.filterflg==0 or self.filterflg==self.typ.filterflg):
							if self.texty>=0 and self.texty<=self.widy:
								self.labtx=simplefont.render((self.fileitm), True, libthemeconf.tiletext, libthemeconf.tilecolor)
								self.clickbx=self.widsurf.blit(self.minibox, (self.textx, self.texty))
								self.widsurf.blit(self.labtx, (self.textx+44, self.texty+4))
								self.widsurf.blit(self.typ.typeicon, (self.textx, self.texty))
								self.clickbx.x += self.x
								self.clickbx.y += self.y
								self.clicklist.extend([fileclick(self.clickbx, self.fileitm, self.typ.qxtype)])
								self.texty += 30
							else:
								self.texty += 30
			self.texty += 30
			if self.yoff<0:
				self.widsurf.blit(self.vscrollbtns[0], (self.widx-40, 0))
			if self.texty>self.widy:
				self.widsurf.blit(self.vscrollbtns[1], (self.widx-40, self.widy-20))
		drawframe(self.framerect, self.closerect, self.widbox, self.widsurf, self.screensurf, self.title, self.wo)
		
		#filter menu render
		if self.filmenu==1:
			self.filret=vmui.passivemenu(filtermenu, (self.x + 42 + 2), (self.y + 42), fontsize=24)
			self.filmenubx=self.filret[1]
			self.filmenulist=self.filret[0]
		#task commands
		#self.clx=self.screensurf.blit(self.closetasktx, (self.x, self.y))
		#self.topx=self.screensurf.blit(self.bringtoptx, (self.x+5+self.closetasktx.get_width(), self.y))
	def movet(self, xoff, yoff):
		self.x -= xoff
		self.y -= yoff
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		self.closerect=self.frametoup[2]
		self.widbox=self.frametoup[0]
		self.framerect=self.frametoup[1]
		self.scup=1
	def resizet(self, xoff, yoff):
		#manipulate your window surface x and y sizes like so: if want only x or only y, manipulate only that.
		self.widy -= yoff
		#check the size to ensure it isn't too small (or invalid)
		if self.widy<300:
			self.widy=300
		self.scup=1
		#redefine your widsurf, and refresh rects, also do any needed sdap-specific operations.
		self.widsurf=pygame.Surface((self.widx, self.widy)).convert(self.screensurf)
		self.widsurf.fill(framebg)
		#TO SHOW THE RESIZEBAR AT THE BOTTOM OF WINDOW YOU MUST SPECIFY resizebar=1 !!!
		self.frametoup=getframes(self.x, self.y, self.widsurf, resizebar=1)
		self.closerect=self.frametoup[2]
		self.widbox=self.frametoup[0]
		self.framerect=self.frametoup[1]
	def click(self, event):
		#filter menu click processing
		if self.filmenu==1:
			if event.button==1:
				if self.filmenubx.collidepoint(event.pos):
					for self.itm in self.filmenulist:
						if self.itm.box.collidepoint(event.pos):
							self.filterflg=self.itm.retstring
							self.filmenu=0
							self.scup=1
							return
				else:
					self.filmenu=0
		if event.button==4:
			if event.pos[0]>150:
				if self.yoff<0:
					self.yoff += 30
					#scupdate=1
					self.scup=1
				return
		if event.button==5:
			if event.pos[0]>150:
				if self.texty>self.widy:
					self.yoff -= 30
					#scupdate=1
					self.scup=1
				if self.yoff>0:
					self.yoff=0
					#scupdate=1
					self.scup=1
				return
		#run view switch
		if self.sw1bx.collidepoint(event.pos)==1 and event.button==1:
			self.scup=1
			if self.runexec==0:
				self.runexec=1
			else:
				self.runexec=0
		#filter button click processing
		if self.filbtn.collidepoint(event.pos)==1 and event.button==1:
			self.filmenu=1
		#tile click processor
		for self.f in self.clicklist:
			if self.f.box.collidepoint(event.pos)==1 and event.button==1:
				#program launchers
				
				if self.runexec==0:
					if self.f.ftype=="trom":
						subprocess.Popen(["python", "MK2-RUN.py", (os.path.join(self.iterfiles, self.f.filename))])
					if self.f.ftype=="streg":
						subprocess.Popen(["python", "MK2-RUN.py", (os.path.join(self.iterfiles, self.f.filename))])
				else:
					if self.f.ftype=="trom":
						subprocess.Popen(["python", "MK2-TOOLS.py", "codeview", (os.path.join(self.iterfiles, self.f.filename))])
					if self.f.ftype=="streg":
						subprocess.Popen(["python", "MK2-TOOLS.py", "codeview", (os.path.join(self.iterfiles, self.f.filename))])
				if self.f.ftype=="tasm":
					subprocess.Popen(["python", "MK2-TOOLS.py", "codeview", (os.path.join(self.iterfiles, self.f.filename))])
				if self.f.ftype=="log":
					subprocess.Popen(["python", "MK2-TOOLS.py", "codeview", (os.path.join(self.iterfiles, self.f.filename))])
				if self.f.ftype=="dmp":
					subprocess.Popen(["python", "MK2-TOOLS.py", "codeview", (os.path.join(self.iterfiles, self.f.filename))])
				
				if self.f.ftype=="img":
					subprocess.Popen(["python", "MK2-TOOLS.py", "imgview", (os.path.join(self.iterfiles, self.f.filename))])
				if self.f.ftype=="text":
					subprocess.Popen(["python", "MK2-TOOLS.py", "textview", (os.path.join(self.iterfiles, self.f.filename))])
				#special directory handler
				if self.f.ftype=="dir":
					self.scup=1
					self.yoff=0
					#home directory (SBTCVM's repository root directory)
					self.argument=libfilevirtual.dir_cd(self.argument, self.f.filename)
					self.iterfiles=os.path.join(*self.argument)
					self.title="Fileman: " + self.iterfiles
					return
	def clickup(self, event):
		return
	def keydown(self, event):
		return
	def keyup(self, event):
		return
	def close(self):
		return
	def hostquit(self):
		return
	def sig(self):
		return
	def que(self, signal):
		return
		


