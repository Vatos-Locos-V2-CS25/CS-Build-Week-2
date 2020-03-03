import json
import requests
import time
from queue import SimpleQueue as Q
# defines a function to add blank rooms from a current location
def add_next_rooms(map, current_room, room_info):
    current = current_room
    map[current] = {}
    for next in room_info['exits']:
        map[current][next] = '?'
# a function to find a path from 'start' to 'end'
def find_room(map, start, end):
    q = Q()
    q.put([start])
    visited = set()
    while q.qsize() > 0:
        path = q.get()
        last_room = path[-1]
        if last_room == end:
            return(path)
        if last_room not in visited:
            visited.add(last_room)
            for next in map[last_room]:
                if next == 'info':
                    break
                if map[last_room][next] != '?':
                    new_path = path.copy()
                    new_path.append(map[last_room][next])
                    q.put(new_path)
# created a function to get the directions needed to follow an input path
def get_directions(map, path):
    directions = []
    for i in range(len(path)-1):
        dirs = map[path[i]]
        for dir in dirs:
            if map[path[i]][dir] == path[i+1]:
                directions.append(dir)
    return(directions)
# creates a function to inverse a direction
def inv_dir(dir):
    if dir == 'n':
        return('s')
    if dir == 'e':
        return('w')
    if dir == 's':
        return('n')
    if dir == 'w':
        return('e')
# sets variables for making post requests to the server
url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv'
headers = {'Authorization': 'Token <token>',
           'Content-Type': 'application/json'}
# sets default variables
start_room_info = {
        "room_id": 0,
        "title": "A brightly lit room",
        "description": "You are standing in the center of a brightly lit room. You notice a shop to the west and exits to the north, south and east.",
        "coordinates": "(60,60)",
        "elevation": 0,
        "terrain": "NORMAL",
        "items": [],
        "exits": ["n", "s", "e", "w"],
        "cooldown": 1.0,
        "errors": [],
        "messages": []
}
map = {0: {"n": "?", "s": "?", "e": "?", "w": "?", "info": start_room_info}}
current_room = 0
# a while loop for creating the map
while len(map) < 500:
    # waits for cooldown before starting next loop
    cooldown = map[current_room]['info']['cooldown']
    time.sleep(cooldown + .1)
    # starts looking for a '?'
    searching = 1
    next_direction = None
    while searching == 1:
        for next in map[current_room]['info']['exits']:
            if map[current_room][next] == '?':
                next_direction = next
                searching = 0
                break
        if searching != 0:
            searching = 2
    # look for a room that has a ? if none were found in current room
    if searching == 2:
        # finds the room and sets it to go_to
        go_to = 0
        for room in map:
            for dir in map[room]:
                if map[room][dir] == '?':
                    go_to = room
                    break
        # finds a path to the room
        path = find_room(map, current_room, go_to)
        # finds the directions to follow that path
        dirs = get_directions(map, path)
        # moves the player to the room with a new path
        for dir in dirs:
            data = {'direction': f'{dir}'}
            resp = requests.post(url + '/move/',
                                 data=json.dumps(data),
                                 headers=headers
                                 )
            temp_content = json.loads(resp.content)
            CD = temp_content['cooldown']
            current_room = temp_content['room_id']
            print(f'moved to {current_room}')
            time.sleep(CD + .1)
    else:
        # sets last room to use to update the next room
        last_room = current_room
        # travels the player and updates the current room
        data = {'direction': f'{next_direction}'}
        response = requests.post(url + '/move/',
                                 data=json.dumps(data),
                                 headers=headers
                                 )
        output = json.loads(response.content)
        current_room = output['room_id']
        print(f'moved to {current_room}')
        # adds next rooms exits to the graph
        if current_room not in map:
            add_next_rooms(map, current_room, output)
            map[current_room]['info'] = output
        # updates directions from past and current room
        map[last_room][next_direction] = current_room
        map[current_room][inv_dir(next_direction)] = last_room
        # writes map dict to file for use later
        with open('map.json', 'w') as map_file:
            json.dump(map, map_file)
# writes map dict to file for use later
with open('map.json', 'w') as map_file:
    json.dump(map, map_file)
for room in map:
    print(room)