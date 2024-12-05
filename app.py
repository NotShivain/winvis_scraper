from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
@app.route('/team_records', methods=['GET'])
def get_team_records():
    # Fetch and parse team data
    r = requests.get('https://www.formula1.com/en/teams')
    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('div', class_='flex flex-col tablet:grid tablet:grid-cols-12 [&>*]:col-span-12 tablet:[&>*]:col-span-6 gap-xl laptop:[&>*]:col-span-6 desktop:[&>*]:col-span-6')

    imgs = s.find_all('img')
    drivers = s.find_all('p')
    teams = s.find_all('span')

    img_indices = sorted(set(range(1, 40, 4)) | set(range(2, 40, 4)))
    team_imgs = [imgs[i]['src'] for i in range(0, 40, 4)]
    car_imgs = [imgs[i]['src'] for i in range(3, 40, 4)]
    driver_imgs = [imgs[i]['src'] for i in img_indices]

    rank = [drivers[i].text for i in range(0, 70, 7)]
    pts = [drivers[i].text for i in range(1, 70, 7)]
    indices = sorted(set(range(3, 70, 7)) | set(range(5, 70, 7)))
    names = [drivers[i].text + ' ' + drivers[i + 1].text for i in indices]
    constructors = [teams[i].text for i in range(10)]

    # Extract color codes
    res = s.find_all('div')
    all_classes = [div.get('class') for div in res if div.get('class')]
    codes = [cls.split('-')[1] for cls in sum(all_classes, []) if cls.startswith('text')]
    hex_pattern = re.compile(r'^[0-9A-Fa-f]{6}$')
    hex_codes = [code for code in codes if hex_pattern.match(code)]

    # Create team records
    records = []
    for i in range(len(constructors)):
        record = {
            'Pos': rank[i],
            'Pts': pts[i],
            'Drivers': [names[2 * i], names[2 * i + 1]],
            'Team': constructors[i],
            'Driver-img': [driver_imgs[2 * i], driver_imgs[2 * i + 1]],
            'Team-img': team_imgs[i],
            'Car-img': car_imgs[i],
            'Color-code': hex_codes[i]
        }
        records.append(record)

    return jsonify(records)


@app.route('/driver_records', methods=['GET'])
def get_driver_records():
    # Fetch and parse driver data
    req = requests.get('https://www.formula1.com/en/drivers')
    soup = BeautifulSoup(req.content, 'html.parser')
    s2 = soup.find('div', class_=re.compile(r'^flex flex-col tablet:grid tablet:grid-cols-12'))

    info = s2.find_all('p')
    imgs2 = s2.find_all('img')

    pos = [info[i].text for i in range(0, 126, 6)]
    points = [info[i].text for i in range(1, 126, 6)]
    fname = [info[i].text for i in range(3, 126, 6)]
    lname = [info[i].text for i in range(4, 126, 6)]
    team = [info[i].text for i in range(5, 126, 6)]
    flag_img = [imgs2[i]['src'] for i in range(0, 63, 3)]
    no_img = [imgs2[i]['src'] for i in range(1, 63, 3)]
    driver_img = [imgs2[i]['src'] for i in range(2, 63, 3)]

    # Extract color codes
    res2 = s2.find_all('div')
    all_classes2 = [div.get('class') for div in res2 if div.get('class')]
    codes2 = [cls.split('-')[1] for cls in sum(all_classes2, []) if cls.startswith('text')]
    hex_pattern = re.compile(r'^[0-9A-Fa-f]{6}$')
    hex_codes2 = ["#" + code for code in codes2 if hex_pattern.match(code)]
    print("First names:", fname)
    print("Last names:", lname)

    # Create driver records
    driver_records = []
    for i in range(len(pos)):

        # Skip specified drivers
        # if (fname[i] == 'Oliver' and lname[i] == 'Bearman') or \
        #    (fname[i] == 'Jack' and lname[i] == 'Doohan'):
        #     print(f"Skipping driver: {fname[i]} {lname[i]}")
        #     continue
        driver_record = {
            'Pos': pos[i],
            'Pts': points[i],
            'Fname': fname[i],
            'Lname': lname[i],
            'Team': team[i],
            'Flag-img': flag_img[i],
            'No-img': no_img[i],
            'Driver-img': driver_img[i],
            'Color-code': hex_codes2[i]
        }
        driver_records.append(driver_record)
    print(f"Processed {len(driver_records)} driver records")

    return jsonify(driver_records)


if __name__ == '__main__':
    app.run(debug=True)
