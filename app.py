from flask import Flask, render_template, request, jsonify, send_file
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from dataclasses import dataclass
from typing import List, Tuple
import io
import base64
import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
import tempfile
import os

app = Flask(__name__)

@dataclass
class Room:
    x: float
    y: float
    width: float
    height: float
    name: str
    color: str
    
    def split_horizontal(self, ratio: float) -> Tuple['Room', 'Room']:
        h1 = self.height * ratio
        h2 = self.height - h1
        top = Room(self.x, self.y + h1, self.width, h2, "", "")
        bottom = Room(self.x, self.y, self.width, h1, "", "")
        return bottom, top
    
    def split_vertical(self, ratio: float) -> Tuple['Room', 'Room']:
        w1 = self.width * ratio
        w2 = self.width - w1
        left = Room(self.x, self.y, w1, self.height, "", "")
        right = Room(self.x + w1, self.y, w2, self.height, "", "")
        return left, right

@dataclass
class Door:
    x: float
    y: float
    width: float
    height: float
    orientation: str

class FloorPlanGenerator:
    def __init__(self, width: float, height: float, entrance_dir: str):
        self.width = width
        self.height = height
        self.entrance_dir = entrance_dir
        self.rooms: List[Room] = []
        self.doors: List[Door] = []
        
        self.colors = {
            'sitout': '#F5F5F5',
            'parking': '#E8E8E8',
            'living': '#E6F3FF',
            'bedroom1': '#FFE6F0',
            'bedroom2': '#FFFACD',
            'bathroom1': '#E0F7FA',
            'bathroom2': '#E0F7FA',
            'kitchen': '#FFF9E6',
            'dining': '#E8F5E9',
            'hallway': 'white',
            'storage': '#FFF8DC'
        }
        
    def generate_layout(self):
        if self.entrance_dir == 'North':
            layout_type = random.choice([1, 2, 3])
            if layout_type == 1:
                self._generate_north_layout_1()
            elif layout_type == 2:
                self._generate_north_layout_2()
            else:
                self._generate_north_layout_3()
        elif self.entrance_dir == 'East':
            layout_type = random.choice([1, 2, 3])
            if layout_type == 1:
                self._generate_east_layout_1()
            elif layout_type == 2:
                self._generate_east_layout_2()
            else:
                self._generate_east_layout_3()
        else:
            layout_type = random.choice([1, 2, 3])
            if layout_type == 1:
                self._generate_west_layout_1()
            elif layout_type == 2:
                self._generate_west_layout_2()
            else:
                self._generate_west_layout_3()
        
        self._add_doors()
    
    def _add_doors(self):
        door_thickness = 0.3
        door_size = min(self.width, self.height) * 0.08
        
        for room in self.rooms:
            if room.name == 'Sitout':
                if self.entrance_dir == 'North':
                    door_x = room.x + room.width/2 - door_size/2
                    door_y = room.y + room.height - door_thickness
                    self.doors.append(Door(door_x, door_y, door_size, door_thickness, 'horizontal'))
                elif self.entrance_dir == 'East':
                    door_x = room.x + room.width - door_thickness
                    door_y = room.y + room.height/2 - door_size/2
                    self.doors.append(Door(door_x, door_y, door_thickness, door_size, 'vertical'))
                else:
                    door_x = room.x
                    door_y = room.y + room.height/2 - door_size/2
                    self.doors.append(Door(door_x, door_y, door_thickness, door_size, 'vertical'))
            
            elif 'Bedroom' in room.name:
                hallway_room = next((r for r in self.rooms if r.name == 'Hallway'), None)
                
                if hallway_room:
                    room_center_x = room.x + room.width/2
                    room_center_y = room.y + room.height/2
                    hall_center_x = hallway_room.x + hallway_room.width/2
                    hall_center_y = hallway_room.y + hallway_room.height/2
                    
                    dx = abs(room_center_x - hall_center_x)
                    dy = abs(room_center_y - hall_center_y)
                    
                    if dx > dy:
                        if room_center_x < hall_center_x:
                            door_x = room.x + room.width - door_thickness
                            door_y = room.y + room.height/2 - door_size/2
                            self.doors.append(Door(door_x, door_y, door_thickness, door_size, 'vertical'))
                        else:
                            door_x = room.x
                            door_y = room.y + room.height/2 - door_size/2
                            self.doors.append(Door(door_x, door_y, door_thickness, door_size, 'vertical'))
                    else:
                        if room_center_y < hall_center_y:
                            door_x = room.x + room.width/2 - door_size/2
                            door_y = room.y + room.height - door_thickness
                            self.doors.append(Door(door_x, door_y, door_size, door_thickness, 'horizontal'))
                        else:
                            door_x = room.x + room.width/2 - door_size/2
                            door_y = room.y
                            self.doors.append(Door(door_x, door_y, door_size, door_thickness, 'horizontal'))
    
    def _generate_north_layout_1(self):
        """North entrance - Layout Variation 1"""
        plot = Room(0, 0, self.width, self.height, "", "")
        bottom_section, temp = plot.split_horizontal(0.30)
        middle_section, top_section = temp.split_horizontal(0.57)
        
        left_entrance, right_entrance = top_section.split_vertical(0.5)
        self.rooms.append(Room(left_entrance.x, left_entrance.y, left_entrance.width, 
                              left_entrance.height, 'Sitout', self.colors['sitout']))
        self.rooms.append(Room(right_entrance.x, right_entrance.y, right_entrance.width, 
                              right_entrance.height, 'Parking', self.colors['parking']))
        
        left_mid, temp_mid = middle_section.split_vertical(0.30)
        center_mid, right_mid = temp_mid.split_vertical(0.43)
        
        self.rooms.append(Room(left_mid.x, left_mid.y, left_mid.width, left_mid.height,
                              'Living Room', self.colors['living']))
        self.rooms.append(Room(center_mid.x, center_mid.y, center_mid.width, center_mid.height,
                              'Hallway', self.colors['hallway']))
        
        bathroom1, bedroom1 = right_mid.split_horizontal(0.25)
        self.rooms.append(Room(bedroom1.x, bedroom1.y, bedroom1.width, bedroom1.height,
                              'Bedroom 1', self.colors['bedroom1']))
        self.rooms.append(Room(bathroom1.x, bathroom1.y, bathroom1.width, bathroom1.height,
                              'Bathroom 1', self.colors['bathroom1']))
        
        left_bot, temp_bot = bottom_section.split_vertical(0.30)
        center_bot, right_bot = temp_bot.split_vertical(0.43)
        
        bedroom2, bathroom2 = left_bot.split_vertical(0.70)
        self.rooms.append(Room(bedroom2.x, bedroom2.y, bedroom2.width, bedroom2.height,
                              'Bedroom 2', self.colors['bedroom2']))
        self.rooms.append(Room(bathroom2.x, bathroom2.y, bathroom2.width, bathroom2.height,
                              'Bathroom 2', self.colors['bathroom2']))
        
        self.rooms.append(Room(center_bot.x, center_bot.y, center_bot.width, center_bot.height,
                              'Dining', self.colors['dining']))
        self.rooms.append(Room(right_bot.x, right_bot.y, right_bot.width, right_bot.height,
                              'Kitchen', self.colors['kitchen']))
    
    def _generate_north_layout_2(self):
        """North entrance - Layout Variation 2"""
        plot = Room(0, 0, self.width, self.height, "", "")
        rest, top = plot.split_horizontal(0.75)
        
        sitout, parking = top.split_vertical(0.5)
        self.rooms.append(Room(sitout.x, sitout.y, sitout.width, sitout.height,
                              'Sitout', self.colors['sitout']))
        self.rooms.append(Room(parking.x, parking.y, parking.width, parking.height,
                              'Parking', self.colors['parking']))
        
        left_col, temp = rest.split_vertical(0.35)
        center_col, right_col = temp.split_vertical(0.46)
        
        bedroom2, living = left_col.split_horizontal(0.50)
        self.rooms.append(Room(living.x, living.y, living.width, living.height,
                              'Living Room', self.colors['living']))
        self.rooms.append(Room(bedroom2.x, bedroom2.y, bedroom2.width, bedroom2.height,
                              'Bedroom 2', self.colors['bedroom2']))
        
        bath2_w = bedroom2.width * 0.35
        bath2_h = bedroom2.height * 0.35
        self.rooms.append(Room(bedroom2.x, bedroom2.y, bath2_w, bath2_h,
                              'Bath 2', self.colors['bathroom2']))
        
        dining, hallway = center_col.split_horizontal(0.40)
        self.rooms.append(Room(hallway.x, hallway.y, hallway.width, hallway.height,
                              'Hallway', self.colors['hallway']))
        self.rooms.append(Room(dining.x, dining.y, dining.width, dining.height,
                              'Dining', self.colors['dining']))
        
        kitchen, bedroom1 = right_col.split_horizontal(0.45)
        self.rooms.append(Room(bedroom1.x, bedroom1.y, bedroom1.width, bedroom1.height,
                              'Bedroom 1', self.colors['bedroom1']))
        self.rooms.append(Room(kitchen.x, kitchen.y, kitchen.width, kitchen.height,
                              'Kitchen', self.colors['kitchen']))
        
        bath1_w = bedroom1.width * 0.35
        bath1_h = bedroom1.height * 0.35
        self.rooms.append(Room(bedroom1.x + bedroom1.width - bath1_w, bedroom1.y,
                              bath1_w, bath1_h, 'Bath 1', self.colors['bathroom1']))
    
    def _generate_north_layout_3(self):
        """North entrance - Layout Variation 3"""
        plot = Room(0, 0, self.width, self.height, "", "")
        bottom, temp = plot.split_horizontal(0.35)
        middle, top = temp.split_horizontal(0.62)
        
        sitout, parking = top.split_vertical(0.5)
        self.rooms.append(Room(sitout.x, sitout.y, sitout.width, sitout.height,
                              'Sitout', self.colors['sitout']))
        self.rooms.append(Room(parking.x, parking.y, parking.width, parking.height,
                              'Parking', self.colors['parking']))
        
        left, temp = middle.split_vertical(0.25)
        mid_left, temp2 = temp.split_vertical(0.33)
        mid_right, right = temp2.split_vertical(0.50)
        
        self.rooms.append(Room(left.x, left.y, left.width, left.height,
                              'Living Room', self.colors['living']))
        self.rooms.append(Room(mid_left.x, mid_left.y, mid_left.width, mid_left.height,
                              'Bedroom 2', self.colors['bedroom2']))
        
        bath2_w = mid_left.width * 0.40
        bath2_h = mid_left.height * 0.35
        self.rooms.append(Room(mid_left.x, mid_left.y + mid_left.height - bath2_h,
                              bath2_w, bath2_h, 'Bath 2', self.colors['bathroom2']))
        
        self.rooms.append(Room(mid_right.x, mid_right.y, mid_right.width, mid_right.height,
                              'Hallway', self.colors['hallway']))
        self.rooms.append(Room(right.x, right.y, right.width, right.height,
                              'Bedroom 1', self.colors['bedroom1']))
        
        bath1_w = right.width * 0.40
        bath1_h = right.height * 0.35
        self.rooms.append(Room(right.x + right.width - bath1_w, right.y + right.height - bath1_h,
                              bath1_w, bath1_h, 'Bath 1', self.colors['bathroom1']))
        
        dining, kitchen = bottom.split_vertical(0.50)
        self.rooms.append(Room(dining.x, dining.y, dining.width, dining.height,
                              'Dining', self.colors['dining']))
        self.rooms.append(Room(kitchen.x, kitchen.y, kitchen.width, kitchen.height,
                              'Kitchen', self.colors['kitchen']))
    
    def _generate_east_layout_1(self):
        """East entrance - Layout Variation 1"""
        plot = Room(0, 0, self.width, self.height, "", "")
        left, temp = plot.split_vertical(0.30)
        middle, right = temp.split_vertical(0.57)
        
        parking, sitout = right.split_horizontal(0.5)
        self.rooms.append(Room(sitout.x, sitout.y, sitout.width, sitout.height,
                              'Sitout', self.colors['sitout']))
        self.rooms.append(Room(parking.x, parking.y, parking.width, parking.height,
                              'Parking', self.colors['parking']))
        
        bottom, temp = middle.split_horizontal(0.35)
        mid, top = temp.split_horizontal(0.46)
        
        self.rooms.append(Room(bottom.x, bottom.y, bottom.width, bottom.height,
                              'Kitchen', self.colors['kitchen']))
        self.rooms.append(Room(mid.x, mid.y, mid.width, mid.height,
                              'Hallway', self.colors['hallway']))
        self.rooms.append(Room(top.x, top.y, top.width, top.height,
                              'Living Room', self.colors['living']))
        
        bottom_left, temp = left.split_horizontal(0.35)
        mid_left, top_left = temp.split_horizontal(0.46)
        
        self.rooms.append(Room(bottom_left.x, bottom_left.y, bottom_left.width, bottom_left.height,
                              'Bedroom 2', self.colors['bedroom2']))
        
        bath2_w = bottom_left.width * 0.35
        bath2_h = bottom_left.height * 0.35
        self.rooms.append(Room(bottom_left.x + bottom_left.width - bath2_w, 
                              bottom_left.y + bottom_left.height - bath2_h,
                              bath2_w, bath2_h, 'Bath 2', self.colors['bathroom2']))
        
        self.rooms.append(Room(mid_left.x, mid_left.y, mid_left.width, mid_left.height,
                              'Dining', self.colors['dining']))
        self.rooms.append(Room(top_left.x, top_left.y, top_left.width, top_left.height,
                              'Bedroom 1', self.colors['bedroom1']))
        
        bath1_w = top_left.width * 0.35
        bath1_h = top_left.height * 0.35
        self.rooms.append(Room(top_left.x + top_left.width - bath1_w, top_left.y,
                              bath1_w, bath1_h, 'Bath 1', self.colors['bathroom1']))
    
    def _generate_east_layout_2(self):
        """East entrance - Layout Variation 2"""
        plot = Room(0, 0, self.width, self.height, "", "")
        left, temp = plot.split_vertical(0.35)
        center, right = temp.split_vertical(0.62)
        
        parking, sitout = right.split_horizontal(0.5)
        self.rooms.append(Room(sitout.x, sitout.y, sitout.width, sitout.height,
                              'Sitout', self.colors['sitout']))
        self.rooms.append(Room(parking.x, parking.y, parking.width, parking.height,
                              'Parking', self.colors['parking']))
        
        kitchen, temp = center.split_horizontal(0.30)
        hallway, dining = temp.split_horizontal(0.43)
        
        self.rooms.append(Room(kitchen.x, kitchen.y, kitchen.width, kitchen.height,
                              'Kitchen', self.colors['kitchen']))
        self.rooms.append(Room(hallway.x, hallway.y, hallway.width, hallway.height,
                              'Hallway', self.colors['hallway']))
        self.rooms.append(Room(dining.x, dining.y, dining.width, dining.height,
                              'Dining', self.colors['dining']))
        
        bed1, temp = left.split_horizontal(0.33)
        living, bed2 = temp.split_horizontal(0.50)
        
        self.rooms.append(Room(bed1.x, bed1.y, bed1.width, bed1.height,
                              'Bedroom 1', self.colors['bedroom1']))
        bath1_w = bed1.width * 0.35
        bath1_h = bed1.height * 0.35
        self.rooms.append(Room(bed1.x, bed1.y + bed1.height - bath1_h,
                              bath1_w, bath1_h, 'Bath 1', self.colors['bathroom1']))
        
        self.rooms.append(Room(living.x, living.y, living.width, living.height,
                              'Living Room', self.colors['living']))
        
        self.rooms.append(Room(bed2.x, bed2.y, bed2.width, bed2.height,
                              'Bedroom 2', self.colors['bedroom2']))
        bath2_w = bed2.width * 0.35
        bath2_h = bed2.height * 0.35
        self.rooms.append(Room(bed2.x, bed2.y,
                              bath2_w, bath2_h, 'Bath 2', self.colors['bathroom2']))
    
    def _generate_east_layout_3(self):
        """East entrance - Layout Variation 3"""
        plot = Room(0, 0, self.width, self.height, "", "")
        sect1, temp = plot.split_vertical(0.25)
        sect2, temp2 = temp.split_vertical(0.33)
        sect3, sect4 = temp2.split_vertical(0.50)
        
        parking, sitout = sect4.split_horizontal(0.5)
        self.rooms.append(Room(sitout.x, sitout.y, sitout.width, sitout.height,
                              'Sitout', self.colors['sitout']))
        self.rooms.append(Room(parking.x, parking.y, parking.width, parking.height,
                              'Parking', self.colors['parking']))
        
        bed1, bed2 = sect1.split_horizontal(0.50)
        self.rooms.append(Room(bed1.x, bed1.y, bed1.width, bed1.height,
                              'Bedroom 1', self.colors['bedroom1']))
        self.rooms.append(Room(bed2.x, bed2.y, bed2.width, bed2.height,
                              'Bedroom 2', self.colors['bedroom2']))
        
        bath1_w = bed1.width * 0.40
        bath1_h = bed1.height * 0.35
        self.rooms.append(Room(bed1.x + bed1.width - bath1_w, bed1.y,
                              bath1_w, bath1_h, 'Bath 1', self.colors['bathroom1']))
        
        bath2_w = bed2.width * 0.40
        bath2_h = bed2.height * 0.35
        self.rooms.append(Room(bed2.x + bed2.width - bath2_w, bed2.y + bed2.height - bath2_h,
                              bath2_w, bath2_h, 'Bath 2', self.colors['bathroom2']))
        
        kitchen, dining = sect2.split_horizontal(0.50)
        self.rooms.append(Room(kitchen.x, kitchen.y, kitchen.width, kitchen.height,
                              'Kitchen', self.colors['kitchen']))
        self.rooms.append(Room(dining.x, dining.y, dining.width, dining.height,
                              'Dining', self.colors['dining']))
        
        bottom3, temp = sect3.split_horizontal(0.35)
        hallway, living = temp.split_horizontal(0.46)
        
        self.rooms.append(Room(bottom3.x, bottom3.y, bottom3.width, bottom3.height,
                              'Storage', self.colors['storage']))
        self.rooms.append(Room(hallway.x, hallway.y, hallway.width, hallway.height,
                              'Hallway', self.colors['hallway']))
        self.rooms.append(Room(living.x, living.y, living.width, living.height,
                              'Living Room', self.colors['living']))
    
    def _generate_west_layout_1(self):
        """West entrance - Layout Variation 1"""
        plot = Room(0, 0, self.width, self.height, "", "")
        left, temp = plot.split_vertical(0.30)
        middle, right = temp.split_vertical(0.57)
        
        parking, sitout = left.split_horizontal(0.5)
        self.rooms.append(Room(sitout.x, sitout.y, sitout.width, sitout.height,
                              'Sitout', self.colors['sitout']))
        self.rooms.append(Room(parking.x, parking.y, parking.width, parking.height,
                              'Parking', self.colors['parking']))
        
        bottom, temp = middle.split_horizontal(0.35)
        mid, top = temp.split_horizontal(0.46)
        
        self.rooms.append(Room(bottom.x, bottom.y, bottom.width, bottom.height,
                              'Dining', self.colors['dining']))
        self.rooms.append(Room(mid.x, mid.y, mid.width, mid.height,
                              'Hallway', self.colors['hallway']))
        self.rooms.append(Room(top.x, top.y, top.width, top.height,
                              'Living Room', self.colors['living']))
        
        bottom_right, temp = right.split_horizontal(0.35)
        mid_right, top_right = temp.split_horizontal(0.46)
        
        self.rooms.append(Room(bottom_right.x, bottom_right.y, bottom_right.width, bottom_right.height,
                              'Kitchen', self.colors['kitchen']))
        self.rooms.append(Room(mid_right.x, mid_right.y, mid_right.width, mid_right.height,
                              'Bedroom 2', self.colors['bedroom2']))
        
        bath2_w = mid_right.width * 0.35
        bath2_h = mid_right.height * 0.35
        self.rooms.append(Room(mid_right.x, mid_right.y,
                              bath2_w, bath2_h, 'Bath 2', self.colors['bathroom2']))
        
        self.rooms.append(Room(top_right.x, top_right.y, top_right.width, top_right.height,
                              'Bedroom 1', self.colors['bedroom1']))
        
        bath1_w = top_right.width * 0.35
        bath1_h = top_right.height * 0.35
        self.rooms.append(Room(top_right.x, top_right.y + top_right.height - bath1_h,
                              bath1_w, bath1_h, 'Bath 1', self.colors['bathroom1']))
    
    def _generate_west_layout_2(self):
        """West entrance - Layout Variation 2"""
        plot = Room(0, 0, self.width, self.height, "", "")
        left, temp = plot.split_vertical(0.25)
        center, right = temp.split_vertical(0.53)
        
        parking, sitout = left.split_horizontal(0.5)
        self.rooms.append(Room(sitout.x, sitout.y, sitout.width, sitout.height,
                              'Sitout', self.colors['sitout']))
        self.rooms.append(Room(parking.x, parking.y, parking.width, parking.height,
                              'Parking', self.colors['parking']))
        
        dining, temp = center.split_horizontal(0.30)
        hallway, living = temp.split_horizontal(0.43)
        
        self.rooms.append(Room(dining.x, dining.y, dining.width, dining.height,
                              'Dining', self.colors['dining']))
        self.rooms.append(Room(hallway.x, hallway.y, hallway.width, hallway.height,
                              'Hallway', self.colors['hallway']))
        self.rooms.append(Room(living.x, living.y, living.width, living.height,
                              'Living Room', self.colors['living']))
        
        kitchen, temp = right.split_horizontal(0.33)
        bed1, bed2 = temp.split_horizontal(0.50)
        
        self.rooms.append(Room(kitchen.x, kitchen.y, kitchen.width, kitchen.height,
                              'Kitchen', self.colors['kitchen']))
        
        self.rooms.append(Room(bed1.x, bed1.y, bed1.width, bed1.height,
                              'Bedroom 1', self.colors['bedroom1']))
        bath1_w = bed1.width * 0.35
        bath1_h = bed1.height * 0.35
        self.rooms.append(Room(bed1.x + bed1.width - bath1_w, bed1.y + bed1.height - bath1_h,
                              bath1_w, bath1_h, 'Bath 1', self.colors['bathroom1']))
        
        self.rooms.append(Room(bed2.x, bed2.y, bed2.width, bed2.height,
                              'Bedroom 2', self.colors['bedroom2']))
        bath2_w = bed2.width * 0.35
        bath2_h = bed2.height * 0.35
        self.rooms.append(Room(bed2.x + bed2.width - bath2_w, bed2.y,
                              bath2_w, bath2_h, 'Bath 2', self.colors['bathroom2']))
    
    def _generate_west_layout_3(self):
        """West entrance - Layout Variation 3"""
        plot = Room(0, 0, self.width, self.height, "", "")
        sect1, temp = plot.split_vertical(0.25)
        sect2, temp2 = temp.split_vertical(0.33)
        sect3, sect4 = temp2.split_vertical(0.50)
        
        parking, sitout = sect1.split_horizontal(0.5)
        self.rooms.append(Room(sitout.x, sitout.y, sitout.width, sitout.height,
                              'Sitout', self.colors['sitout']))
        self.rooms.append(Room(parking.x, parking.y, parking.width, parking.height,
                              'Parking', self.colors['parking']))
        
        storage, temp = sect2.split_horizontal(0.35)
        hallway, living = temp.split_horizontal(0.46)
        
        self.rooms.append(Room(storage.x, storage.y, storage.width, storage.height,
                              'Storage', self.colors['storage']))
        self.rooms.append(Room(hallway.x, hallway.y, hallway.width, hallway.height,
                              'Hallway', self.colors['hallway']))
        self.rooms.append(Room(living.x, living.y, living.width, living.height,
                              'Living Room', self.colors['living']))
        
        kitchen, dining = sect3.split_horizontal(0.50)
        self.rooms.append(Room(kitchen.x, kitchen.y, kitchen.width, kitchen.height,
                              'Kitchen', self.colors['kitchen']))
        self.rooms.append(Room(dining.x, dining.y, dining.width, dining.height,
                              'Dining', self.colors['dining']))
        
        bed1, bed2 = sect4.split_horizontal(0.50)
        self.rooms.append(Room(bed1.x, bed1.y, bed1.width, bed1.height,
                              'Bedroom 1', self.colors['bedroom1']))
        self.rooms.append(Room(bed2.x, bed2.y, bed2.width, bed2.height,
                              'Bedroom 2', self.colors['bedroom2']))
        
        bath1_w = bed1.width * 0.40
        bath1_h = bed1.height * 0.35
        self.rooms.append(Room(bed1.x, bed1.y,
                              bath1_w, bath1_h, 'Bath 1', self.colors['bathroom1']))
        
        bath2_w = bed2.width * 0.40
        bath2_h = bed2.height * 0.35
        self.rooms.append(Room(bed2.x, bed2.y + bed2.height - bath2_h,
                              bath2_w, bath2_h, 'Bath 2', self.colors['bathroom2']))
    
    def draw_to_buffer(self):
        fig, ax = plt.subplots(figsize=(12, 10))
        
        ax.add_patch(patches.Rectangle((0, 0), self.width, self.height,
                                        fill=False, edgecolor='black', linewidth=4))
        
        for room in self.rooms:
            ax.add_patch(patches.Rectangle((room.x, room.y), room.width, room.height,
                                          fill=True, facecolor=room.color,
                                          edgecolor='black', linewidth=2))
            area = room.width * room.height
            label_text = f"{room.name}\n{area:.2f} sq"
            ax.text(room.x + room.width/2, room.y + room.height/2, label_text,
                   ha='center', va='center', fontweight='bold', fontsize=9)
        
        door_color = '#5C4033'
        for door in self.doors:
            ax.add_patch(patches.Rectangle((door.x, door.y), door.width, door.height,
                                          fill=True, facecolor=door_color,
                                          edgecolor='black', linewidth=2.5))
            
            if door.orientation == 'horizontal':
                arc = patches.Arc((door.x + door.width/2, door.y), 
                                 door.width, door.width,
                                 angle=0, theta1=0, theta2=90,
                                 color=door_color, linewidth=2, linestyle='--')
                ax.add_patch(arc)
            else:
                arc = patches.Arc((door.x, door.y + door.height/2), 
                                 door.height, door.height,
                                 angle=0, theta1=0, theta2=90,
                                 color=door_color, linewidth=2, linestyle='--')
                ax.add_patch(arc)
        
        margin = 2.0
        ax.text(self.width / 2, -margin, 'SOUTH', ha='center', fontsize=16,
                fontweight='bold', color='red', bbox=dict(boxstyle='round', facecolor='wheat'))
        ax.text(self.width / 2, self.height + margin * 0.6, 'NORTH', ha='center',
                fontsize=16, fontweight='bold', color='blue',
                bbox=dict(boxstyle='round', facecolor='lightblue'))
        ax.text(self.width + margin * 1.2, self.height / 2, 'EAST', va='center',
                rotation=270, fontsize=16, fontweight='bold', color='green',
                bbox=dict(boxstyle='round', facecolor='lightgreen'))
        ax.text(-margin * 1.2, self.height / 2, 'WEST', va='center',
                rotation=90, fontsize=16, fontweight='bold', color='purple',
                bbox=dict(boxstyle='round', facecolor='plum'))
        
        ax.annotate('', xy=(0, -margin*1.3), xytext=(self.width, -margin*1.3),
                   arrowprops=dict(arrowstyle='<->', color='black', lw=2.5))
        ax.text(self.width/2, -margin*1.6, f'Width: {self.width} units',
               ha='center', fontsize=13, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='black', linewidth=1.5))
        
        ax.annotate('', xy=(-margin*1.8, 0), xytext=(-margin*1.8, self.height),
                   arrowprops=dict(arrowstyle='<->', color='black', lw=2.5))
        ax.text(-margin*2.3, self.height/2, f'Height: {self.height} units',
               va='center', rotation=90, fontsize=13, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='black', linewidth=1.5))
        
        entrance_color = 'darkred'
        if self.entrance_dir == 'North':
            ax.annotate('', xy=(self.width/2, self.height),
                       xytext=(self.width/2, self.height + margin*1.8),
                       arrowprops=dict(arrowstyle='->', color=entrance_color, lw=4))
            ax.text(self.width/2, self.height + margin*2.2, ' ',
                   ha='center', fontsize=15, fontweight='bold', color=entrance_color)
        elif self.entrance_dir == 'East':
            ax.annotate('', xy=(self.width, self.height/2),
                       xytext=(self.width + margin*2.5, self.height/2),
                       arrowprops=dict(arrowstyle='->', color=entrance_color, lw=4))
            ax.text(self.width + margin*3.2, self.height/2, ' ',
                   va='center', fontsize=15, fontweight='bold', color=entrance_color)
        else:
            ax.annotate('', xy=(0, self.height/2),
                       xytext=(-margin*2.5, self.height/2),
                       arrowprops=dict(arrowstyle='->', color=entrance_color, lw=4))
            ax.text(-margin*3.2, self.height/2, ' ',
                   va='center', fontsize=15, fontweight='bold', color=entrance_color)
        
        ax.set_xlim(-margin*3.8, self.width + margin*3.5)
        ax.set_ylim(-margin*2.8, self.height + margin*2.5)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.title(f'Floor Plan \nEntrance: {self.entrance_dir}',
                 fontsize=20, fontweight='bold', pad=25)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return buf
    
    def export_to_dxf(self):
        """Export floor plan to DXF format for AutoCAD"""
        # Create a new DXF document
        doc = ezdxf.new('R2010')  # AutoCAD 2010 format
        msp = doc.modelspace()
        
        # Create layers for different room types
        doc.layers.add('WALLS', color=colors.BLACK)
        doc.layers.add('DOORS', color=colors.RED)
        doc.layers.add('LABELS', color=colors.BLUE)
        doc.layers.add('DIMENSIONS', color=colors.GREEN)
        
        # Draw plot boundary
        msp.add_lwpolyline([
            (0, 0),
            (self.width, 0),
            (self.width, self.height),
            (0, self.height),
            (0, 0)
        ], close=True, dxfattribs={'layer': 'WALLS', 'lineweight': 50})
        
        # Draw all rooms
        for room in self.rooms:
            # Room rectangle
            room_points = [
                (room.x, room.y),
                (room.x + room.width, room.y),
                (room.x + room.width, room.y + room.height),
                (room.x, room.y + room.height),
                (room.x, room.y)
            ]
            msp.add_lwpolyline(room_points, close=True, 
                             dxfattribs={'layer': 'WALLS', 'lineweight': 25})
            
            # Room label
            center_x = room.x + room.width / 2
            center_y = room.y + room.height / 2
            area = room.width * room.height
            
            # Add room name
            msp.add_text(
                room.name,
                dxfattribs={
                    'layer': 'LABELS',
                    'height': min(room.width, room.height) * 0.08,
                    'style': 'Standard'
                }
            ).set_placement(
                (center_x, center_y + 0.3),
                align=TextEntityAlignment.MIDDLE_CENTER
            )
            
            # Add room area
            msp.add_text(
                f"{area:.2f} sq",
                dxfattribs={
                    'layer': 'LABELS',
                    'height': min(room.width, room.height) * 0.05,
                    'style': 'Standard'
                }
            ).set_placement(
                (center_x, center_y - 0.3),
                align=TextEntityAlignment.MIDDLE_CENTER
            )
        
        # Draw doors
        for door in self.doors:
            door_points = [
                (door.x, door.y),
                (door.x + door.width, door.y),
                (door.x + door.width, door.y + door.height),
                (door.x, door.y + door.height),
                (door.x, door.y)
            ]
            msp.add_lwpolyline(door_points, close=True,
                             dxfattribs={'layer': 'DOORS', 'lineweight': 35})
            
            # Draw door swing arc
            if door.orientation == 'horizontal':
                center = (door.x + door.width/2, door.y)
                msp.add_arc(
                    center=center,
                    radius=door.width/2,
                    start_angle=0,
                    end_angle=90,
                    dxfattribs={'layer': 'DOORS'}
                )
            else:
                center = (door.x, door.y + door.height/2)
                msp.add_arc(
                    center=center,
                    radius=door.height/2,
                    start_angle=0,
                    end_angle=90,
                    dxfattribs={'layer': 'DOORS'}
                )
        
        # Add directional labels
        label_offset = 2.0
        
        # North
        msp.add_text(
            'NORTH',
            dxfattribs={'layer': 'DIMENSIONS', 'height': 1.5}
        ).set_placement(
            (self.width/2, self.height + label_offset),
            align=TextEntityAlignment.MIDDLE_CENTER
        )
        
        # South
        msp.add_text(
            'SOUTH',
            dxfattribs={'layer': 'DIMENSIONS', 'height': 1.5}
        ).set_placement(
            (self.width/2, -label_offset),
            align=TextEntityAlignment.MIDDLE_CENTER
        )
        
        # East
        msp.add_text(
            'EAST',
            dxfattribs={'layer': 'DIMENSIONS', 'height': 1.5, 'rotation': 90}
        ).set_placement(
            (self.width + label_offset, self.height/2),
            align=TextEntityAlignment.MIDDLE_CENTER
        )
        
        # West
        msp.add_text(
            'WEST',
            dxfattribs={'layer': 'DIMENSIONS', 'height': 1.5, 'rotation': 90}
        ).set_placement(
            (-label_offset, self.height/2),
            align=TextEntityAlignment.MIDDLE_CENTER
        )
        
        # Add dimension lines
        dim_offset = 1.5
        
        # Width dimension
        msp.add_line(
            (0, -dim_offset), 
            (self.width, -dim_offset),
            dxfattribs={'layer': 'DIMENSIONS'}
        )
        msp.add_text(
            f'Width: {self.width}',
            dxfattribs={'layer': 'DIMENSIONS', 'height': 0.8}
        ).set_placement(
            (self.width/2, -dim_offset - 0.5),
            align=TextEntityAlignment.MIDDLE_CENTER
        )
        
        # Height dimension
        msp.add_line(
            (-dim_offset, 0),
            (-dim_offset, self.height),
            dxfattribs={'layer': 'DIMENSIONS'}
        )
        msp.add_text(
            f'Height: {self.height}',
            dxfattribs={'layer': 'DIMENSIONS', 'height': 0.8, 'rotation': 90}
        ).set_placement(
            (-dim_offset - 0.5, self.height/2),
            align=TextEntityAlignment.MIDDLE_CENTER
        )
        
        # Add entrance indicator
        if self.entrance_dir == 'North':
            msp.add_text(
                '★ ENTRANCE',
                dxfattribs={'layer': 'LABELS', 'height': 1.2, 'color': colors.RED}
            ).set_placement(
                (self.width/2, self.height + label_offset + 2),
                align=TextEntityAlignment.MIDDLE_CENTER
            )
        elif self.entrance_dir == 'East':
            msp.add_text(
                '★ ENTRANCE',
                dxfattribs={'layer': 'LABELS', 'height': 1.2, 'color': colors.RED, 'rotation': 90}
            ).set_placement(
                (self.width + label_offset + 2, self.height/2),
                align=TextEntityAlignment.MIDDLE_CENTER
            )
        else:  # West
            msp.add_text(
                '★ ENTRANCE',
                dxfattribs={'layer': 'LABELS', 'height': 1.2, 'color': colors.RED, 'rotation': 90}
            ).set_placement(
                (-label_offset - 2, self.height/2),
                align=TextEntityAlignment.MIDDLE_CENTER
            )
        
        # Add title block
        msp.add_text(
            f'VASTU FLOOR PLAN - Entrance: {self.entrance_dir}',
            dxfattribs={'layer': 'LABELS', 'height': 2.0}
        ).set_placement(
            (self.width/2, self.height + label_offset + 4),
            align=TextEntityAlignment.MIDDLE_CENTER
        )
        
        # Save to buffer
        # ezdxf requires writing to a file-like object in binary mode
        buf = io.BytesIO()
        
        # Write the DXF document to the buffer
        # Use saveas which properly handles BytesIO
        doc.write(buf)
        
        # Reset buffer position to beginning for reading
        buf.seek(0)
        
        return buf

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        width = float(data.get('width', 30))
        height = float(data.get('height', 30))
        entrance = data.get('entrance', 'random')
        
        if entrance == 'random':
            entrance = random.choice(['North', 'East', 'West'])
        
        generator = FloorPlanGenerator(width, height, entrance)
        generator.generate_layout()
        
        # Store layout data in session for DXF export
        from flask import session
        session['last_layout'] = {
            'width': width,
            'height': height,
            'entrance': entrance,
            'rooms': [(r.x, r.y, r.width, r.height, r.name, r.color) for r in generator.rooms],
            'doors': [(d.x, d.y, d.width, d.height, d.orientation) for d in generator.doors]
        }
        
        img_buffer = generator.draw_to_buffer()
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        total_area = 0
        room_stats = []
        for room in generator.rooms:
            area = room.width * room.height
            total_area += area
            room_stats.append({
                'name': room.name,
                'area': round(area, 2),
                'width': round(room.width, 2),
                'height': round(room.height, 2)
            })
        
        plot_area = width * height
        coverage = (total_area / plot_area) * 100
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}',
            'entrance': entrance,
            'stats': {
                'total_rooms': len(generator.rooms),
                'total_doors': len(generator.doors),
                'total_area': round(total_area, 2),
                'plot_area': round(plot_area, 2),
                'coverage': round(coverage, 2),
                'rooms': room_stats
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/download_dxf', methods=['GET'])
def download_dxf():
    """Download the current floor plan as DXF file"""
    temp_file = None
    try:
        from flask import session
        
        if 'last_layout' not in session:
            return jsonify({
                'success': False,
                'error': 'No floor plan generated yet. Please generate a floor plan first.'
            }), 400
        
        layout_data = session['last_layout']
        
        # Recreate generator with stored data
        generator = FloorPlanGenerator(
            layout_data['width'],
            layout_data['height'],
            layout_data['entrance']
        )
        
        # Restore rooms
        for room_data in layout_data['rooms']:
            x, y, w, h, name, color = room_data
            generator.rooms.append(Room(x, y, w, h, name, color))
        
        # Restore doors
        for door_data in layout_data['doors']:
            x, y, w, h, orientation = door_data
            generator.doors.append(Door(x, y, w, h, orientation))
        
        # Create temporary file for DXF
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'floor_plan_{layout_data["entrance"]}_{timestamp}.dxf'
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w+b', suffix='.dxf', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Export DXF directly to temporary file
        # Create the DXF document
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Create layers
        doc.layers.add('WALLS', color=colors.BLACK)
        doc.layers.add('DOORS', color=colors.RED)
        doc.layers.add('LABELS', color=colors.BLUE)
        doc.layers.add('DIMENSIONS', color=colors.GREEN)
        
        # Draw plot boundary
        msp.add_lwpolyline([
            (0, 0),
            (generator.width, 0),
            (generator.width, generator.height),
            (0, generator.height),
            (0, 0)
        ], close=True, dxfattribs={'layer': 'WALLS', 'lineweight': 50})
        
        # Draw all rooms
        for room in generator.rooms:
            room_points = [
                (room.x, room.y),
                (room.x + room.width, room.y),
                (room.x + room.width, room.y + room.height),
                (room.x, room.y + room.height),
                (room.x, room.y)
            ]
            msp.add_lwpolyline(room_points, close=True, 
                             dxfattribs={'layer': 'WALLS', 'lineweight': 25})
            
            center_x = room.x + room.width / 2
            center_y = room.y + room.height / 2
            area = room.width * room.height
            
            msp.add_text(
                room.name,
                dxfattribs={'layer': 'LABELS', 'height': min(room.width, room.height) * 0.08}
            ).set_placement((center_x, center_y + 0.3), align=TextEntityAlignment.MIDDLE_CENTER)
            
            msp.add_text(
                f"{area:.2f} sq",
                dxfattribs={'layer': 'LABELS', 'height': min(room.width, room.height) * 0.05}
            ).set_placement((center_x, center_y - 0.3), align=TextEntityAlignment.MIDDLE_CENTER)
        
        # Draw doors
        for door in generator.doors:
            door_points = [
                (door.x, door.y),
                (door.x + door.width, door.y),
                (door.x + door.width, door.y + door.height),
                (door.x, door.y + door.height),
                (door.x, door.y)
            ]
            msp.add_lwpolyline(door_points, close=True,
                             dxfattribs={'layer': 'DOORS', 'lineweight': 35})
        
        # Add directional labels
        label_offset = 2.0
        msp.add_text('NORTH', dxfattribs={'layer': 'DIMENSIONS', 'height': 1.5}
            ).set_placement((generator.width/2, generator.height + label_offset), align=TextEntityAlignment.MIDDLE_CENTER)
        msp.add_text('SOUTH', dxfattribs={'layer': 'DIMENSIONS', 'height': 1.5}
            ).set_placement((generator.width/2, -label_offset), align=TextEntityAlignment.MIDDLE_CENTER)
        msp.add_text('EAST', dxfattribs={'layer': 'DIMENSIONS', 'height': 1.5, 'rotation': 90}
            ).set_placement((generator.width + label_offset, generator.height/2), align=TextEntityAlignment.MIDDLE_CENTER)
        msp.add_text('WEST', dxfattribs={'layer': 'DIMENSIONS', 'height': 1.5, 'rotation': 90}
            ).set_placement((-label_offset, generator.height/2), align=TextEntityAlignment.MIDDLE_CENTER)
        
        # Add title
        msp.add_text(
            f'FLOOR PLAN - Entrance: {generator.entrance_dir}',
            dxfattribs={'layer': 'LABELS', 'height': 2.0}
        ).set_placement((generator.width/2, generator.height + label_offset + 4), align=TextEntityAlignment.MIDDLE_CENTER)
        
        # Save to temporary file
        doc.saveas(temp_path)
        
        # Send the file
        return send_file(
            temp_path,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"DXF Export Error: {error_details}")
        
        # Clean up temp file if it exists
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass
        
        return jsonify({
            'success': False,
            'error': f'DXF export failed: {str(e)}'
        }), 400
    finally:
        # Schedule cleanup of temp file after sending
        # Note: In production, you'd want a background task to clean up temp files
        pass

if __name__ == '__main__':
    # Set secret key for session management
    app.secret_key = 'vastu_floor_plan_secret_key_2024'
    app.run(debug=True, host='0.0.0.0', port=5000)