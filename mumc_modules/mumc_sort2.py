

#sort the movie delete list
def sort_movie_deleteItems_List2(item):
    return str(item['Name'])


#sort the episode delete list
def sort_episode_deleteItems_List2(item):
    return str(item['SeriesName']) + ' ' + str(item['ParentIndexNumber']).rjust(6,'0') + str(item['IndexNumber']).rjust(6,'0')


#sort the audio delete list
def sort_audio_deleteItems_List2(item):
    return str(item['AlbumArtist']) + ' ' + str(item['Album']) + ' ' + str(item['ParentIndexNumber']).rjust(6,'0') + str(item['IndexNumber']).rjust(6,'0')


#sort the audiobook delete list
def sort_audiobook_deleteItems_List2(item):
    return sort_audio_deleteItems_List2(item)


def sortDeleteLists2(media_type,deleteItems_dict):

    deleteItems_media=deleteItems_dict[media_type]

    #sort and combine into single list
    if (media_type == 'movie'):
        deleteItems=(sorted(deleteItems_media,key=sort_movie_deleteItems_List2))
    elif (media_type == 'episode'):
        deleteItems=(sorted(deleteItems_media,key=sort_episode_deleteItems_List2))
    elif (media_type == 'audio'):
        deleteItems=(sorted(deleteItems_media,key=sort_audio_deleteItems_List2))
    elif (media_type == 'audiobook'):
        deleteItems=(sorted(deleteItems_media,key=sort_audiobook_deleteItems_List2))

    return deleteItems