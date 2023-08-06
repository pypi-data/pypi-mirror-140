# -*- coding: utf-8 -*-
"""
Tool to get any information about iTunes tracks and playlists quickly and easily.
Mickael <mickael2054dev@gmail.com>
MIT License
"""

import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse


def lib_init():
    """Initilize the library, must be called at the very beginning"""
    lib_class = Library()
    return lib_class


class Library(object):
    def __init__(self):
        """Constructor"""
        self.lib = 0
        self.complete_playlist = []
        self.track_attr_list = []
        

    def parse(self, path_to_XML_file):
        """Reads xml file and generate tracks list"""
        tree = ET.parse(path_to_XML_file)
        self.lib = tree.getroot()
        self.read_tracks()
    
            
    def get_playlist_list(self):
        """Creates playlists list"""
        main_dict = self.lib.findall('dict')
        
        sub_array=main_dict[0].findall('array')
        sub_array_childrens = list(sub_array[0])
          
        # For each playlist
        playlist_name_list = []
        for array in sub_array_childrens:
            playlist = list(array)
            
            # Save name of playlists
            for i in range(len(playlist)):
                if playlist[i].text == "Name":
                    playlist_name_list.append(playlist[i+1].text)
                    cur_playlist_name = playlist[i+1].text
                    
                    
                # Get tracks
                if playlist[i].tag == "array":
                    sub_array = list(playlist[i])
                    
                    for k in range(len(sub_array)):
                        track_tags = list(sub_array[k])
                    
                        self.complete_playlist.append([cur_playlist_name, 
                                                       track_tags[1].text])
                        
        return playlist_name_list
    
    
    def get_track_list(self):
        """Returns playlists list"""
        return self.track_attr_list
   
    def read_tracks(self):
        """Generate tracks list"""
        attribut_name_list = ["Track ID", "Size", "Total Time", "Date Modified", 
                      "Date Added", "Bit Rate", "Sample Rate", "Play Count", 
                      "Play Date", "Play Date UTC", "Skip Count", "Skip Date", 
                      "Rating", "Album Rating", "Persistent ID", "Track Type",
                      "File Folder Count", "Library Folder Count", "Name", 
                      "Artist", "Kind", "Location"]
        
        class Track:
          def __init__(self, track_id, size, total_time, date_modified, 
                       date_added, bitrate, sample_rate, play_count, play_date, 
                       play_date_utc, skip_count, skip_date, rating,
                       album_rating, persistent_id, track_type, 
                       file_folder_count, library_folder_count, name, artist, 
                       kind, location):
              
            self.track_id = track_id
            self.size = size
            self.total_time = total_time
            self.date_modified = date_modified
            self.date_added = date_added
            self.bitrate = bitrate
            self.sample_rate = sample_rate
            self.play_count = play_count
            self.play_date = play_date
            self.play_date_utc = play_date_utc
            self.skip_count = skip_count
            self.skip_date = skip_date
            self.rating = rating
            self.album_rating = album_rating
            self.persistent_id = persistent_id
            self.track_type = track_type
            self.file_folder_count = file_folder_count
            self.library_folder_count = library_folder_count
            self.name = name
            self.artist = artist
            self.kind = kind
            self.location = location
        
    
        # Create tracks list with attributes
        main_dict = self.lib.findall('dict')    
        
        sub_array=main_dict[0].findall('dict')
        sub_array_childrens = list(sub_array[0])
              
        for track in sub_array_childrens:
            att_list = [None] * 22
            
            if track.tag == "dict":
                track_attributes = list(track)
                for att_ind in range(0, len(track_attributes), 2):
                    try:
                        tag_index = attribut_name_list.index(
                                track_attributes[att_ind].text)
                    except ValueError:
                        pass
                    else:
                        att_list[tag_index] = track_attributes[att_ind+1].text

                self.track_attr_list.append(Track(att_list[0], att_list[1], 
                                                  att_list[2], att_list[3],
                                                  att_list[4], att_list[5], 
                                                  att_list[6], att_list[7],
                                                  att_list[8], att_list[9], 
                                                  att_list[10], att_list[11],
                                                  att_list[12], att_list[13], 
                                                  att_list[14], att_list[15], 
                                                  att_list[16], att_list[17], 
                                                  att_list[18], att_list[19], 
                                                  att_list[20], att_list[21]))
    
    
    def get_playlist_contents(self, playlist_name):
        """Returns tracks (with attributes) of given playlist"""
        playlist_with_attributes = []
        
        for track in self.complete_playlist:
            if track[0] == playlist_name:
                temp_track_ID = track[1]
                        
                for elem in self.track_attr_list:                    
                    if elem.track_id == temp_track_ID:
                        playlist_with_attributes.append(elem)
                        break
        return playlist_with_attributes
    
    
def get_size(input_size):
    """Returns the size of a track in a human-readable way"""
    return float("{0:.2f}".format(int(input_size)/1E6))
    
    
def get_total_time(input_time):
    """Returns the duration of a track in a human-readable way"""
    return int(int(input_time)/1000)


def get_rating(input_rating):
    """ Returns stars iTunes rating"""
    if input_rating:
        return (int(input_rating)/100)*5
    else:
        return input_rating
    

def get_track_path(input_url):
    """Returns the path of a track"""
    return unquote(urlparse(input_url).path[1:])
