#!/usr/bin/env python3


#sort the movie delete list
def sort_movie_deleteItems_List(item):
    return str(item['Name'])


#sort the episode delete list
def sort_episode_deleteItems_List(item):
    return str(item['SeriesName']) + ' ' + str(item['ParentIndexNumber']).rjust(6,'0') + str(item['IndexNumber']).rjust(6,'0')


#sort the audio delete list
def sort_audio_deleteItems_List(item):
    return str(item['AlbumArtist']) + ' ' + str(item['Album']) + ' ' + str(item['ParentIndexNumber']).rjust(6,'0') + str(item['IndexNumber']).rjust(6,'0')


#sort the audiobook delete list
def sort_audiobook_deleteItems_List(item):
    return sort_audio_deleteItems_List(item)


def sortDeleteLists(deleteItems_dict):
    deleteItems_movie=deleteItems_dict['movie']
    deleteItems_episode=deleteItems_dict['episode']
    deleteItems_audio=deleteItems_dict['audio']
    deleteItems_audiobook=deleteItems_dict['audiobook']

    #sort and combine into single list
    deleteItems=(sorted(deleteItems_movie,key=sort_movie_deleteItems_List) +
                sorted(deleteItems_episode,key=sort_episode_deleteItems_List) +
                sorted(deleteItems_audio,key=sort_audio_deleteItems_List) +
                sorted(deleteItems_audiobook,key=sort_audiobook_deleteItems_List))

    return deleteItems

def sortLibSelection(libList):
    return libList['selection']