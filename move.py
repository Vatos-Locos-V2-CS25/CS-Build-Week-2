import json
import requests
import time
from queue import SimpleQueue as Q

# set path to follow
start = '0'
end = '467'

# sets vars for making requests
url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv'
headers = {'Authorization': 'Token <your token>',
           'Content-Type': 'application/json'}

# opens map file
with open('map.json') as json_file:
    map = json.load(json_file)


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
                    new_path.append(str(map[last_room][next]))
                    q.put(new_path)


# created a function to get the directions needed to follow an input path
def get_directions(map, path):
    directions = []
    temp_path = []
    for x in path:
        temp_path.append(str(x))
    path = temp_path
    for i in range(len(path)-1):
        dirs = map[path[i]]
        for dir in dirs:
            if str(map[path[i]][dir]) == str((path[i+1])):
                directions.append(dir)
    return(directions)

# gets the path and directions to follow that path
path = find_room(map, start, end)
directions = get_directions(map, path)

# follows the path with the directions
current_room = start
for dir in directions:
    next_room = str(map[current_room][dir])
    data = {'direction': f'{dir}', 'next_room_id': f'{next_room}'}
    resp = requests.post(url + '/move/',
                         data=json.dumps(data),
                         headers=headers
                         )
    temp_content = json.loads(resp.content)
    CD = temp_content['cooldown']
    current_room = str(temp_content['room_id'])
    items = temp_content['items']
    print(f'moved to {current_room}')
    print(f'items {items}')
    time.sleep(CD + .1)