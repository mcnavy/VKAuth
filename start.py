from flask import Flask, render_template, request, redirect, session, url_for
import requests
import random

app = Flask(__name__)
app.secret_key = "super secret key"


@app.route('/')
def hello_world():
    if 'friends' in session:
        return redirect(url_for('get_list'))
    return render_template('index.html')


@app.route('/friends')
def get_list():
    if 'access_token' not in session:
        ans = get_token()
        if ans == 'Error':
            return render_template('index.html')

    access_token = session.get('access_token')
    user_id = session.get('user_id')
    domain = "https://api.vk.com/method"
    query_params = {
        'domain': domain,
        'access_token': access_token,
        'user_id': user_id,
        'fields': 'sex'
    }
    query = "{domain}/friends.get?access_token={access_token}&user_id={user_id}&fields={fields}&v=5.53".format(
        **query_params)
    response = requests.get(query)

    friends_all = response.json()['response']['items']

    #session['all'] = friends_all
    friends_number = len(friends_all)
    session['friends_number'] = friends_number

    query_for_name = "https://api.vk.com/method/users.get?access_token={0}&user_id={1}&fields=photo_max_orig&v=5.53".format(
        access_token,
        user_id)
    name_response = requests.get(query_for_name)

    user_name = (name_response.json()['response'][0]['first_name']) + ' ' + (

        name_response.json()['response'][0]['last_name'])
    user_photo = (name_response.json()['response'][0]['photo_max_orig'])

    friends_five = []
    used = []
    for _ in range(5):
        i = random.randint(0, len(friends_all) - 1)

        while i in used or 'deactivated' in friends_all[i]:
            i = random.randint(0, len(friends_all) - 1)
        used.append(i)


        full_name = friends_all[i]['first_name'] + ' ' + friends_all[i]['last_name']
        friend_id = friends_all[i]['id']
        friend_url = 'https://vk.com/id' + str(friend_id)
        friend = {'name': full_name, 'url': friend_url}
        friends_five.append(friend)
    session['friends'] = friends_five
    session['user'] = user_name
    session['photo'] = user_photo

    return redirect(url_for('show'))


def get_token():
    code = request.args.get('code')  # .get('access_token')


    url = "https://oauth.vk.com/access_token?&client_id=7259578&client_secret=emeD74Scic6XXk5Ak6za&code=" + str(
        code) + "&redirect_uri=http://localhost:5000/friends"

    r = requests.get(url)
    if 'error' in r.json():
        print("yes")
        return "Error"
    else:

        access_token = r.json()['access_token']
        # print(r.json())
        user_id = r.json()['user_id']
        session['access_token'] = access_token
        session['user_id'] = user_id
        return "Success"


@app.route('/friends_show')
def show():
    friends_all = session.get('friends')
    friends_number = session.get('friends_number')
    user = session.get('user')
    photo = session.get('photo')


    return render_template('blank.html', value=(friends_all, user, friends_number, photo))

@app.route('/find',methods = ['POST','GET'])
def handle_name():
    projectpath = request.form['projectFilepath']
    access_token = session.get('access_token')
    user_id = session.get('user_id')
    domain = "https://api.vk.com/method"
    query_params = {
        'domain': domain,
        'access_token': access_token,
        'user_id': user_id,
        'fields': projectpath
    }


    query = "{domain}/friends.search?access_token={access_token}&user_id={user_id}&q={fields}&v=5.53".format(
        **query_params)

    response = requests.get(query)

    friends_all = response.json()['response']['items']


    value = []
    for friend in friends_all:
        full_name = friend['first_name']+' '+ friend['last_name']
        friend_url = 'https://vk.com/id' +str(friend['id'])
        value.append({'name':full_name,'url':friend_url})



    return render_template('friends_finder.html',value=value)
@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('hello_world'))


if __name__ == "__main__":
    app.run(debug=True)
