#
# Copyright (c) 2013 Piston Cloud Computing, Inc. All Rights Reserved.
# Copyright (c) 2014 IBM Corp, Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import flask
from flask import abort, flash, request, redirect, url_for, \
    render_template, g, session, make_response, send_file

from flask_mail import Mail

import json

from refstack import app as base_app
from refstack.extensions import db
from refstack.extensions import oid
from refstack.models import User
from refstack.models import Vendor
from refstack.models import Cloud

from refstack.refstack_config import RefStackConfig
from refstack.tools.tempest_tester import TempestTester

from refstack.models import Cloud


app = base_app.create_app()
mail = Mail(app)


@app.before_request
def before_request():
    """Runs before the request itself."""
    g.user = None
    if 'openid' in session:
        flask.g.user = User.query.filter_by(openid=session['openid']).first()


@app.route('/', methods=['POST', 'GET'])
def index():
    """Index view."""
    vendors = Vendor.query.all()
    clouds = []
    if g.user is not None:
        clouds = Cloud.query.filter_by(user_id=g.user.id).all()
    return render_template('index.html', vendors=vendors, clouds=clouds)


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    """Does the login via OpenID.

    Has to call into `oid.try_login` to start the OpenID machinery.
    """
    # if we are already logged in, go back to were we came from
    if g.user is not None:
        return redirect(oid.get_next_url())
    return oid.try_login(
        "https://login.launchpad.net/",
        ask_for=['email', 'nickname'])


@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session['openid'] = resp.identity_url
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user is not None:
        flash(u'Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())
    return redirect(url_for('create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))


@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    """If this is the user's first login, the create_or_login function
    will redirect here so that the user can set up his profile.
    """
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if not name:
            flash(u'Error: you have to provide a name')
        elif '@' not in email:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            db.session.add(User(name, email, session['openid']))
            db.session.commit()
            return redirect(oid.get_next_url())
    return render_template(
        'create_profile.html', next_url=oid.get_next_url())


@app.route('/delete-cloud/<int:cloud_id>', methods=['GET', 'POST'])
def delete_cloud(cloud_id):
    """Delete function for clouds."""
    c = Cloud.query.filter_by(id=cloud_id).first()

    if not c:
        flash(u'Not a valid Cloud ID!')
    elif not c.user_id == g.user.id:
        flash(u"This isn't your cloud!")
    else:
        db.session.delete(c)
        db.session.commit()

    return redirect('/')


@app.route('/edit-cloud/<int:cloud_id>', methods=['GET', 'POST'])
def edit_cloud(cloud_id):
    c = Cloud.query.filter_by(id=cloud_id).first()

    if not c:
        flash(u'Not a valid Cloud ID!')
        return redirect('/')
    elif not c.user_id == g.user.id:
        flash(u"This isn't your cloud!")

    if request.method == 'POST':
        #validate this biotch
        if not request.form['label']:
            flash(u'Error: All fields are required')
        elif not request.form['endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['test_user']:
            flash(u'Error: All fields are required')
        elif not request.form['test_key']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_user']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_key']:
            flash(u'Error: All fields are required')
        else:
            c.label = request.form['label']
            c.endpoint = request.form['endpoint']
            c.test_user = request.form['test_user']
            c.test_key = request.form['test_key']
            c.admin_endpoint = request.form['admin_endpoint']
            c.admin_user = request.form['admin_user']
            c.admin_key = request.form['admin_key']

            db.session.commit()

            flash(u'Cloud Saved!')
            return redirect('/')

    form = dict(label=c.label,
                endpoint=c.endpoint,
                test_user=c.test_user,
                test_key=c.test_key,
                admin_endpoint=c.admin_endpoint,
                admin_user=c.admin_user,
                admin_key=c.admin_key)

    return render_template('edit_cloud.html', form=form)


@app.route('/create-cloud', methods=['GET', 'POST'])
def create_cloud():
    """This is the handler for creating a new cloud."""

    #if g.user is None:
    #    abort(401)
    if request.method == 'POST':
        if not request.form['label']:
            flash(u'Error: All fields are required')
        elif not request.form['endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['test_user']:
            flash(u'Error: All fields are required')
        elif not request.form['test_key']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_endpoint']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_user']:
            flash(u'Error: All fields are required')
        elif not request.form['admin_key']:
            flash(u'Error: All fields are required')
        else:
            c = Cloud()
            c.user_id = g.user.id
            c.label = request.form['label']
            c.endpoint = request.form['endpoint']
            c.test_user = request.form['test_user']
            c.test_key = request.form['test_key']
            c.admin_endpoint = request.form['admin_endpoint']
            c.admin_user = request.form['admin_user']
            c.admin_key = request.form['admin_key']

            db.session.add(c)
            db.session.commit()
            return redirect('/')

    return render_template('create_cloud.html', next_url='/')


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Updates a profile."""
    if g.user is None:
        abort(401)
    form = dict(name=g.user.name, email=g.user.email)
    if request.method == 'POST':
        if 'delete' in request.form:
            db.session.delete(g.user)
            db.session.commit()
            session['openid'] = None
            flash(u'Profile deleted')
            return redirect(url_for('index'))
        form['name'] = request.form['name']
        form['email'] = request.form['email']
        if not form['name']:
            flash(u'Error: you have to provide a name')
        elif '@' not in form['email']:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            g.user.name = form['name']
            g.user.email = form['email']
            db.session.commit()
            return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
def view_profile():
    """Updates a profile."""
    if g.user is None:
        abort(401)

    return render_template('view_profile.html', user=g.user)


@app.route('/logout')
def logout():
    """Log out."""
    session.pop('openid', None)
    flash(u'You have been signed out')
    return redirect(oid.get_next_url())


@app.route('/test-cloud/<int:cloud_id>', methods=['GET', 'POST'])
def test_cloud(cloud_id):
    c = Cloud.query.filter_by(id=cloud_id).first()

    if not c:
        flash(u'Not a valid Cloud ID!')
        return redirect('/')
    elif not c.user_id == g.user.id:
        flash(u"This isn't your cloud!")

    if request.method == 'POST':
        #validate this biotch
        if not request.form['label']:
            flash(u'Error: All fields are required')
        elif not request.form['pw_user']:
            flash(u'Error: All fields are required')
        # elif not request.form['pw_admin']:
        #    flash(u'Error: All fields are required')
        # elif not request.form['pw_alter_user']:
        #    flash(u'Error: All fields are required')
        else:
            ''' Construct confJSON with the passwords provided '''
            params = {}
            params['identity'] = {}
            params['identity']['password'] = request.form['pw_user']
            params['identity']['admin_password'] = request.form.get('pw_admin', '')
            params['identity']['alt_password'] = request.form.get('pw_alter_user', '')

            TempestTester().test_cloud(cloud_id, json.dumps(params))

            flash(u'Test Started!')
            return redirect('/')
    #TODO(JMC): This should be using a wtforms form instead.
    return render_template('test_cloud.html', next_url='/')


@app.route('/get-script', methods=['GET'])
def send_script():
    """Return a generic python script to be run in the docker container."""

    return send_file('tools/execute_test.py', mimetype='text/plain')


@app.route('/get-miniconf', methods=['GET'])
def send_miniconf():
    """Return a JSON of mini tempest conf to the docker container."""

    test_id = request.args.get('test_id', '')
    response = make_response(TempestTester(test_id).generate_miniconf())
    response.headers["Content-Disposition"] = \
        "attachment; filename=miniconf.json"
    return response


@app.route('/get-testcases', methods=['GET'])
def send_testcases():
    """Return a JSON of tempest test cases to the docker container."""

    test_id = request.args.get('test_id', '')
    response = make_response(TempestTester(test_id).generate_testcases())
    response.headers["Content-Disposition"] = \
        "attachment; filename=testcases.json"
    return response


@app.route('/post-result', methods=['POST'])
def receive_result():
    """Receive tempest test result from the docker container."""

    test_id = request.args.get('test_id', '')
    filename = '%s/test_%s.result' % (RefStackConfig().get_working_dir(),
                                      test_id)
    f = request.files['file']
    if f:
        f.save(filename)
        TempestTester(test_id).process_resultfile(filename)
        ''' TODO: Remove the uploaded file after processing '''
        # os.remove(filename)
    return make_response('')
