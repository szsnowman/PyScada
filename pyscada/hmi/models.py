# -*- coding: utf-8 -*-
from pyscada.models import Variable

from django.db import models 
from django.contrib.auth.models import Group
import random

class Color(models.Model):
	id 		= models.AutoField(primary_key=True)
	name 	= models.SlugField(max_length=80, verbose_name="variable name")
	R 		= models.PositiveSmallIntegerField(default=0)
	G 		= models.PositiveSmallIntegerField(default=0)
	B 		= models.PositiveSmallIntegerField(default=0)
	def __unicode__(self):
		return unicode('rgb('+str(self.R)+', '+str(self.G)+', '+str(self.B)+', '+')')
	def color_code(self):
		return unicode('#%02x%02x%02x' % (self.R, self.G, self.B))	


class VariableDisplayPropery(models.Model):
	hmi_variable		= models.OneToOneField(Variable)
	short_name			= models.CharField(default='',max_length=80, verbose_name="variable short name")
	chart_line_color 	= models.ForeignKey('Color',default=0,null=True, on_delete=models.SET_NULL)
	chart_line_thickness_choices = ((3,'3Px'),)
	chart_line_thickness = models.PositiveSmallIntegerField(default=3,choices=chart_line_thickness_choices)
	def variable_name(self):
		if self.short_name and self.short_name != '-':
			return self.short_name
		else:
			return self.hmi_variable.variable_name
	def chart_line_color_code(self):
		if self.chart_line_color and self.chart_line_color.id != 1:
			return self.chart_line_color.color_code()
		else:
			c = 51
			id = self.pk+1
			c = c%id
			while c >= 51:
				id = id-c
				c = c%id
			return Color.objects.get(id=id).color_code()

class ControlItem(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	position			= models.PositiveSmallIntegerField(default=0)
	type_choices 	= ((0,'label blue'),(1,'label light blue'),(2,'label ok'),(3,'label warning'),(4,'label alarm'),(5,'Control Element'),(6,'Display Value'),)
	type			= models.PositiveSmallIntegerField(default=0,choices=type_choices)
	variable    		= models.ForeignKey(Variable,null=True, on_delete=models.SET_NULL)
	class Meta:
		ordering = ['position']
	def __unicode__(self):
		return unicode(self.label+" ("+self.variable.variable_name + ")")
	def web_id(self):
		return unicode(self.id.__str__() + "-" + self.label.replace(' ','_')+"-"+self.variable.variable_name.replace(' ','_'))


class Chart(models.Model):
	id 				= models.AutoField(primary_key=True)
	title			= models.CharField(max_length=400, default='')
	x_axis_label	= models.CharField(max_length=400, default='',blank=True)
	x_axis_ticks	= models.PositiveSmallIntegerField(default=6)
	y_axis_label	= models.CharField(max_length=400, default='',blank=True)
	y_axis_min		= models.FloatField(default=0)
	y_axis_max		= models.FloatField(default=100)
	variables		= models.ManyToManyField(Variable)
	def __unicode__(self):
		return unicode(str(self.id) + ': ' + self.title)
	

class Page(models.Model):
	id 				= models.AutoField(primary_key=True)
	title 			= models.CharField(max_length=400, default='')
	link_title		= models.SlugField(max_length=80, default='')
	position			= models.PositiveSmallIntegerField(default=0)
	class Meta:
		ordering = ['position']
	def __unicode__(self):
		return unicode(self.link_title.replace(' ','_'))


class ControlPanel(models.Model):
	id 				= models.AutoField(primary_key=True)
	title			= models.CharField(max_length=400, default='')
	items 			= models.ManyToManyField(ControlItem,blank=True)
	def __unicode__(self):
		return unicode(str(self.id) + ': ' + self.title)


class CustomHTMLPanel(models.Model):
	id 				= models.AutoField(primary_key=True)
	title			= models.CharField(max_length=400, default='',blank=True)
	html 			= models.TextField()	
	def __unicode__(self):
		return unicode(str(self.id) + ': ' + self.title)

class SlidingPanelMenu(models.Model):
	id 				= models.AutoField(primary_key=True)
	title			= models.CharField(max_length=400, default='')
	position_choices = ((0,'Control Menu'),(1,'left'),(2,'right'))
	position			= models.PositiveSmallIntegerField(default=0,choices=position_choices)
	control_panel   = models.ForeignKey(ControlPanel,blank=True,null=True,default=None)
	visable			= models.BooleanField(default=True)
	def __unicode__(self):
		return unicode(self.title)

class ChartSet(models.Model):
	size_choices	= ((0,'side by side (1/2)'),(1,'side by side (2/3|1/3)'),(2,'side by side (1/3|2/3)'),)
	id 				= models.AutoField(primary_key=True)
	distribution	= models.PositiveSmallIntegerField(max_length=20, default=0,choices=size_choices)
	chart_1			= models.ForeignKey(Chart,blank=True,null=True,related_name="chart_1",verbose_name="left Chart")
	chart_2			= models.ForeignKey(Chart,blank=True,null=True,related_name="chart_2",verbose_name="right Chart")
	def __unicode__(self):
		return unicode(str(self.id) + ': ' + (self.chart_1.title if self.chart_1 else 'None')  + ' | ' +  (self.chart_2.title if self.chart_2 else 'None') )
		

class Widget(models.Model):
	id 				= models.AutoField(primary_key=True)
	title			= models.CharField(max_length=400, default='',blank=True)	
	page 			= models.ForeignKey(Page,default=0,null=True, on_delete=models.SET_NULL)
	row_choises  	= ((0,"1. row"),(1,"2. row"),(2,"3. row"),(3,"4. row"),(4,"5. row"),(5,"6. row"),(6,"7. row"),(7,"8. row"),(8,"9. row"),(9,"10. row"),(10,"11. row"),(11,"12. row"),)
	row				= models.PositiveSmallIntegerField(default=0,choices=row_choises)
	col_choises		= ((0,"1. col"),(1,"2. col"),(2,"3. col"),(3,"4. col"))
	col 			= models.PositiveSmallIntegerField(default=0,choices=col_choises)
	size_choices 	= ((4,'page width'),(3,'3/4 page width'),(2,'1/2 page width'),(1,'1/4 page width'))
	size			= models.PositiveSmallIntegerField(default=4,choices=size_choices)
	chart			= models.ForeignKey(Chart,blank=True,null=True,default=None)
	chart_set		= models.ForeignKey(ChartSet,blank=True,null=True,default=None)
	control_panel  = models.ForeignKey(ControlPanel,blank=True,null=True,default=None)
	custom_html_panel = models.ForeignKey(CustomHTMLPanel,blank=True,null=True,default=None)
	visable			= models.BooleanField(default=True)
	class Meta:
		ordering = ['row','col']
	def __unicode__(self):
		return unicode(str(self.id) + ': ' + self.page.title + ', ' + self.title)
	
	def css_class(self):
		widget_size = "col-xs-12 col-sm-12 col-md-12 col-lg-12"
		if self.size == 3:
			widget_size = "col-xs-8 col-sm-8 col-md-8 col-lg-8"
		elif self.size == 2:
			widget_size = "col-xs-6 col-sm-6 col-md-6 col-lg-6"
		elif self.size == 1:
			widget_size = "col-xs-4 col-sm-4 col-md-4 col-lg-4"
		return unicode('widget_row_' + str(self.row) + ' widget_col_' + str(self.col) + ' ' + widget_size)

class GroupDisplayPermission(models.Model):
	hmi_group			= models.OneToOneField(Group)
	pages 				= models.ManyToManyField(Page,blank=True)
	sliding_panel_menus = models.ManyToManyField(SlidingPanelMenu,blank=True)
	charts 				= models.ManyToManyField(Chart,blank=True)
	control_items 		= models.ManyToManyField(ControlItem,blank=True)
	widget 				= models.ManyToManyField(Widget,blank=True)
	def __unicode__(self):
		return unicode(self.hmi_group.name)